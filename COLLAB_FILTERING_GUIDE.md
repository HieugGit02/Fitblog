# 🤝 Collaborative Filtering Recommendation - Hướng Dẫn

## Tổng Quan

Bảng `ProductReview` hiện tại **đã được cập nhật** để hỗ trợ **Collaborative Filtering** recommendation algorithm. 

Trước đó, chỉ có 2 thuật toán:
- ✅ Content-based: So sánh thông tin sản phẩm (category, type, goals)
- ✅ Personalized: Dựa vào user goal
- ❌ Collaborative Filtering: Cần user-item interaction matrix

Bây giờ bạn có **đủ dữ liệu** để xây dựng Collaborative Filtering!

---

## 📊 Cấu Trúc Dữ Liệu

### ProductReview Model
```python
class ProductReview(models.Model):
    user = ForeignKey(User, null=True, blank=True)  # ← NEW! User ID
    product = ForeignKey(Product)                     # ← Product ID  
    rating = IntegerField(1-5)                        # ← Rating (1-5 sao)
    author_name = CharField()                         # ← Fallback nếu anonymous
    author_email = EmailField()
    # ... các trường khác
```

### User-Item Matrix (Collaborative Filtering)
```
        Product_1  Product_2  Product_3  Product_4
User_1      5         4         null      3
User_2      4         null      5         4
User_3      null      5         4         5
User_4      3         4         null      null

Mỗi cell = rating của user cho product
null = user chưa đánh giá product
```

---

## 🔌 API Endpoints

### 1. **Lấy Tất Cả Reviews (với user_id & product_id)**
```bash
GET /api/reviews/
```

**Response:**
```json
{
  "count": 15,
  "results": [
    {
      "id": 1,
      "user_id": 5,                    # ← ID người dùng
      "username": "john_doe",          # ← Username
      "product_id": 10,                # ← ID sản phẩm
      "rating": 5,                     # ← Điểm 1-5
      "title": "Sản phẩm tốt",
      "content": "Rất hài lòng...",
      "is_approved": true,
      "created_at": "2026-01-04T10:30:00Z"
    },
    {
      "id": 2,
      "user_id": 3,
      "product_id": 15,
      "rating": 4,
      ...
    }
  ]
}
```

### 2. **Lọc Reviews theo Product**
```bash
GET /api/reviews/?product=10
```

Lấy tất cả reviews cho product ID 10 (kèm user_id)

### 3. **Lọc Reviews theo User**
```bash
GET /api/reviews/?user=5
```

Lấy tất cả reviews của user ID 5 (các sản phẩm họ đã đánh giá)

### 4. **Lọc Reviews theo Rating**
```bash
GET /api/reviews/?rating=5
```

Lấy tất cả reviews với 5 sao

### 5. **Tạo Review Mới (Tự động gán user)**
```bash
POST /api/reviews/
Content-Type: application/json

{
  "product": 10,
  "rating": 5,
  "title": "Sản phẩm rất tốt",
  "content": "Mình rất hài lòng với chất lượng...",
  "author_name": "John Doe",          # ← Fallback nếu không login
  "author_email": "john@example.com"
}
```

**Nếu user đã authenticated → tự động gán `user_id`**
**Nếu anonymous → để trống `user_id`, dùng `author_name` & `author_email`**

---

## 🧮 Ví Dụ Xây Dựng Collaborative Filtering

### Step 1: Lấy User-Item Matrix
```python
from products.models import ProductReview
import pandas as pd
import numpy as np

# Lấy tất cả reviews approved
reviews = ProductReview.objects.filter(
    is_approved=True, 
    user__isnull=False  # Chỉ lấy reviews từ authenticated users
).values('user_id', 'product_id', 'rating')

# Chuyển sang DataFrame
df = pd.DataFrame(list(reviews))

# Tạo pivot table (user-item matrix)
user_item_matrix = df.pivot_table(
    index='user_id',
    columns='product_id', 
    values='rating',
    fill_value=0  # 0 = chưa đánh giá
)

print(user_item_matrix)
#            1    2    3    4
# user_id            
# 1        5.0  4.0  0.0  3.0
# 2        4.0  0.0  5.0  4.0
# 3        0.0  5.0  4.0  5.0
# 4        3.0  4.0  0.0  0.0
```

### Step 2: Tính Độ Tương Đồng (Similarity) Giữa Users
```python
from sklearn.metrics.pairwise import cosine_similarity

# Tính cosine similarity giữa các users
user_similarity = cosine_similarity(user_item_matrix)

print(f"User 1 tương tự User 2: {user_similarity[0][1]:.2f}")
# Output: User 1 tương tự User 2: 0.96 (rất giống nhau)
```

