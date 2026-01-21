# ❓ PHÂN BIỆT 3 LOẠI RECOMMENDATION: PERSONALIZED vs GOAL-BASED vs CONTENT-BASED

## ⚠️ NHẬP NHẰNG TRONG TÀI LIỆU CŨ

Tài liệu `RECOMMENDATION_SYSTEM.md` viết:
```
### 3️⃣ **GOAL-BASED RECOMMENDATIONS**
### 4️⃣ **CONTENT-BASED RECOMMENDATIONS**
```

**Nhưng thực tế trong code thì CHỈ CÓ 3 LOẠI:**
1. ✅ **`personalized`** - Khi product MATCH goal của user
2. ✅ **`content-based`** - Khi product KHÔNG match goal nhưng cùng category
3. ✅ **`review-action`** - Khi user submit review (cho collaborative filtering)

---

## 🔍 PHÂN TÍCH CODE CHI TIẾT

### VỊ TRÍ 1: Product Detail View (lines 1070-1120 in views.py)

```python
# 📍 products/views.py, lines 1079-1084
if user_profile.goal in product.suitable_for_goals:
    # ✅ TYPE 1: "personalized" - MATCHES GOAL
    log, created = RecommendationLog.objects.get_or_create(
        user_profile=user_profile,
        recommended_product=product,
        recommendation_type='personalized',  # 🔑 LOẠI 1
        defaults={'score': 0.95, 'clicked': True}
    )

# 📍 products/views.py, lines 1094-1099
else:
    # ✅ TYPE 2: "content-based" - SAME CATEGORY, DIFFERENT GOAL
    log, created = RecommendationLog.objects.get_or_create(
        user_profile=user_profile,
        recommended_product=product,
        recommendation_type='content-based',  # 🔑 LOẠI 2
        defaults={'score': 0.5, 'clicked': True}
    )
```

**LỰA CHỌN LÀ:**
- Nếu `user.goal` ∈ `product.suitable_for_goals` → `"personalized"` (0.95 score)
- Nếu `user.goal` ∉ `product.suitable_for_goals` → `"content-based"` (0.5 score)

---

### VỊ TRÍ 2: Review Submission (lines 1000-1020 in views.py)

```python
# 📍 products/views.py, lines 1010-1022
if user:
    # ✅ TYPE 3: "review-action" - USER REVIEWS A PRODUCT
    rec_log, rec_created = RecommendationLog.objects.get_or_create(
        user_profile=user_profile,
        recommended_product=product,
        recommendation_type='review-action',  # 🔑 LOẠI 3
        defaults={
            'score': rating_score,  # 1-5 → 0-1
            'clicked': True
        }
    )
```

**QUAN TRỌNG:**
- Chỉ authenticated users mới tạo "review-action" log
- Anonymous users: `if user:` → FALSE → không tạo log

---

## 📊 SO SÁNH 3 LOẠI

| Loại | Điều kiện tạo | Score | Clicked? | Mục đích |
|------|---|---|---|---|
| **personalized** | Product matches user's goal | 0.95 | ✅ True | User explicitly browsed products for their goal |
| **content-based** | Product same category but NOT user's goal | 0.5 | ✅ True | User browsed but not aligned with goal |
| **review-action** | User writes/updates a review | rating/5 | ✅ True | Collaborative filtering training data |

---

## 🚫 KHÔNG CÓ "GOAL-BASED" LÀ LOẠI RIÊNG

### Tại sao tài liệu viết "GOAL-BASED"?

```python
# 📍 products/views.py, line 530
personalized_products = RecommendationLog.objects.filter(
    user_profile=user,
    recommendation_type__in=['personalized', 'goal-based']  # ⚠️ Bị mix
)
```

**ĐÂY LÀ BUG!** Code filter cả `'goal-based'` nhưng:
- ❌ Database KHÔNG CÓ loại `'goal-based'` nào được tạo
- ✅ Chỉ có `'personalized'` được tạo (khi match goal)

### Lý do:

Người viết code định nghĩa:
- `'personalized'` = product matches goal
- Nhưng sau đó filter thêm `'goal-based'` (dự phòng?)
- Thực tế: **KHÔNG CÓ loại nào được tạo với tên `'goal-based'`**

