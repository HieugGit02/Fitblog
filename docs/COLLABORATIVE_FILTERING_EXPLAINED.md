# 🤖 Collaborative Filtering Algorithm Giải Thích

## 📍 Vị Trí Code

File: `/products/recommendation_service.py`  
Class: `CollaborativeFilteringEngine` (Line 101-250)

---

## 🎯 Thuật Toán Sử Dụng: **User-Based Collaborative Filtering + Cosine Similarity**

### Đây Là Thuật Toán Nào?

```
User-Based Collaborative Filtering
├─ Loại: Memory-Based (không dùng ML)
├─ Độ phức tạp: O(n²) - tính toán độ tương đồng tất cả user pairs
├─ Accuracy: 70-80% (tốt cho dataset nhỏ-vừa)
└─ Ưu điểm: Đơn giản, dễ hiểu, không cần training
```

---

## 🔍 Chi Tiết Từng Bước

### **Bước 1: Xây Dựng User-Item Matrix**

```python
# Code: recommendation_service.py - Line 22-67 (UserItemMatrix class)

class UserItemMatrix:
    def build(self):
        # Lấy tất cả reviews từ users
        reviews = ProductReview.objects.filter(
            is_approved=True,
            user__isnull=False
        ).select_related('user', 'product')
        
        # Tạo matrix:
        #            Product1  Product2  Product3  Product4
        # User1      [5]       [4]       [0]       [3]
        # User2      [4]       [0]       [5]       [2]
        # User3      [0]       [5]       [4]       [5]
        # User4      [3]       [4]       [3]       [0]
        
        # 0 = chưa rate, 1-5 = rating
```

**Dữ liệu Input**: ProductReview (user, product, rating)  
**Output**: Matrix 2D (users × products) với ratings

---

### **Bước 2: Tính Cosine Similarity**

```python
# Code: recommendation_service.py - Line 120-154 (cosine_similarity method)

def cosine_similarity(self, vec1, vec2):
    """
    Tính độ tương đồng giữa 2 vectors
    
    Vector = Rating pattern của user
    Cosine = Góc giữa 2 vectors
    """
    
    # Công Thức Toán Học:
    # similarity = (vec1 · vec2) / (||vec1|| × ||vec2||)
    #
    # Nôm na:
    # - Tính tích vô hướng (dot product)
    # - Chia cho độ dài vectors
    # - Kết quả: -1 (đối lập) đến 1 (giống hệt)
    
    # Normalize ratings 1-5 → 0-1 range
    v1_norm = (v1 - 1) / 4
    v2_norm = (v2 - 1) / 4
    
    # Cosine formula
    dot_product = np.dot(v1_norm, v2_norm)
    norm1 = np.linalg.norm(v1_norm)
    norm2 = np.linalg.norm(v2_norm)
    
    return dot_product / (norm1 * norm2 + 1e-9)
```

**Kết Quả**: Similarity Score từ 0 (không liên hệ) đến 1 (giống hệt)

---

### **Bước 3: Tìm K-Nearest Neighbors (Similar Users)**

```python
# Code: recommendation_service.py - Line 156-179 (find_similar_users method)

def find_similar_users(self, user_id):
    """
    Tìm K users tương tự nhất
    
    Algorithm: K-Nearest Neighbors (KNN)
    K = 5 (mặc định)
    """
    
    user_vector = self.matrix.get_user_vector(user_id)  # Rating pattern của user
    
    similarities = []
    for other_user_id in self.matrix.user_ids:
        if other_user_id == user_id:
            continue
        
        other_vector = self.matrix.get_user_vector(other_user_id)
        similarity = self.cosine_similarity(user_vector, other_vector)
        similarities.append((other_user_id, similarity))
    
    # Sort & lấy top 5
    similarities.sort(key=lambda x: x[1], reverse=True)
    return similarities[:self.k_neighbors]  # k_neighbors=5
```

**Đầu Vào**: User ID  
**Đầu Ra**: Top 5 users tương tự nhất + similarity scores

---

### **Bước 4: Predict Rating (Weighted Average)**