### Step 3: Recommend Sản Phẩm cho User
```python
def collaborative_recommend(user_id, n_recommendations=5):
    """
    Dùng Collaborative Filtering để gợi ý sản phẩm cho user
    
    Logic:
    1. Tìm users tương tự với user đó
    2. Xem những sản phẩm mà similar users đã đánh giá cao
    3. Sản phẩm đó mà target user chưa đánh giá
    4. Recommend top N sản phẩm
    """
    # Lấy users tương tự
    user_idx = list(user_item_matrix.index).index(user_id)
    similar_users = np.argsort(user_similarity[user_idx])[::-1][1:6]  # Top 5 similar users
    
    # Lấy sản phẩm mà user này chưa đánh giá
    user_ratings = user_item_matrix.loc[user_id]
    unevaluated_products = user_ratings[user_ratings == 0].index.tolist()
    
    # Tính score dựa vào similar users
    recommendations = {}
    for prod_id in unevaluated_products:
        scores = []
        for similar_user_idx in similar_users:
            similar_user_id = user_item_matrix.index[similar_user_idx]
            rating = user_item_matrix.loc[similar_user_id, prod_id]
            if rating > 0:
                similarity_score = user_similarity[user_idx][similar_user_idx]
                scores.append(rating * similarity_score)
        
        if scores:
            recommendations[prod_id] = np.mean(scores)
    
    # Sort và return top N
    top_products = sorted(recommendations.items(), key=lambda x: x[1], reverse=True)[:n_recommendations]
    return [prod_id for prod_id, score in top_products]

# Ví dụ
recommended = collaborative_recommend(user_id=1, n_recommendations=3)
print(f"Gợi ý cho user 1: {recommended}")
# Output: Gợi ý cho user 1: [3, 15, 8]
```

---

## 📈 Hybrid Recommendation (Kết Hợp 3 Algorithms)

Bạn có thể kết hợp **Collaborative + Content-based + Personalized**:

```python
def hybrid_recommend(user_id, n_recommendations=5):
    """
    Kết hợp 3 algorithms:
    1. Collaborative Filtering (30%)
    2. Content-based (40%)
    3. Personalized (30%)
    """
    collab_items = set(collaborative_recommend(user_id, 20))
    content_items = set(content_based_recommend(user_id, 20))
    personalized_items = set(personalized_recommend(user_id, 20))
    
    # Tính scores
    scores = {}
    for item in collab_items | content_items | personalized_items:
        score = 0
        if item in collab_items:
            score += 0.30
        if item in content_items:
            score += 0.40
        if item in personalized_items:
            score += 0.30
        scores[item] = score
    
    # Return top N
    recommendations = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:n_recommendations]
    return [item_id for item_id, score in recommendations]
```

---

## 🗄️ Database Constraints

### Unique Constraint
```python
# Mỗi user chỉ có 1 review cho 1 sản phẩm
unique_together = ('user', 'product')
```

Nếu user đã review một sản phẩm, không thể tạo review thứ 2 cho sản phẩm đó.

### Indexes (Để Tối Ưu Truy Vấn)
```python
Index(fields=['user', 'product'])           # Tìm review của user cho product
Index(fields=['user', '-created_at'])       # Lấy reviews gần đây của user
```

---

## 🚀 Next Steps

### Phase 1: Data Collection ✅ DONE
- ProductReview đã có `user_id` & `product_id`
- API có thể trả về user-item matrix

### Phase 2: Implement Collaborative Filtering 🔄 TODO
```bash
# Cài đặt dependencies
pip install scikit-learn pandas numpy

# Tạo recommendation service
# products/recommendation_service.py
```

### Phase 3: Deploy Collaborative Filtering View
```python
# API endpoint
GET /api/products/collab-recommendations/?user_id=5

# Response: Gợi ý từ collaborative filtering
```

### Phase 4: A/B Testing
So sánh độ chính xác giữa 3 algorithms:
- Collaborative Filtering
- Content-based
- Personalized
- Hybrid (kết hợp)

---

## 📊 SQL Queries Hữu Ích

### Lấy User-Item Matrix
```sql
SELECT 
    user_id,
    product_id,
    rating
FROM products_productreview
WHERE is_approved = true
ORDER BY user_id, product_id;
```

### Tìm Users Tương Tự (đánh giá cùng sản phẩm)
```sql
SELECT 
    pr1.user_id,
    pr2.user_id,
    COUNT(*) as common_products,
    AVG(ABS(pr1.rating - pr2.rating)) as rating_diff
FROM products_productreview pr1
JOIN products_productreview pr2 
    ON pr1.product_id = pr2.product_id 
    AND pr1.user_id < pr2.user_id
WHERE pr1.is_approved = true 
    AND pr2.is_approved = true
GROUP BY pr1.user_id, pr2.user_id
ORDER BY common_products DESC;
```

### Lấy Products Chưa Review Của User
```sql
SELECT p.id
FROM products_product p
WHERE p.id NOT IN (
    SELECT product_id 
    FROM products_productreview 
    WHERE user_id = 5
)
LIMIT 10;
```

---

## 🎯 Metrics Theo Dõi

- **Review Coverage**: % products có ít nhất 1 review
- **User Engagement**: % users có ít nhất 1 review
- **Matrix Sparsity**: % cells trong user-item matrix là 0
- **Recommendation Quality**: Click-through rate, conversion rate

---

## 📝 Chú Ý

1. **Anonymous Users**: Nếu `user_id = null`, review không dùng cho Collaborative Filtering
2. **Unapproved Reviews**: Không dùng reviews chưa được duyệt (is_approved = false)
3. **Rating Scale**: 1-5 stars (1 = xấu, 5 = tuyệt vời)
4. **Cold Start Problem**: Users/products mới không có review → cần content-based fallback

---

**Created:** 2026-01-04  
**Status:** ✅ Data Infrastructure Ready, Algorithm Implementation Pending
