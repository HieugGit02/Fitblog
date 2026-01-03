# 📋 Hướng Dẫn UserProfile Setup - Người Dùng Điền Thông Tin

## 🎯 Giải Quyết Vấn đề Của Bạn

**Câu hỏi:** *"Truy cập lần đầu nhận session rồi, nhưng ở đâu để người dùng điền UserProfile?"*

**Trả lời:** Giờ đã có 3 trang để người dùng điền thông tin:

1. **Thiết Lập Đầy Đủ** → `/products/setup/`
2. **Quick Setup** → `/products/quick-setup/`
3. **Xem & Chỉnh Sửa Hồ Sơ** → `/products/profile/`

---

## 🚀 Cách Hoạt Động - Quy Trình Đầy Đủ

### **Bước 1: Người dùng truy cập website**

```
User mở browser → Vào localhost:8000/
↓
Django tạo session_id (lưu vào cookie)
↓
Middleware tự động tạo UserProfile mới (empty)
↓
Thêm request.user_profile để dùng trong views
```

### **Bước 2: User click vào link "Hồ Sơ" trong Navigation**

```html
<!-- Link trong base.html navigation bar -->
<a href="/products/profile/"> Hồ Sơ</a>
```

Hoặc trực tiếp vào: `http://localhost:8000/products/profile/`

### **Bước 3: User setup thông tin (Cách A: Đầy đủ)**

```
Click "Thiết lập thông tin" → Vào /products/setup/
↓
Form hiển thị:
- Tuổi (16-120)
- Cân nặng (kg)
- Chiều cao (cm)
- Mục tiêu fitness
- Mức độ vận động
- Loại supplement ưa thích (tùy chọn)
- Hạn chế ăn uống (tùy chọn)
↓
Click "Lưu Thông Tin"
↓
Server tính BMI & TDEE tự động
↓
Lưu vào database
↓
Redirect về /products/
```

### **Bước 4: Setup thông tin (Cách B: Quick)**

```
Click "Quick Setup" → Vào /products/quick-setup/
↓
Form ngắn chỉ hỏi 5 thứ:
- Tuổi
- Cân nặng
- Chiều cao
- Mục tiêu
- Mức độ vận động
↓
Click "Xong!"
↓
Lưu + Redirect
```

### **Bước 5: User xem profile**

```
Vào /products/profile/
↓
Hiển thị:
- Session ID
- Thông tin cá nhân (age, weight, height)
- BMI & trạng thái (Gầy/Bình thường/Thừa cân)
- TDEE & lời khuyên
- Mục tiêu & mức độ hoạt động
- Lịch sử gợi ý sản phẩm
- Button "Chỉnh sửa"
```

---

## 📁 Các File Được Tạo / Sửa

### **Tạo Mới:**

| File | Nội Dung |
|------|---------|
| `products/forms.py` | 2 form: `UserProfileForm` (đầy đủ) + `QuickProfileForm` (ngắn) |
| `products/middleware.py` | Middleware tự động tạo UserProfile từ session |
| `templates/products/user_profile_setup.html` | Form setup đầy đủ (Bootstrap 5) |
| `templates/products/user_profile_quick_setup.html` | Form quick setup |
| `templates/products/user_profile_view.html` | Trang xem/chỉnh sửa profile |

### **Sửa Đổi:**

| File | Thay Đổi |
|------|----------|
| `products/views.py` | + 4 view hàm mới: `user_profile_setup`, `user_profile_quick_setup`, `user_profile_view`, 2 helper |
| `products/urls.py` | + 3 URL path cho setup pages |
| `fitblog_config/settings.py` | + `products.middleware.UserProfileMiddleware` vào MIDDLEWARE |
| `templates/base.html` | + Link " Hồ Sơ" vào navigation bar |

---

## 🔗 URLs Mới

| URL | Tên | Chức Năng |
|-----|-----|----------|
| `/products/setup/` | `user_profile_setup` | Setup đầy đủ |
| `/products/quick-setup/` | `user_profile_quick_setup` | Quick setup |
| `/products/profile/` | `user_profile_view` | Xem & chỉnh sửa profile |

---

## 📊 Dữ Liệu Flow

```
User Browser
    ↓
Django Session Middleware
    ↓ (tạo session_id)
UserProfileMiddleware
    ↓ (get_or_create UserProfile)
request.user_profile ← có sẵn trong mọi request
    ↓
Views (user_profile_setup, etc)
    ↓ (lấy data từ request.user_profile)
Form Handling
    ↓ (validate & save)
Database (UserProfile model)
    ↓ (calculate_bmi() & calculate_tdee())
Templates
    ↓ (render with user profile data)
HTML Response
    ↓
Browser
```

---

## 🎁 Tính Năng

### **1. Form Validation**

```python
# Age validation: 16-120
# Weight validation: 30-200 kg
# Height validation: 100-250 cm
# Auto-validate trong form

form = UserProfileForm(request.POST, instance=user_profile)
if form.is_valid():
    form.save()  # Tự động tính BMI & TDEE
```

### **2. Auto-Calculate BMI & TDEE**

```python
# Form.save() tự động gọi:
profile.calculate_bmi()      # BMI = weight / (height²)
profile.calculate_tdee()     # TDEE = BMR × Activity Factor
profile.save()
```

### **3. Session-Based (Không cần Login)**