---

## 🎯 LOGIC THỰC TẾ

```
┌─────────────────────────────────────┐
│ User visits product detail page     │
└─────────────────────────────────────┘
            │
            ▼
┌─────────────────────────────────────┐
│ Does user have profile + goal?      │
│ (goal != 'general-health')          │
└─────────────────────────────────────┘
         │          │
      YES │          │ NO
         ▼          ▼
    ┌────────┐   └─ Skip (no logging)
    │
    ▼
┌──────────────────────────────┐
│ Does product match goal?     │
│ (goal in suitable_for_goals) │
└──────────────────────────────┘
     │ YES           │ NO
     ▼               ▼
"personalized"   "content-based"
score: 0.95      score: 0.5
```

---

## 💭 RECOMMENDATION LOG TYPES THỰC HIỆN

```python
# 📍 products/models.py - RecommendationLog model
RECOMMENDATION_TYPES = [
    ('personalized', 'Personalized (goal match)'),
    ('content-based', 'Content-Based (same category)'),
    ('review-action', 'Review Action'),
    # ('goal-based', 'Goal-Based'),  ← ❌ KHÔNG DÙNG
]
```

---

## 🔧 CÁCH SỬA DOCUMENTATION

### Option 1: Xóa GOAL-BASED (nên làm)
```markdown
### 1️⃣ **PERSONALIZED RECOMMENDATIONS** ✅
- Khi: User goal MATCHES product suitable_for_goals
- Score: 0.95

### 2️⃣ **CONTENT-BASED RECOMMENDATIONS** ✅
- Khi: User goal KHÔNG MATCH nhưng cùng category
- Score: 0.5

### 3️⃣ **REVIEW-ACTION RECOMMENDATIONS** ✅
- Khi: User submit review (authenticated only)
- Score: rating / 5.0
```

### Option 2: Giải thích rõ
```markdown
Có 3 loại recommendation:
1. Personalized (goal match) - gợi ý sản phẩm phù hợp goal
2. Content-based (not goal) - gợi ý same category
3. Review-action (collaf filter) - dùng để training ML model
```

---

## 📝 TÓML: PERSONALIZED ≠ GOAL-BASED

```
❌ NHẦM: "PERSONALIZED và GOAL-BASED là 2 cái khác nhau"
✅ ĐÚNG: "Cả 2 đều là personalized (chỉ khác tên lý thuyết)"

❌ NHẦM: "Có 4 loại recommendation"
✅ ĐÚNG: "Chỉ có 3 loại: personalized, content-based, review-action"

❌ NHẦM: "GOAL-BASED được tạo trong code"
✅ ĐÚNG: "Chỉ được filter nhưng không bao giờ được tạo"
```

---

## 🎓 GIẢI THÍCH TRIẾT LÝ

**"Personalized" trong code Fitblog:**
```
= "Gợi ý sản phẩm phù hợp với MỤC TIÊU CỤ THỂ của user"
= "Goal-based" (theo lý thuyết)
```

**"Content-based" trong code Fitblog:**
```
= "Gợi ý sản phẩm tương tự (category) dù không match goal"
= "Recommendation based on product attributes"
```

**"Review-action":**
```
= "Log mỗi khi user review → dữ liệu cho collaborative filtering"
= "User feedback for ML model"
```

---

## ✅ KẾT LUẬN

**Câu hỏi của bạn:** *"PERSONALIZED và GOAL-BASED chung 1 cái à?"*

**Trả lời:**
1. ✅ **Trong code**: Chỉ có `'personalized'` được tạo (không có `'goal-based'`)
2. ✅ **Theo lý thuyết**: Personalized = Goal-based + Content-based
3. ✅ **Thực hiện**: Mỗi product view → log as either personalized hoặc content-based

**Tổng cộng: 3 loại recommendation**
- `personalized` - matches goal
- `content-based` - same category, different goal  
- `review-action` - user review

---

**Cần sửa RECOMMENDATION_SYSTEM.md không?** (Y/N)