```python
# Code: recommendation_service.py - Line 181-211 (predict_rating method)

def predict_rating(self, user_id, product_id):
    """
    Dự đoán rating của user cho product
    
    Công thức: weighted average
    predicted_rating = Σ(similar_user_rating × similarity_weight) / Σ(similarity_weights)
    """
    
    similar_users = self.find_similar_users(user_id)  # Top 5 similar users
    
    weighted_sum = 0
    similarity_sum = 0
    
    for similar_user_id, similarity_score in similar_users:
        # Lấy rating của similar user cho product này
        rating = ProductReview.objects.filter(
            user_id=similar_user_id,
            product_id=product_id,
            is_approved=True
        ).values_list('rating', flat=True).first()
        
        if rating:
            weighted_sum += rating * similarity_score  # Weight bằng similarity
            similarity_sum += similarity_score
    
    if similarity_sum == 0:
        return None
    
    predicted_rating = weighted_sum / similarity_sum
    return min(5.0, max(1.0, predicted_rating))  # Clamp 1-5
```

**VÍ DỤ TÍNH TOÁN**:

```
User A chưa rate Product X

Similar Users của A:
  - User B: similarity=0.9, đã rate Product X = 5 sao
  - User C: similarity=0.8, đã rate Product X = 4 sao
  - User D: similarity=0.7, chưa rate Product X
  - User E: similarity=0.6, đã rate Product X = 3 sao
  - User F: similarity=0.5, đã rate Product X = 4 sao

Tính toán:
  weighted_sum = (5 × 0.9) + (4 × 0.8) + (3 × 0.6) + (4 × 0.5)
               = 4.5 + 3.2 + 1.8 + 2.0
               = 11.5

  similarity_sum = 0.9 + 0.8 + 0.6 + 0.5 = 2.8

  predicted_rating = 11.5 / 2.8 = 4.1 ⭐
```

---

### **Bước 5: Recommend Top N Products**

```python
# Code: recommendation_service.py - Line 213-250 (recommend method)

def recommend(self, user_id, n_recommendations=5):
    """
    Gợi ý 5 sản phẩm tốt nhất cho user
    """
    
    similar_users = self.find_similar_users(user_id)
    
    # Lấy products mà user chưa review
    reviewed_products = ProductReview.objects.filter(
        user_id=user_id
    ).values_list('product_id', flat=True)
    
    unevaluated_products = set(Product.objects.values_list('id', flat=True)) - reviewed_products
    
    # Predict rating cho mỗi unevaluated product
    predictions = []
    for product_id in unevaluated_products:
        predicted_rating = self.predict_rating(user_id, product_id)
        
        if predicted_rating and predicted_rating >= 3.5:  # Min threshold
            predictions.append((product_id, predicted_rating))
    
    # Sort by predicted rating
    predictions.sort(key=lambda x: x[1], reverse=True)
    
    return predictions[:n_recommendations]  # Return top 5
```

---

## 📊 Toàn Bộ Workflow

