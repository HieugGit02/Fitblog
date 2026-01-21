# 🎯 Hành Vi Của Recommendation Khi User Đổi Goal

## Câu Hỏi Người Dùng
> "Giả sử ban đầu là mục tiêu tăng cơ và recommendation hiện những sản phẩm tăng cơ, h người dùng đổi thông tin sang tăng cơ giảm mỡ, thì những recommendation cũ có mất và thay bằng recommendation sản phẩm tăng cơ giảm mỡ ko"

---

## 📊 Trả Lời: **KHÔNG MẤT - VẪN GIỮ LẠI**

### Kịch Bản Cụ Thể

```
🔄 TRƯỚC:
User "Hieu"
├─ Goal: "muscle-building" (tăng cơ)
├─ Recommendation Logs:
│  ├─ Log #1: Creatine (type: personalized) ✅
│  ├─ Log #2: BCAA (type: personalized) ✅
│  └─ Log #3: Whey (type: goal-based) ✅
└─ UI hiển thị 6 sản phẩm trong "Gợi Ý Cho Bạn"

🔄 AFTER (User cập nhật goal → "muscle-gain-weight-loss"):
User "Hieu"
├─ Goal: "muscle-gain-weight-loss" (tăng cơ giảm mỡ) ← THAY ĐỔI
├─ Recommendation Logs cũ:
│  ├─ Log #1: Creatine (type: personalized) ← VẪN CÓ
│  ├─ Log #2: BCAA (type: personalized) ← VẪN CÓ
│  └─ Log #3: Whey (type: goal-based) ← VẪN CÓ
├─ NEW Recommendation Logs:
│  ├─ Log #4: Green Tea (type: personalized) ✨ NEW
│  ├─ Log #5: Garcinia (type: goal-based) ✨ NEW
│  └─ Log #6: L-Carnitine (type: personalized) ✨ NEW
└─ UI hiển thị 6 sản phẩm MỚI NHẤT (Log #4-9) trong "Gợi Ý Cho Bạn"
```

---

## 🔍 Lý Do: Code Chứng Minh

### 1️⃣ **Recommendation Logs Không Bị Xóa**

```python
# Code: products/views.py - Line 424-428
if request.method == 'POST':
    form = UserProfileForm(request.POST, instance=user_profile)
    if form.is_valid():
        form.save()  # ← Chỉ UPDATE goal, KHÔNG DELETE logs
        messages.success(request, '✅ Thông tin của bạn đã được lưu!')
        return redirect('products:user_profile_view')
```

**Kết luận**: `form.save()` chỉ cập nhật UserProfile, **KHÔNG xóa** RecommendationLog cũ.

---

### 2️⃣ **Database Schema: Log Độc Lập Với Goal**

```python
# Code: products/models.py

class UserProfile(models.Model):
    goal = models.CharField(...)  # ← User cập nhật cái này
    # ... other fields

class RecommendationLog(models.Model):
    user_profile = models.ForeignKey(UserProfile, ...)
    recommended_product = models.ForeignKey(Product, ...)
    recommendation_type = models.CharField(...)  # personalized, goal-based, etc.
    score = models.FloatField()
    clicked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)  # ← Mốc thời gian
```

**Kết luận**: RecommendationLog **độc lập** với UserProfile.goal, chỉ lưu reference.

---

### 3️⃣ **Query Logic: Hiển Thị 6 Mới Nhất**

```python
# Code: products/views.py - Line 528-533

personalized_products = RecommendationLog.objects.filter(
    user_profile=user_profile,
    recommendation_type__in=['personalized', 'goal-based']
).order_by('-created_at')[:6]  # ← Lấy 6 MỚI NHẤT theo thời gian
```

**Kết luận**: 
- ✅ Tất cả logs cũ vẫn trong database
- ✅ Hiển thị chỉ **6 cái mới nhất** (theo `created_at`)
- ✅ Nếu có log mới được tạo → nó sẽ thay thế log cũ nhất trong top 6

---

## 🔄 Workflow Chi Tiết

```
┌─────────────────────────────────────────────────────────┐
│ 1. User xem sản phẩm (goal=muscle-building)           │
├─────────────────────────────────────────────────────────┤
│ ✅ RecommendationLog #1: Creatine (personalized)       │
│ ✅ RecommendationLog #2: BCAA (goal-based)             │
│ ✅ RecommendationLog #3: Whey (personalized)           │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│ 2. User UPDATE goal → "muscle-gain-weight-loss"       │
├─────────────────────────────────────────────────────────┤
│ UserProfile.goal = "muscle-gain-weight-loss"           │
│ RecommendationLog (tất cả 3 cái): VẪN CÓ ✓            │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│ 3. System tự động sinh gợi ý MỚI                       │
├─────────────────────────────────────────────────────────┤
│ (Khi user xem sản phẩm hoặc truy cập /personalized/)   │
│ ✨ RecommendationLog #4: Green Tea (personalized)      │
│ ✨ RecommendationLog #5: Garcinia (goal-based)         │
│ ✨ RecommendationLog #6: L-Carnitine (personalized)    │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│ 4. UI hiển thị (Line 528-533 trong views.py)          │
├─────────────────────────────────────────────────────────┤
│ query: RecommendationLog                               │
│   .filter(user_profile=user, type__in=[...])           │
│   .order_by('-created_at')[:6]  ← 6 MỚI NHẤT          │
├─────────────────────────────────────────────────────────┤
│ Kết quả: Log #4, #5, #6, #3, #2, #1 (Top 6)          │
│          (Mới nhất → Cũ nhất)                          │
└─────────────────────────────────────────────────────────┘
```

