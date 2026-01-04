# ⚡ Collaborative Filtering - Quick Start Guide

## 📋 Tóm Tắt Những Gì Đã Được Thêm

| Thành Phần | Vị Trí | Trạng Thái |
|-----------|--------|----------|
| **Database Field** | ProductReview.user | ✅ Migration 0007 |
| **API Serializer** | ProductReviewSerializer | ✅ Includes user_id |
| **API Endpoint** | GET /api/products/collaborative/ | ✅ Ready |
| **Recommendation Engine** | recommendation_service.py | ✅ Implemented |
| **Admin Interface** | ProductReviewAdmin | ✅ Shows user_id |
| **Documentation** | COLLAB_FILTERING_GUIDE.md | ✅ Complete |

---

## 🚀 Cách Bắt Đầu

### 1. Xem Dữ Liệu Review Hiện Tại
```bash
# Django shell
python manage.py shell

>>> from products.models import ProductReview
>>> reviews = ProductReview.objects.filter(is_approved=True, user__isnull=False)
>>> reviews.count()
5  # Cần ít nhất 10-15 để test collaborative filtering

>>> for r in reviews[:5]:
...     print(f"User {r.user_id} → Product {r.product_id}: {r.rating}⭐")
User 1 → Product 10: 5⭐
User 2 → Product 10: 4⭐
...
```

### 2. Tạo Test Reviews (Nếu không đủ dữ liệu)
```bash
# Trong Django shell
python manage.py shell < create_demo_reviews.py

# Output:
# 👥 Users: 5
# 📦 Products: 8
# ✅ Created: 24 reviews
```

### 3. Test API Endpoint
```bash
# Đăng nhập user thứ nhất
curl -X POST "http://localhost:8000/api/token/" \
  -d "username=user1&password=pass"

# Lấy token từ response
TOKEN="eyJ0eXAiOiJKV1QiLCJhbGc..."

# Gọi collaborative recommendation
curl -X GET "http://localhost:8000/api/products/collaborative/?limit=5&min_rating=3.5" \
  -H "Authorization: Bearer $TOKEN" | jq

# Output:
{
  "count": 3,
  "recommendations": [
    {
      "id": 15,
      "name": "Pre-workout Energy",
      "predicted_rating": 4.5,
      ...
    }
  ]
}
```

---

## 🧮 Công Thức Toán Học (Nếu Tò Mò)

### Cosine Similarity
```
Tìm users tương tự dựa trên rating patterns
- 1.0 = Hoàn toàn giống nhau
- 0.9 = Rất giống
- 0.5 = Có chút liên hệ  
- 0.0 = Không liên hệ
```

### Weighted Average Prediction
```
rating_prediction = Σ(similar_user_rating × similarity_score)
                    ─────────────────────────────────────
                         Σ(similarity_score)
```

---

## 📊 Các Thuật Toán Hiện Có

### 1. **Content-based** (Đã có)
```
Xem products tương tự về category, type, goals
GET /api/products/{id}/recommendations/
```

### 2. **Personalized** (Đã có)
```
Xem products phù hợp với user's goal
GET /api/products/personalized/
```

### 3. **Collaborative Filtering** (NEW! 🎉)
```
Xem products mà similar users rated cao
GET /api/products/collaborative/
```

### 4. **Hybrid** (Foundation ready, algorithm TODO)
```
Kết hợp 3 algorithms trên
```

---

## 💾 Database Structure

```
ProductReview
├── id (Primary Key)
├── user (Foreign Key → User) ← NEW!
├── product (Foreign Key → Product)
├── rating (1-5)
├── title
├── content
├── is_approved
├── created_at
└── updated_at

Indexes:
✅ (user, product) - Find reviews
✅ (user, -created_at) - Timeline

Constraints:
✅ Unique(user, product) - 1 review per user per product
```

---

## 🔌 API Response Examples

### Success Case
```json
{
  "count": 3,
  "recommendations": [
    {
      "id": 10,
      "name": "Whey Protein Pro",
      "price": "29.99",
      "predicted_rating": 4.5,
      "actual_rating": 4.2,
      "category": "Whey Protein",
      "reason": "Similar users rated this 4.5/5"
    },
    {
      "id": 15,
      "name": "Pre-workout Energy",
      "predicted_rating": 4.3,
      ...
    }
  ],
  "similar_users": [
    {"user_id": 5, "similarity_score": 0.92},
    {"user_id": 8, "similarity_score": 0.88}
  ],
  "algorithm": "User-based Collaborative Filtering",
  "status": "✅ Success"
}
```

