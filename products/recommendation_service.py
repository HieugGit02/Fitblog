# -*- coding: utf-8 -*-
"""
Collaborative Filtering Recommendation Service

Implements user-based collaborative filtering để gợi ý sản phẩm dựa trên
user behavior của những users tương tự.

Cấu trúc:
1. UserSimilarityMatrix: Tính độ tương đồng giữa các users
2. CollaborativeFilteringEngine: Engine để predict ratings & recommend products
3. HybridRecommendationEngine: Kết hợp collab + content-based + personalized
"""

from django.db.models import Q, Avg, Count
from django.core.cache import cache
import numpy as np
from .models import Product, ProductReview, UserProfile
import logging

logger = logging.getLogger(__name__)


class UserItemMatrix:
    """
    Tạo & quản lý user-item matrix từ reviews
    
    Dạng:
        rows: user_ids
        cols: product_ids
        values: ratings (1-5) hoặc 0 (chưa review)
    """
    
    def __init__(self):
        """Initialize matrix"""
        self.matrix = None
        self.user_ids = None
        self.product_ids = None
        self.build()
    
    def build(self):
        """Xây dựng matrix từ database"""
        try:
            # Lấy tất cả approved reviews từ authenticated users
            reviews = ProductReview.objects.filter(
                is_approved=True,
                user__isnull=False
            ).select_related('user', 'product').values(
                'user_id', 'product_id', 'rating'
            )
            
            if not reviews.exists():
                logger.warning("⚠️ Không có reviews nào từ authenticated users")
                return
            
            # Lấy unique user_ids & product_ids
            self.user_ids = sorted(set(r['user_id'] for r in reviews))
            self.product_ids = sorted(set(r['product_id'] for r in reviews))
            
            # Khởi tạo matrix với 0s
            self.matrix = np.zeros((len(self.user_ids), len(self.product_ids)))
            
            # Fill trong ratings
            for review in reviews:
                user_idx = self.user_ids.index(review['user_id'])
                product_idx = self.product_ids.index(review['product_id'])
                self.matrix[user_idx][product_idx] = review['rating']
            
            logger.info(
                f"✅ Built user-item matrix: "
                f"{len(self.user_ids)} users × {len(self.product_ids)} products"
            )
            
        except Exception as e:
            logger.error(f"❌ Error building matrix: {str(e)}")
    
    def get_user_index(self, user_id):
        """Lấy index của user trong matrix"""
        if user_id in self.user_ids:
            return self.user_ids.index(user_id)
        return None
    
    def get_product_index(self, product_id):
        """Lấy index của product trong matrix"""
        if product_id in self.product_ids:
            return self.product_ids.index(product_id)
        return None
    
    def get_user_vector(self, user_id):
        """Lấy rating vector của user"""
        idx = self.get_user_index(user_id)
        if idx is not None:
            return self.matrix[idx]
        return None
    
    def get_product_vector(self, product_id):
        """Lấy rating vector của product"""
        idx = self.get_product_index(product_id)
        if idx is not None:
            return self.matrix[:, idx]
        return None


