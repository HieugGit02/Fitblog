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
    
    Optimization:
    - Use hash maps (dicts) instead of list.index() for O(1) lookup
    - Cache user_index_map and product_index_map
    
    Structure:
        rows: user_ids
        cols: product_ids
        values: ratings (1-5) or 0 (not reviewed)
    """
    
    def __init__(self):
        """Initialize matrix"""
        self.matrix = None
        self.user_ids = None
        self.product_ids = None
        self.user_index_map = {}  # {user_id: index} for O(1) lookup
        self.product_index_map = {}  # {product_id: index} for O(1) lookup
        self.build()
    
    def build(self):
        """Build matrix from database"""
        try:
            # Get all approved reviews from authenticated users
            reviews = ProductReview.objects.filter(
                is_approved=True,
                user__isnull=False
            ).select_related('user', 'product').values(
                'user_id', 'product_id', 'rating'
            )
            
            if not reviews.exists():
                logger.warning("⚠️ No reviews from authenticated users")
                return
            
            # Get unique user_ids and product_ids
            self.user_ids = sorted(set(r['user_id'] for r in reviews))
            self.product_ids = sorted(set(r['product_id'] for r in reviews))
            
            # Build hash maps for O(1) lookup instead of list.index()
            self.user_index_map = {user_id: idx for idx, user_id in enumerate(self.user_ids)}
            self.product_index_map = {product_id: idx for idx, product_id in enumerate(self.product_ids)}
            
            # Initialize matrix with zeros
            self.matrix = np.zeros((len(self.user_ids), len(self.product_ids)))
            
            # Fill ratings
            for review in reviews:
                user_idx = self.user_index_map[review['user_id']]
                product_idx = self.product_index_map[review['product_id']]
                self.matrix[user_idx][product_idx] = review['rating']
            
            logger.info(
                f"✅ Built user-item matrix: "
                f"{len(self.user_ids)} users × {len(self.product_ids)} products"
            )
            
        except Exception as e:
            logger.error(f"❌ Error building matrix: {str(e)}")
    
    def get_user_index(self, user_id):
        """Get user index in matrix - O(1) lookup using hash map"""
        return self.user_index_map.get(user_id)
    
    def get_product_index(self, product_id):
        """Get product index in matrix - O(1) lookup using hash map"""
        return self.product_index_map.get(product_id)
    
    def get_user_vector(self, user_id):
        """Get rating vector of user"""
        idx = self.get_user_index(user_id)
        if idx is not None:
            return self.matrix[idx]
        return None
    
    def get_product_vector(self, product_id):
        """Get rating vector of product"""
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
        Calculate cosine similarity between 2 vectors with min_common_ratings constraint.
        
        Returns similarity score from -1 (opposite) to 1 (identical):
        - 1.0: identical
        - 0.9: very similar
        - 0.5: somewhat related
        - 0.0: no relationship
        
        Optimization:
        - Apply min_common_ratings constraint: if common rated products < threshold, return 0.0
        - Only keep similarity > 0.0
        """
        # Get indices where both users rated (non-zero values)
        mask = (vec1 != 0) & (vec2 != 0)
        common_count = np.sum(mask)
        
        # Apply min_common_ratings threshold
        if common_count < self.min_common_ratings:
            return 0.0
        
        if not np.any(mask):
            return 0.0
        
        v1 = vec1[mask]
        v2 = vec2[mask]
        
        # Normalize ratings from [1-5] to [0-1]
        v1_norm = (v1 - 1) / 4.0
        v2_norm = (v2 - 1) / 4.0
        
        # Calculate cosine similarity
        dot_product = np.dot(v1_norm, v2_norm)
        norm1 = np.linalg.norm(v1_norm)
        norm2 = np.linalg.norm(v2_norm)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        similarity = dot_product / (norm1 * norm2 + 1e-9)
        
        # Only return similarity > 0
        return max(0.0, similarity)
    
    def find_similar_users(self, user_id):
        """
        Find K most similar users to target user.
        
        Returns:
            List of (similar_user_id, similarity_score) with similarity > 0,
            sorted by similarity descending, max k_neighbors items.
            
        Optimization:
        - Filter out similarity <= 0 to avoid wasting computation
        - Only return top k_neighbors with positive similarity
        """
        user_idx = self.matrix.get_user_index(user_id)
        if user_idx is None:
            logger.debug(f"User {user_id} not in matrix")
            return []
        
        user_vector = self.matrix.get_user_vector(user_id)
        similarities = []
        
        for other_idx, other_user_id in enumerate(self.matrix.user_ids):
            if other_user_id == user_id:
                continue
            
            other_vector = self.matrix.matrix[other_idx]
            similarity = self.cosine_similarity(user_vector, other_vector)
            
            # Only keep positive similarities
            if similarity > 0.0:
                similarities.append((other_user_id, similarity))
        
        # Sort by similarity descending and return top k_neighbors
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:self.k_neighbors]
    
    def predict_rating(self, user_id, product_id, similar_users_with_scores):
        """
        Predict rating for user on product using weighted average from similar users.
        
        Args:
            user_id: Target user ID
            product_id: Target product ID
            similar_users_with_scores: Pre-fetched list of (user_id, similarity_score)
        
        Returns:
            Predicted rating (1.0-5.0) or None if no similar users rated this product
            
        Optimization:
        - Accept pre-fetched similar_users to avoid redundant similarity calculations
        - Use pre-fetched ratings dict to avoid N+1 queries
        """
        if not similar_users_with_scores:
            return None
        
        weighted_sum = 0.0
        similarity_sum = 0.0
        
        for similar_user_id, similarity_score in similar_users_with_scores:
            # Look up in pre-fetched data (will be populated by recommend())
            rating = self._get_cached_rating(similar_user_id, product_id)
            
            if rating:
                weighted_sum += rating * similarity_score
                similarity_sum += similarity_score
        
        if similarity_sum == 0.0:
            return None
        
        predicted_rating = weighted_sum / similarity_sum
        return min(5.0, max(1.0, predicted_rating))  # Clamp to [1-5]
    
    def _get_cached_rating(self, user_id, product_id):
        """
        Get rating from cached data.
        This will be populated by recommend() before calling predict_rating.
        """
        if not hasattr(self, '_rating_cache'):
            self._rating_cache = {}
        
        key = (user_id, product_id)
        return self._rating_cache.get(key)
    
    def _get_cold_start_recommendations(self, n_recommendations=5):
        """
        Fallback recommendations for cold-start users (no similar users found).
        
        Strategy:
        1. Top-rated products (by average rating)
        2. Best sellers (by review count)
        
        Returns:
            List of dicts with product info
        """
        logger.info("❄️ Applying cold-start fallback: top-rated products")
        
        try:
            # Get top-rated products with sufficient reviews
            top_products = Product.objects.filter(
                status='active'
            ).annotate(
                avg_rating=Avg('reviews__rating'),
                review_count=Count('reviews')
            ).filter(
                review_count__gte=2  # At least 2 reviews to be reliable
            ).select_related('category').order_by(
                '-avg_rating', '-review_count'
            )[:n_recommendations]
            
            result = []
            for product in top_products:
                result.append({
                    'product_id': product.id,
                    'product_name': product.name,
                    'product_slug': product.slug,
                    'product_price': float(product.price),
                    'product_image': product.image.url if product.image else '/static/placeholder.jpg',
                    'product_category': product.category.name if product.category else 'N/A',
                    'predicted_rating': round(product.avg_rating or 3.0, 2)
                })
            
            return result
        except Exception as e:
            logger.error(f"❌ Cold-start fallback error: {str(e)}")
            return []

    def recommend(self, user_id, n_recommendations=5, min_predicted_rating=3.5):
        """
        Recommend N products for user using collaborative filtering.
        
        Args:
            user_id: Target user ID
            n_recommendations: Number of products to recommend
            min_predicted_rating: Minimum predicted rating threshold (1-5)
        
        Returns:
            List of dicts with product info:
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
        
        Optimizations:
        1. Find similar users once
        2. Fetch all similar users' ratings in bulk (avoid N+1 query)
        3. Only predict for products rated by at least one similar user
        4. Cold-start fallback if no similar users found
        """
        try:
            # Step 1: Find similar users
            similar_users = self.find_similar_users(user_id)
            
            # Cold-start handling: no similar users found
            if not similar_users:
                logger.warning(f"⚠️ No similar users found for user {user_id}, using cold-start fallback")
                return self._get_cold_start_recommendations(n_recommendations)
            
            # Step 2: Get products already reviewed by target user
            reviewed_products = set(
                ProductReview.objects.filter(
                    user_id=user_id
                ).values_list('product_id', flat=True)
            )
            
            # Step 3: Bulk fetch all ratings from similar users
            # This avoids N+1 query problem in predict_rating()
            similar_user_ids = [uid for uid, _ in similar_users]
            
            similar_reviews = ProductReview.objects.filter(
                user_id__in=similar_user_ids,
                is_approved=True
            ).select_related('product').values(
                'user_id', 'product_id', 'rating'
            )
            
            # Build rating cache: {(user_id, product_id): rating}
            self._rating_cache = {
                (r['user_id'], r['product_id']): r['rating']
                for r in similar_reviews
            }
            
            # Get products rated by similar users (candidates for recommendation)
            products_rated_by_similar = set(
                r['product_id'] for r in similar_reviews
            )
            
            # Step 4: Get unevaluated products
            # Only consider products rated by similar users (avoid unnecessary predictions)
            unevaluated_products = products_rated_by_similar - reviewed_products
            
            if not unevaluated_products:
                logger.warning(f"⚠️ No unevaluated products for user {user_id}")
                return []
            
            # Step 5: Predict ratings and collect predictions
            predictions = []
            for product_id in unevaluated_products:
                predicted_rating = self.predict_rating(
                    user_id, 
                    product_id, 
                    similar_users
                )
                
                if predicted_rating and predicted_rating >= min_predicted_rating:
                    predictions.append((product_id, predicted_rating))
            
            if not predictions:
                logger.warning(f"⚠️ No predictions above threshold for user {user_id}")
                return self._get_cold_start_recommendations(n_recommendations)
            
            # Step 6: Sort by predicted rating
            predictions.sort(key=lambda x: x[1], reverse=True)
            
            # Step 7: Fetch product details and format response
            result = []
            product_ids = [pid for pid, _ in predictions[:n_recommendations]]
            
            # Bulk fetch products
            products_map = {
                p.id: p
                for p in Product.objects.filter(
                    id__in=product_ids
                ).select_related('category')
            }
            
            for product_id, predicted_rating in predictions[:n_recommendations]:
                if product_id not in products_map:
                    logger.warning(f"⚠️ Product {product_id} not found (may have been deleted)")
                    continue
                
                product = products_map[product_id]
                result.append({
                    'product_id': product.id,
                    'product_name': product.name,
                    'product_slug': product.slug,
                    'product_price': float(product.price),
                    'product_image': product.image.url if product.image else '/static/placeholder.jpg',
                    'product_category': product.category.name if product.category else 'N/A',
                    'predicted_rating': round(predicted_rating, 2)
                })
            
            return result
        
        except Exception as e:
            logger.error(f"❌ Recommendation error for user {user_id}: {str(e)}")
            return []


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