```python
# Middleware tự động:
session_id = request.session.session_key
user_profile, created = UserProfile.objects.get_or_create(
    session_id=session_id
)
request.user_profile = user_profile
```

### **4. Track Recommendations**

```python
# Mỗi khi show gợi ý, log lại:
RecommendationLog.objects.create(
    user_profile=profile,
    recommended_product=product,
    clicked=True/False,
    purchased=True/False
)

# Xem lịch sử trong /products/profile/
```

---

## 🧪 Test

### **Test Setup Page**

```bash
curl http://localhost:8000/products/setup/
# Should return HTML form page
```

### **Test POST (Submit Form)**

```bash
curl -X POST http://localhost:8000/products/setup/ \
  -d "age=30&weight_kg=75&height_cm=175&goal=muscle-gain&activity_level=moderate"
```

### **Test Profile View**

```bash
curl http://localhost:8000/products/profile/
# Should show user profile with BMI, TDEE, etc
```

---

## 💡 Ví Dụ Thực Tế

### **User Flow 1: Setup lần đầu**

```
1. User vào http://localhost:8000/
   → Middleware tạo UserProfile (empty)
   
2. User click " Hồ Sơ" 
   → Redirect /products/profile/
   → Thấy "Chưa có thông tin"
   → Click "Thiết lập ngay"
   → Vào /products/setup/
   
3. User điền form:
   - Tuổi: 30
   - Cân: 75 kg
   - Cao: 175 cm
   - Mục tiêu: Tăng cơ
   - Vận động: Vừa phải (3-5h/tuần)
   
4. Click "Lưu Thông Tin"
   → Server tính:
      BMI = 75 / (1.75²) = 24.5
      TDEE = 1698 × 1.55 = 2631 kcal/ngày
   → Lưu vào database
   → Redirect /products/
   
5. User xem gợi ý sản phẩm
   → API endpoint /api/products/personalized/
   → Gợi ý base on goal=muscle-gain + TDEE=2631
```

### **User Flow 2: Quick setup từ modal**

```
1. User vào trang sản phẩm
   → Widget "Quick Setup" hiện lên
   
2. User điền nhanh 5 trường
   → Click "Xong!"
   
3. Save profile → Lấy gợi ý ngay
```

### **User Flow 3: Chỉnh sửa profile**

```
1. User vào /products/profile/
   → Xem profile hiện tại
   → Click "✏️ Chỉnh Sửa"
   
2. Form pre-filled với data cũ
   → Update values
   → Click "Lưu"
   → BMI & TDEE recalculated
```

---

## 🚨 Troubleshooting

### **Vấn đề: Form không submit**

```bash
# Check CSRF token
curl -c cookies.txt http://localhost:8000/products/setup/
# Copy CSRF token từ HTML
curl -b cookies.txt -X POST \
  -d "csrfmiddlewaretoken=XXX&age=30&..."
```

### **Vấn đề: Middleware không chạy**

```python
# Check settings.py MIDDLEWARE list
# Phải có: 'products.middleware.UserProfileMiddleware'
# Chạy lệnh:
python manage.py check
```

### **Vấn đề: Session không tạo**

```python
# Middleware tự động tạo nếu chưa có
# Nhưng cần SESSION_ENGINE trong settings.py
SESSION_ENGINE = 'django.contrib.sessions.backends.db'  # Default
```

---

## 📱 UI/UX Features

### **Setup Page Features:**

✅ Bootstrap 5 responsive design
✅ Color-coded input fields
✅ Real-time validation
✅ BMI/TDEE display (nếu có)
✅ Info box giải thích
✅ Back button

### **Profile Page Features:**

✅ Sidebar: profile info
✅ Main: recommendation history
✅ Info cards: BMI status, TDEE info
✅ Edit button
✅ Table: last 10 recommendations

---

## 🔄 Tích Hợp Với Recommendation

```python
# Khi user xem product detail:
GET /api/products/personalized/

# API tự động:
1. Lấy session_id từ request
2. Get UserProfile (via middleware có sẵn)
3. Filter products by user.goal
4. Return gợi ý phù hợp
5. Log vào RecommendationLog
```

---

## 📝 Tiếp Theo

1. ✅ User có thể setup profile → **DONE**
2. ✅ Auto-calculate BMI & TDEE → **DONE**
3. ✅ Session-based tracking → **DONE**
4. ⏳ **Sắp tới:** Implement real recommendations algorithm
5. ⏳ A/B testing framework
6. ⏳ Collaborative filtering

---

## 🎓 Key Concepts

| Concept | Chi Tiết |
|---------|---------|
| **Session** | Browser cookie lưu session_id, Django server track |
| **Middleware** | Chạy trước mỗi request, tạo UserProfile tự động |
| **Forms** | `UserProfileForm` validate input, `QuickProfileForm` ngắn |
| **Auto-Calculate** | `form.save()` → `calculate_bmi()` → `calculate_tdee()` |
| **Anonymous User** | Không cần login, dùng session_id thay thế |
| **Recommendation** | Dùng user.goal + TDEE để filter sản phẩm |

Bây giờ người dùng **không cần login**, chỉ cần:
1. Truy cập website
2. Click "Hồ Sơ" → "Setup"
3. Điền tuổi, cân, cao, mục tiêu
4. Lấy gợi ý sản phẩm

Simple & effective! 🚀