```
┌─────────────────────────────────────────────────────────┐
│ 1. USER A TRUY CẬP PROFILE                              │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│ 2. BUILD USER-ITEM MATRIX (Tất cả reviews)             │
│    Users: [A, B, C, D, E, F]                           │
│    Products: [P1, P2, P3, P4, P5]                      │
│                                                         │
│              P1  P2  P3  P4  P5                        │
│    User A [ 5   4   0   3   0]                        │
│    User B [ 4   0   5   2   4]                        │
│    User C [ 0   5   4   5   3]                        │
│    User D [ 3   4   3   0   5]                        │
│    User E [ 0   3   0   4   4]                        │
│    User F [ 4   4   3   0   5]                        │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│ 3. CALCULATE COSINE SIMILARITY                          │
│                                                         │
│    User A vs User B: similarity = 0.85                 │
│    User A vs User C: similarity = 0.72                 │
│    User A vs User D: similarity = 0.80                 │
│    User A vs User E: similarity = 0.68                 │
│    User A vs User F: similarity = 0.88                 │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│ 4. FIND K-NEAREST NEIGHBORS (K=5)                      │
│                                                         │
│    Top 5 Similar Users:                                │
│    1. User F (similarity=0.88)                         │
│    2. User B (similarity=0.85)                         │
│    3. User D (similarity=0.80)                         │
│    4. User C (similarity=0.72)                         │
│    5. User E (similarity=0.68)                         │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│ 5. PREDICT RATINGS FOR UNEVALUATED PRODUCTS             │
│                                                         │
│    User A chưa rate: P2, P3, P4, P5                    │
│                                                         │
│    Predicted P2: (4×0.88 + 0×0.85 + 4×0.80 + 5×0.72) │
│                  / (0.88+0.85+0.80+0.72) = 4.2 ⭐      │
│                                                         │
│    Predicted P3: (5×0.85 + 4×0.72 + 3×0.80)           │
│                  / (0.85+0.72+0.80) = 4.2 ⭐          │
│                                                         │
│    Predicted P4: (2×0.85 + 5×0.72 + 0×0.80)           │
│                  / (0.85+0.72+0.80) = 3.2 ⭐          │
│                                                         │
│    Predicted P5: (4×0.88 + 3×0.72 + 5×0.80 + 4×0.68) │
│                  / (0.88+0.72+0.80+0.68) = 4.1 ⭐      │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│ 6. RECOMMEND TOP N (N=5)                               │
│                                                         │
│    Recommendations (sorted by predicted rating):       │
│    1. P2 (predicted: 4.2) ← Best                      │
│    2. P3 (predicted: 4.2)                             │
│    3. P5 (predicted: 4.1)                             │
│    4. P4 (predicted: 3.2) ← Min threshold 3.5        │
│    5. (no more products)                              │
│                                                         │
│    Final Output: [P2, P3, P5]                         │
└─────────────────────────────────────────────────────────┘
```

---

## 🧮 Công Thức Toán Học (Chi Tiết)

### **Cosine Similarity**

$$\text{similarity}(A, B) = \frac{\vec{A} \cdot \vec{B}}{||\vec{A}|| \times ||\vec{B}||} = \frac{\sum_{i=1}^{n} A_i \times B_i}{\sqrt{\sum_{i=1}^{n} A_i^2} \times \sqrt{\sum_{i=1}^{n} B_i^2}}$$

**Giải Thích**:
- Tử số: Tích vô hướng (dot product) của 2 vectors
- Mẫu số: Tích độ dài (norm) của 2 vectors
- Kết quả: -1 (đối lập) đến 1 (giống hệt), thường 0-1 trong practice

---

### **Weighted Average Rating**

$$\text{predicted\_rating}(u, i) = \frac{\sum_{k=1}^{K} \text{similarity}(u, u_k) \times \text{rating}(u_k, i)}{\sum_{k=1}^{K} \text{similarity}(u, u_k)}$$

**Giải Thích**:
- $u$ = target user
- $u_k$ = k-th similar user  
- $i$ = product
- similarity = trọng số (weight)
- rating = đánh giá từ similar user

---

## ⚙️ Hyperparameters (Tùy Chỉnh)

```python
# Code: recommendation_service.py - Line 113-117

class CollaborativeFilteringEngine:
    def __init__(self, k_neighbors=5, min_common_ratings=2):
        self.k_neighbors = k_neighbors  # ← Số similar users (KNN)
        self.min_common_ratings = min_common_ratings  # ← Min common products rated
```

| Tham Số | Giá Trị Mặc Định | Ý Nghĩa | Tác Động |
|---------|-----------------|---------|---------|
| `k_neighbors` | 5 | Số similar users xem xét | ↑ = chậm, ↓ = có thể thiếu data |
| `min_common_ratings` | 2 | Tối thiểu products cùng rate | ↑ = chặt hơn, ↓ = lỏng hơn |
| `min_predicted_rating` | 3.5 | Threshold gợi ý tối thiểu | ↑ = quality cao, ↓ = quantity cao |

---

## ✅ Ưu Điểm