class CollaborativeFilteringEngine:
    """
    User-based Collaborative Filtering Engine
    
    Algorithm:
    1. Tìm K users tương tự nhất (dựa vào rating patterns)
    2. Xem những sản phẩm mà similar users đã rate cao
    3. Predict rating của target user cho những products đó
    4. Recommend top N products
    """
    
    def __init__(self, k_neighbors=5, min_common_ratings=2):
        """
        Args:
            k_neighbors: Số users tương tự cần xem xét
            min_common_ratings: Tối thiểu số products mà 2 users cùng rate
        """
        self.k_neighbors = k_neighbors
        self.min_common_ratings = min_common_ratings
        self.matrix = UserItemMatrix()
        self.similarity_cache = {}
    
    def cosine_similarity(self, vec1, vec2):
        """
        Tính cosine similarity giữa 2 vectors
        
        Score từ -1 (đối lập) tới 1 (giống hệt)
        - 1.0: hoàn toàn giống nhau
        - 0.9: rất giống
        - 0.5: có chút liên hệ
        - 0.0: không liên hệ
        """
        # Remove zero ratings (chưa rate)
        mask = (vec1 != 0) & (vec2 != 0)
        if not np.any(mask):
            return 0.0
        
        v1 = vec1[mask]
        v2 = vec2[mask]
        
        # Normalize vào [0,1] range
        v1_norm = (v1 - 1) / 4  # Ratings 1-5 → 0-1
        v2_norm = (v2 - 1) / 4
        
        dot_product = np.dot(v1_norm, v2_norm)
        norm1 = np.linalg.norm(v1_norm)
        norm2 = np.linalg.norm(v2_norm)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2 + 1e-9)
    
    def find_similar_users(self, user_id):
        """
        Tìm K users tương tự nhất với target user
        
        Returns:
            List of (similar_user_id, similarity_score)
        """
        user_idx = self.matrix.get_user_index(user_id)
        if user_idx is None:
            return []
        
        user_vector = self.matrix.get_user_vector(user_id)
        similarities = []
        
        for other_idx, other_user_id in enumerate(self.matrix.user_ids):
            if other_user_id == user_id:
                continue
            
            other_vector = self.matrix.matrix[other_idx]
            similarity = self.cosine_similarity(user_vector, other_vector)
            similarities.append((other_user_id, similarity))
        
        # Sort và lấy top K
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:self.k_neighbors]
    
    def predict_rating(self, user_id, product_id):
        """
        Predict rating của user cho product
        
        Dùng weighted average của ratings từ similar users
        """
        similar_users = self.find_similar_users(user_id)
        if not similar_users:
            return None
        
        # Lấy ratings của similar users cho product này
        weighted_sum = 0
        similarity_sum = 0
        
        for similar_user_id, similarity_score in similar_users:
            # Lấy rating của similar user cho product
            rating = ProductReview.objects.filter(
                user_id=similar_user_id,
                product_id=product_id,
                is_approved=True
            ).values_list('rating', flat=True).first()
            
            if rating:
                weighted_sum += rating * similarity_score
                similarity_sum += similarity_score
        
        if similarity_sum == 0:
            return None
        
        predicted_rating = weighted_sum / similarity_sum
        return min(5.0, max(1.0, predicted_rating))  # Clamp 1-5
    
    def recommend(self, user_id, n_recommendations=5, min_predicted_rating=3.5):
        """
        Gợi ý N sản phẩm cho user
        
        Args:
            user_id: ID của target user
            n_recommendations: Số sản phẩm cần gợi ý
            min_predicted_rating: Tối thiểu predicted rating (1-5)
        
        Returns:
            List of dict with full product info:
            [
                {
                    'product_id': 1,
                    'product_name': 'Whey Protein',
                    'product_slug': 'whey-protein',
                    'product_price': 500000,
                    'product_image': '/media/...',
                    'product_category': 'Protein',
                    'predicted_rating': 4.5
                },
                ...
            ]
        """
        similar_users = self.find_similar_users(user_id)
        if not similar_users:
            logger.warning(f"⚠️ Không tìm thấy similar users cho user {user_id}")
            return []
        
        # Lấy products mà target user chưa review
        reviewed_products = set(
            ProductReview.objects.filter(
                user_id=user_id
            ).values_list('product_id', flat=True)
        )
        
        unevaluated_products = set(
            Product.objects.filter(
                status='active'
            ).values_list('id', flat=True)
        ) - reviewed_products
        
        # Predict ratings & recommend
        predictions = []
        for product_id in unevaluated_products:
            predicted_rating = self.predict_rating(user_id, product_id)
            
            if predicted_rating and predicted_rating >= min_predicted_rating:
                predictions.append((product_id, predicted_rating))
        
        # Sort by predicted rating
        predictions.sort(key=lambda x: x[1], reverse=True)
        
        # Lấy product info và format return
        result = []
        for product_id, predicted_rating in predictions[:n_recommendations]:
            try:
                product = Product.objects.select_related('category').get(id=product_id)
                result.append({
                    'product_id': product.id,
                    'product_name': product.name,
                    'product_slug': product.slug,
                    'product_price': float(product.price),
                    'product_image': product.image.url if product.image else '/static/placeholder.jpg',
                    'product_category': product.category.name if product.category else 'N/A',
                    'predicted_rating': round(predicted_rating, 2)
                })
            except Product.DoesNotExist:
                logger.error(f"⚠️ Product {product_id} not found")
                continue
        
        return result


