# 🎯 Test Auto-Link User Review Feature

## ✅ Implementation Complete

Các file đã sửa:
1. ✅ `/products/views.py` - product_detail() view - Line 894-945
2. ✅ `/templates/products/product_detail.html` - Review form - Line 258-320

---

## 🧪 Test Cases

### **Test 1: Anonymous User Reviews**

**Kịch Bản**:
1. Không đăng nhập
2. Vào product detail
3. Điền form review: tên, email, rating=5, tiêu đề, nội dung
4. Submit

**Kỳ Vọng**:
```
✅ ProductReview tạo với:
   - user = NULL (vì anonymous)
   - author_name = (tự nhập)
   - author_email = (tự nhập)

❌ RecommendationLog KHÔNG tạo (vì user=NULL)
❌ Collab filtering KHÔNG chạy
```

**Database Check**:
```sql
SELECT * FROM products_productreview 
WHERE user_id IS NULL 
ORDER BY created_at DESC LIMIT 1;
```

---

### **Test 2: Authenticated User Reviews** (🆕 NEW)

**Kịch Bản**:
1. ✅ Đăng nhập (user: john_doe, email: john@example.com)
2. Vào product detail
3. Thấy form review:
   - ✅ Alert: "✅ Đang đăng nhập: john_doe"
   - ✅ Tên + Email fields ẨN
   - ✅ Review info: "Review sẽ được ghi tên: John Doe"
4. Chỉ cần điền: rating=5, tiêu đề, nội dung
5. Submit

**Kỳ Vọng**:
```
✅ ProductReview tạo với:
   - user = User(id=X, username="john_doe")
   - author_name = "John Doe" (auto-filled)
   - author_email = "john@example.com" (auto-filled)

✅ RecommendationLog tạo với:
   - user_profile = john_doe.userprofile
   - recommended_product = (sản phẩm hiện tại)
   - recommendation_type = "review-action"
   - score = 1.0 (vì rating=5)

✅ Log: "✅ Review by authenticated user: john_doe"
✅ Log: "📊 RecommendationLog created for john_doe rating=1.00"
```

**Database Check**:
```sql
-- ProductReview
SELECT * FROM products_productreview 
WHERE user_id IS NOT NULL 
ORDER BY created_at DESC LIMIT 1;

-- RecommendationLog
SELECT * FROM products_recommendationlog 
WHERE recommendation_type = 'review-action'
ORDER BY created_at DESC LIMIT 1;
```

---

### **Test 3: Multi-Review (Duplicate Check)**

**Kịch Bản**:
1. User john_doe xem product #1
2. Submit review rating=5
3. Quay lại product #1
4. Submit review lại rating=3

**Kỳ Vọng**:
```
❌ Error: "IntegrityError: Duplicate unique constraint"
   (vì có constraint: unique_user_product_review)

Hoặc:
✅ Update review cũ (nếu implement update logic)
```

---

### **Test 4: Collaborative Filtering Works**

**Kịch Bản**:
1. User A đăng nhập → review product #1 rating=5
2. User B đăng nhập → review product #1 rating=5
3. User B → review product #2 rating=4, #3 rating=5
4. User A view profile
5. Xem "Gợi Ý Cho Bạn"

**Kỳ Vọng**:
```
✅ User A similar to User B (both like product #1)
✅ Product #2, #3 được recommend cho User A
✅ Type: "personalized" hoặc "review-action"
```

---

## 🧬 Check Database (Manual)

```bash
# Activate venv
source venv/bin/activate

# Enter shell
python manage.py shell
```

```python
from products.models import ProductReview, RecommendationLog, User, UserProfile

# Test 1: Check anonymous reviews
anonymous_reviews = ProductReview.objects.filter(user__isnull=True)
print(f"Anonymous reviews: {anonymous_reviews.count()}")
for r in anonymous_reviews.order_by('-created_at')[:3]:
    print(f"  - {r.author_name} ({r.rating}★)")

# Test 2: Check authenticated reviews
auth_reviews = ProductReview.objects.filter(user__isnull=False)
print(f"\nAuthenticated reviews: {auth_reviews.count()}")
for r in auth_reviews.order_by('-created_at')[:3]:
    print(f"  - {r.user.username} ({r.rating}★)")

# Test 3: Check RecommendationLogs from reviews
review_logs = RecommendationLog.objects.filter(recommendation_type='review-action')
print(f"\nRecommendationLogs from reviews: {review_logs.count()}")
for log in review_logs.order_by('-created_at')[:3]:
    print(f"  - {log.user_profile.user.username if log.user_profile.user else 'N/A'}: {log.recommended_product.name} (score={log.score:.2f})")

# Test 4: Check matrix building
from products.recommendation_service import UserItemMatrix
matrix = UserItemMatrix()
if matrix.matrix is not None:
    print(f"\n✅ Matrix built: {len(matrix.user_ids)} users × {len(matrix.product_ids)} products")
    print(f"   Total reviews: {matrix.matrix.sum()}")
else:
    print("\n❌ Matrix NOT built (no reviews?)")

# Test 5: Test collab recommend
from products.recommendation_service import get_collaborative_engine
engine = get_collaborative_engine()
user = User.objects.get(username="john_doe")
recommendations = engine.recommend(user.id, n_recommendations=3)
print(f"\nRecommendations for john_doe: {len(recommendations)} items")
for prod_id, score in recommendations:
    print(f"  - Product #{prod_id} (score={score:.2f})")

exit()
```

---

## 📝 Log Statements (Debugging)

### **View Logs** (Terminal output when review submitted):

**Case 1: Anonymous**
```
📝 Review by anonymous: Minh Hiếu
```

**Case 2: Authenticated** (✨ NEW)
```
✅ Review by authenticated user: john_doe
📊 RecommendationLog created for john_doe rating=1.00
```

### **Check Logs File**:
```bash
tail -f logs/django.log | grep -i "review\|recommendation"
```

---

## ✅ Checklist

### Code Changes
- [x] `/products/views.py` - Auto-link user logic
- [x] `/templates/products/product_detail.html` - Conditional form
- [x] Django system check - ✅ 0 errors

### Testing
- [ ] Test anonymous review
- [ ] Test authenticated review
- [ ] Check ProductReview.user field
- [ ] Check RecommendationLog created
- [ ] Test collab filtering with multiple users

### Verification
- [ ] logs in database show user_id (not NULL)
- [ ] RecommendationLog created with review-action type
- [ ] matrix building successful
- [ ] collab recommend returns products

---

## 🎯 Success Criteria

✅ **Anonymous users**: Can review without login
- ✅ Form shows name + email fields
- ✅ ProductReview.user = NULL
- ✅ No RecommendationLog

✅ **Authenticated users**: Auto-filled review
- ✅ Form hides name + email
- ✅ ProductReview.user = User (not NULL)
- ✅ RecommendationLog created
- ✅ Collab filtering can use it

✅ **Collaborative Filtering**: Works with reviews
- ✅ User-item matrix includes authenticated user reviews
- ✅ Similar users found
- ✅ Recommendations generated

---

## 🚀 Next Steps

1. ✅ Test both cases (anonymous + authenticated)
2. ✅ Verify database inserts
3. ✅ Run full collab filtering test
4. ✅ Monitor logs for errors
5. ⏳ Deploy to Railway

---

**Status**: ✅ Ready for Testing  
**Files Changed**: 2  
**Lines Added**: ~80  
**Test Time**: ~10 minutes