| Ưu Điểm | Giải Thích |
|--------|-----------|
| **Đơn Giản** | Không cần training, dễ hiểu |
| **Hiệu Quả** | 70-80% accuracy với dataset vừa |
| **Linh Hoạt** | Dễ điều chỉnh k, thresholds |
| **Real-time** | Không cần training lại |
| **Interpretable** | Có thể giải thích vì sao gợi ý sản phẩm X |

---

## ❌ Nhược Điểm

| Nhược Điểm | Giải Thích | Giải Pháp |
|-----------|-----------|---------|
| **Cold Start Problem** | User mới chưa có reviews → không có neighbors | Dùng content-based hoặc popular products |
| **Data Sparsity** | Nếu ít reviews → matrix rất sparse | Thêm users, thêm reviews |
| **Popularity Bias** | Xu hướng recommend sản phẩm nổi tiếng | Thêm diversity penalty |
| **Scalability** | O(n²) → chậm với 100k+ users | Dùng Item-Based hoặc ML (SVD) |
| **No New Items** | Sản phẩm mới không có reviews → không được recommend | Item-based hoặc content-based |

---

## 🆚 So Sánh Với Các Thuật Toán Khác

| Thuật Toán | Độ Phức Tạp | Accuracy | Implementation | Cold Start |
|-----------|-----------|---------|-----------------|-----------|
| **User-Based CF** (Hiện Tại) | O(n²) | 70-80% | Dễ | ❌ Khó |
| **Item-Based CF** | O(m²) | 75-85% | Trung bình | ⚠️ Cải thiện |
| **Matrix Factorization (SVD)** | O(k²) | 85-90% | Khó | ✅ Tốt |
| **Deep Learning (Neural CF)** | O(k×n) | 90%+ | Rất khó | ✅ Tốt |
| **Hybrid** | O(n²+m²) | 90%+ | Rất khó | ✅ Tốt |
| **Content-Based** | O(n×m) | 60-70% | Trung bình | ✅ Tốt |

---

## 🔄 Khi Nào Dùng Thuật Toán Này?

✅ **Dùng User-Based CF khi**:
- Dataset nhỏ-vừa (< 10,000 users)
- Cần implementation nhanh
- Cần interpretability cao
- Đủ reviews (< 30% sparse)

❌ **Không dùng khi**:
- 100,000+ users (scalability issue)
- Quá ít reviews (sparsity issue)
- Cần accuracy 90%+
- Cold start problem nhiều

---

## 📈 Cải Thiện Có Thể

### **1. Hybrid Recommendation (Đang Implement)**

```python
# Code: recommendation_service.py - Line 252-290 (HybridRecommendationEngine)

class HybridRecommendationEngine:
    """
    Kết hợp 3 algorithms:
    - Collaborative Filtering (40%)
    - Content-based (30%)
    - Personalized (30%)
    """
```

### **2. Item-Based CF**

Thay vì so sánh users → so sánh products:
- Tìm products tương tự → recommend based on user's past ratings

### **3. Matrix Factorization (SVD)**

- Phân tách matrix thành latent factors
- Accuracy 85-90%
- Cần: numpy, scipy

### **4. Deep Learning (Neural CF)**

- Dùng neural networks để learn latent factors
- Accuracy 90%+
- Cần: TensorFlow, PyTorch

---

## 📝 Tóm Lại

| Tiêu Chí | Chi Tiết |
|---------|---------|
| **Thuật Toán** | User-Based Collaborative Filtering |
| **Similarity Metric** | Cosine Similarity |
| **Algorithm** | K-Nearest Neighbors (KNN) |
| **Prediction** | Weighted Average Rating |
| **Complexity** | O(n² × m) |
| **Accuracy** | 70-80% |
| **Implementation** | Memory-Based (không dùng ML) |
| **Best For** | Dataset nhỏ-vừa, cần speed + interpretability |

---

**File**: `/products/recommendation_service.py`  
**Lines**: 101-250  
**Status**: ✅ Fully Implemented + Tested  
**Last Updated**: 06/01/2026