### Not Enough Data
```json
{
  "count": 0,
  "recommendations": [],
  "reason": "Not enough similar users found",
  "note": "Collaborative filtering needs more user reviews to work",
  "status": "⚠️ Insufficient data"
}
```

### Requires Login
```json
{
  "error": "Authentication required",
  "message": "Collaborative filtering requires authentication",
  "status": "❌ Failed"
}
```

---

## ⚙️ Configuration

### Engine Settings
```python
# products/recommendation_service.py

engine = CollaborativeFilteringEngine(
    k_neighbors=5,              # Find 5 similar users
    min_common_ratings=2        # Min products rated by both users
)

recommendations = engine.recommend(
    user_id=1,
    n_recommendations=5,        # Return top 5
    min_predicted_rating=3.5    # Only show if predicted >= 3.5
)
```

### Customize via URL
```bash
GET /api/products/collaborative/?limit=10&min_rating=3.0

limit=10         # Return 10 recommendations
min_rating=3.0   # Only show predicted rating >= 3.0
```

---

## 🐛 Troubleshooting

### Error: "Not enough similar users found"
- **Cause:** Not enough reviews in the system
- **Solution:** Run `python manage.py shell < create_demo_reviews.py`
- **Minimum:** 10+ reviews from 5+ different users

### Error: "No products with sufficient predicted rating"
- **Cause:** Similar users haven't reviewed unevaluated products
- **Solution:** Lower `min_rating` parameter or get more reviews

### Error: "Authentication required"
- **Cause:** Anonymous user tried to access CF endpoint
- **Solution:** Only authenticated users can use CF (need user_id)
- **Alternative:** Use content-based or personalized recommendations

### Slow Response
- **Cause:** Matrix too large or many similar users
- **Solution:** 
  - Reduce `k_neighbors` from 5 to 3
  - Add caching for frequently accessed users
  - Cache similarity matrix

---

## 📈 Monitoring

### Check Matrix Stats
```bash
python manage.py shell

>>> from products.models import ProductReview
>>> reviews = ProductReview.objects.filter(is_approved=True, user__isnull=False)
>>> users = reviews.values_list('user_id', flat=True).distinct().count()
>>> products = reviews.values_list('product_id', flat=True).distinct().count()
>>> print(f"Matrix: {users} users × {products} products = {users*products} cells")
>>> print(f"Reviews: {reviews.count()}")
>>> print(f"Sparsity: {100*reviews.count()/(users*products):.1f}%")

# Output:
# Matrix: 5 users × 8 products = 40 cells
# Reviews: 24
# Sparsity: 60.0%
```

### Top Products by Reviews
```bash
from django.db.models import Count
from products.models import Product

Product.objects.annotate(
    review_count=Count('reviews', 
    filter=Q(reviews__is_approved=True, reviews__user__isnull=False))
).order_by('-review_count')[:10]
```

---

## 🎯 Performance Targets

| Metric | Target | Current |
|--------|--------|---------|
| Response Time | < 1s | TBD |
| Accuracy (RMSE) | < 1.0 | TBD |
| Coverage | > 80% | TBD |
| CTR | > 10% | TBD |

---

## 📚 More Resources

- **Full Guide:** `COLLAB_FILTERING_GUIDE.md`
- **Architecture:** `COLLAB_FILTERING_SUMMARY.md`
- **Recommendation Algorithms:** `RECOMMENDATION_ALGORITHM.md`
- **User Profile Setup:** `docs/USER_PROFILE_SETUP_GUIDE.md`

---

## ✅ Checklist for Going Live

- [ ] Minimum 10+ reviews created
- [ ] API endpoint tested & working
- [ ] Database migration applied
- [ ] Admin interface shows user_id
- [ ] Response time acceptable
- [ ] Documentation reviewed
- [ ] A/B test framework ready
- [ ] Monitoring metrics in place

---

**Last Updated:** 2026-01-04  
**Status:** ✅ Ready for Testing & Production  
**Next:** Generate test data & test API endpoint