---

## 📋 Bảng So Sánh

| Tiêu Chí | Chi Tiết | Kết Quả |
|---------|---------|--------|
| **RecommendationLog cũ** | Vẫn lưu trong DB | ✅ VẬN GIỮ |
| **RecommendationLog mới** | Được sinh tự động | ✨ THÊM MỚI |
| **"Gợi Ý Cho Bạn" hiển thị** | 6 mới nhất theo thời gian | 🔄 CẬP NHẬT |
| **"Lịch Sử Xem" hiển thị** | Tất cả logs (5/trang) | ✅ VẬN GIỮ TOÀN BỘ |
| **Goal field** | Thay đổi từ A → B | 🔄 CẬP NHẬT |

---

## ⚙️ CÓ THỂ CẢI THIỆN KHÔNG?

### Vấn Đề Hiện Tại
- ❌ Recommendation cũ (từ goal cũ) vẫn nằm trong "Lịch Sử Xem"
- ❌ Có thể gây nhầm lẫn: "Tại sao còn sản phẩm tăng cơ khi tôi đổi sang giảm mỡ?"

### 3 Giải Pháp

#### **Giải Pháp 1: Tạo "Recommendation Version" (Khuyên Dùng)**
```python
# Thêm field vào RecommendationLog
class RecommendationLog(models.Model):
    user_profile_goal_at_time = models.CharField()  # muscle-building
    # ...
```

Để log ghi nhớ goal lúc nó được tạo, dễ phân biệt.

#### **Giải Pháp 2: Đánh Dấu Log Cũ (Nếu Goal Thay Đổi)**
```python
# Thêm field
class RecommendationLog(models.Model):
    is_stale = models.BooleanField(default=False)  # Nếu goal thay đổi
    # ...

# Khi user update goal:
RecommendationLog.objects.filter(user_profile=user).update(is_stale=True)
# Rồi sinh log mới
```

Sau đó UI chỉ hiển thị `is_stale=False` logs.

#### **Giải Pháp 3: Xóa Log Cũ Khi Đổi Goal (Bạo Lực)**
```python
# Khi user update goal:
RecommendationLog.objects.filter(user_profile=user).delete()
# Xóa sạch, sinh từ đầu
```

⚠️ Mất dữ liệu lịch sử → **KHÔNG KHUYÊN DÙNG**

---

## 🎬 Kết Luận

### Câu Trả Lời Ngắn Gọn

> **Q**: Những recommendation cũ (từ goal "tăng cơ") có mất khi đổi sang "tăng cơ giảm mỡ" không?  
> **A**: **KHÔNG**, logs cũ vẫn giữ lại trong database. Nhưng "Gợi Ý Cho Bạn" sẽ **chỉ hiển thị 6 cái MỚI NHẤT**, nên logs cũ sẽ bị đẩy xuống hoặc lẫn trong "Lịch Sử Xem".

### Hành Vi Hiện Tại
- ✅ **Lịch Sử Xem**: Vẫn thấy tất cả (cũ + mới)
- ✅ **Gợi Ý Cho Bạn**: Chỉ 6 mới nhất
- ✅ **Goal field**: Cập nhật (muscle-building → muscle-gain-weight-loss)

### Nên Cải Thiện?
- 🟡 **Tùy logic UX**: Nếu muốn rõ ràng hơn, dùng **Giải Pháp 1** (ghi nhớ goal lúc sinh log)

---

## 📝 Tóm Lại Bằng Code

```python
# Khi user update goal
user_profile.goal = "muscle-gain-weight-loss"
user_profile.save()

# ✅ RecommendationLog cũ:
RecommendationLog.objects.filter(user_profile=user_profile)  # VẬN CÓ 3 logs cũ

# ✨ RecommendationLog mới:
# Được sinh khi user xem sản phẩm → tạo log với goal mới

# 📊 Query hiển thị:
personalized_products = RecommendationLog.objects.filter(
    user_profile=user_profile
).order_by('-created_at')[:6]
# → [Log mới, Log mới, Log mới, Log cũ, Log cũ, Log cũ]
```

---

**File này được tạo**: 06/01/2026  
**Session**: Giải thích hành vi goal change  
**Status**: ✅ Đủ thông tin để quyết định cải thiện