class HybridRecommendationEngine:
    """
    Kết hợp 3 recommendation algorithms:
    1. Collaborative Filtering (40%)
    2. Content-based (30%)
    3. Personalized (30%)
    
    Mục đích: Tận dụng ưu điểm của cả 3, tránh nhược điểm từng cái
    
    STATUS: Content-based & Personalized methods chưa implement
    Hiện tại chỉ dùng Collaborative Filtering (100%)
    """
    
    def __init__(self):
        """Initialize"""
        self.collab_engine = CollaborativeFilteringEngine()
    
    # ===== COMMENTED: Content-based & Personalized methods (TODO) =====
    # def _get_content_based_recommendations(self, user_id, n=10):
    #     """
    #     Gợi ý dựa trên nội dung (category, supplement type, goals)
    #     TODO: Implement this
    #     """
    #     return []
    
    # def _get_personalized_recommendations(self, user_id, n=10):
    #     """
    #     Gợi ý dựa trên user goal
    #     TODO: Implement this
    #     """
    #     return []
    
    # ===== COMMENTED: Normalize scores (chỉ cần khi dùng Hybrid) =====
    # def _normalize_scores(self, items):
    #     """
    #     items: [(product_id, score), ...] hoặc [dict with product info]
    #     normalize về [0..1] theo max-score
    #     """
    #     if not items:
    #         return {}
    # 
    #     # Handle different input formats
    #     if isinstance(items[0], dict):
    #         # Extract product_id and use predicted_rating as score
    #         scores = {item['product_id']: item['predicted_rating'] for item in items}
    #     else:
    #         # Assume tuple format (product_id, score)
    #         scores = {pid: score for pid, score in items}
    #     
    #     if not scores:
    #         return {}
    # 
    #     max_score = max(scores.values())
    #     if max_score == 0:
    #         max_score = 1.0
    # 
    #     return {pid: score / max_score for pid, score in scores.items()}
    
    # def recommend(self, user_id, n_recommendations=5):
    #     """
    #     Hybrid recommendation
        
    #     Kết hợp 3 algorithms với weights khác nhau
    #     """
    #     try:
    #         # 1. Collaborative Filtering (40%)
    #         collab_items = self.collab_engine.recommend(user_id, n=15)
    #         collab_products = {product_id: score for product_id, score in collab_items}
            
    #         # 2. Content-based (30%)
    #         content_items = self._get_content_based_recommendations(user_id, n=15)
    #         content_products = {product_id: score for product_id, score in content_items}
            
    #         # 3. Personalized (30%)
    #         personal_items = self._get_personalized_recommendations(user_id, n=15)
    #         personal_products = {product_id: score for product_id, score in personal_items}
            
    #         # Combine scores
    #         all_products = set()
    #         all_products.update(collab_products.keys())
    #         all_products.update(content_products.keys())
    #         all_products.update(personal_products.keys())
            
    #         hybrid_scores = {}
    #         for product_id in all_products:
    #             score = 0
    #             if product_id in collab_products:
    #                 score += 0.40 * (collab_products[product_id] / 5.0)  # Normalize
    #             if product_id in content_products:
    #                 score += 0.30 * content_products[product_id]
    #             if product_id in personal_products:
    #                 score += 0.30 * personal_products[product_id]
                
    #             hybrid_scores[product_id] = score
            
    #         # Sort & return top N
    #         ranked = sorted(
    #             hybrid_scores.items(),
    #             key=lambda x: x[1],
    #             reverse=True
    #         )[:n_recommendations]
            
    #         return ranked
            
    #     except Exception as e:
    #         logger.error(f"❌ Hybrid recommendation error: {str(e)}")
    #         return []
    # ===== COMMENTED: Hybrid recommend (chỉ dùng CollaborativeFilteringEngine) =====
    # def recommend(self, user_id, n_recommendations=5):
    #     """
    #     Hybrid recommendation:
    #     - Collaborative Filtering (40%)
    #     - Content-based (30%)
    #     - Personalized (30%)
    #     
    #     Returns:
    #         List of dicts with product info sorted by hybrid score
    #     """
    #     try:
    #         # 1) Get candidates from each source
    #         collab_items = self.collab_engine.recommend(user_id, n=10) or []
    #         content_items = self._get_content_based_recommendations(user_id, n=10) or []
    #         personal_items = self._get_personalized_recommendations(user_id, n=10) or []
    # 
    #         # 2) Normalize each source to same scale [0..1]
    #         collab_scores = self._normalize_scores(collab_items)
    #         content_scores = self._normalize_scores(content_items)
    #         personal_scores = self._normalize_scores(personal_items)
    # 
    #         # 3) Merge all candidates (get unique product IDs)
    #         all_product_ids = set(collab_scores.keys()) | set(content_scores.keys()) | set(personal_scores.keys())
    # 
    #         # 4) Calculate hybrid scores
    #         hybrid_scores = {}
    #         for product_id in all_product_ids:
    #             score = (
    #                 0.40 * collab_scores.get(product_id, 0.0)
    #                 + 0.30 * content_scores.get(product_id, 0.0)
    #                 + 0.30 * personal_scores.get(product_id, 0.0)
    #             )
    #             hybrid_scores[product_id] = score
    # 
    #         # 5) Rank & return top N
    #         ranked_ids = sorted(hybrid_scores.items(), key=lambda x: x[1], reverse=True)[:n_recommendations]
    #         
    #         # 6) Fetch full product info for top ranked items
    #         result = []
    #         product_map = {item['product_id']: item for item in collab_items}
    #         
    #         for product_id, hybrid_score in ranked_ids:
    #             if product_id in product_map:
    #                 item = product_map[product_id].copy()
    #                 item['hybrid_score'] = round(hybrid_score, 3)
    #                 result.append(item)
    #         
    #         return result
    # 
    #     except Exception as e:
    #         logger.error(f"❌ Hybrid recommendation error: {str(e)}")
    #         return []

# Global instances (cache)
_collab_engine = None

def get_collaborative_engine():
    """Get hoặc create singleton collaborative filtering engine"""
    global _collab_engine
    if _collab_engine is None:
        _collab_engine = CollaborativeFilteringEngine()
    return _collab_engine

def collab_recommend(user_id, n=5):
    """
    Quick function để lấy collaborative filtering recommendations
    
    Usage:
        from products.recommendation_service import collab_recommend
        recommendations = collab_recommend(user_id=5, n=10)
    """
    engine = get_collaborative_engine()
    return engine.recommend(user_id, n_recommendations=n)
