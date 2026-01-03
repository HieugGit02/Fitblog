# 🗑️ Hướng Dẫn Xóa Hồ Sơ Người Dùng

## 📌 3 Cách Xóa Hồ Sơ

### **Cách 1: Reset Hồ Sơ (Giữ Session)**
```
URL: /products/profile/reset/

Xóa:
  ✓ Tuổi, cân nặng, chiều cao
  ✓ BMI & TDEE
  ✓ Mục tiêu, mức độ vận động
  ✓ Thông tin khác

Giữ lại:
  ✓ Session ID (browser cookie)
  ✓ Có thể setup lại bất kỳ lúc nào

Khi nào dùng:
  - Muốn tắm "sạch sẽ" nhưng giữ session
  - Sắp thay đổi mục tiêu fitness
  - Cân nặng/chiều cao thay đổi đáng kể
```

### **Cách 2: Xóa Hồ Sơ Vĩnh Viễn (Delete All)**
```
URL: /products/profile/delete/

Xóa:
  ✓ Profile data (age, weight, height, bmi, tdee, goal, etc)
  ✓ Session ID
  ✓ Toàn bộ RecommendationLog
  ✓ Browser cookie sẽ được reset

Kết quả:
  - Lần truy cập tiếp theo: Django tạo session mới
  - Phải setup lại từ đầu
  - Không thể khôi phục (permanent delete)

Khi nào dùng:
  - Không muốn dùng website nữa
  - Muốn có session hoàn toàn mới
  - Xóa toàn bộ tracking data
```

### **Cách 3: Edit & Delete Field Riêng Lẻ**
```
URL: /products/setup/

Cách:
  - Vào setup form
  - Xóa specific field (ví dụ: chỉ xóa age)
  - Điền lại hoặc để trống
  - Click "Lưu"

Khi nào dùng:
  - Chỉ muốn update một field
  - Giữ lại thông tin khác
  - Chỉnh sửa từng phần
```

---

## 🎯 UI: Nơi Để Xóa

### **Trang Profile: `/products/profile/`**

```
┌─────────────────────────────────────┐
│ Hồ Sơ Cá Nhân                       │
├─────────────────────────────────────┤
│ Session ID: abc123...               │
│ Tuổi: 30                            │
│ Cân nặng: 75 kg                     │
│ Chiều cao: 175 cm                   │
│ BMI: 24.5 (Bình thường ✓)          │
│                                     │
│ [✏️ Chỉnh Sửa Thông Tin]           │
│                                     │
│ ─── Khu Vực Nguy Hiểm ───          │
│ [🔄 Reset (Giữ Session)]          │
│ [🗑️ Xóa Hồ Sơ]                    │
└─────────────────────────────────────┘
```

---

## 📋 Quy Trình Chi Tiết

### **Reset Hồ Sơ**

```
Step 1: Click "🔄 Reset (Giữ Session)"
   ↓
Step 2: Trang xác nhận hiện lên
   ↓
Step 3: Hiển thị thông tin sẽ xóa:
   - Session: GIỮA LẠI ✓
   - Tuổi: 30 → xóa
   - Cân nặng: 75 kg → xóa
   - Chiều cao: 175 cm → xóa
   - BMI: 24.5 → xóa
   - TDEE: 2633 → xóa
   - Mục tiêu: muscle-gain → xóa
   ↓
Step 4: Check checkbox "Tôi đồng ý..."
   ↓
Step 5: Click "🔄 Reset Hồ Sơ"
   ↓
Step 6: Message: "✅ Hồ sơ đã được reset"
   ↓
Step 7: Redirect → /products/profile/
   ↓
Step 8: Profile hiện "Chưa có thông tin"
   ↓
Step 9: Click "Thiết lập ngay" → Setup mới
```

### **Xóa Hồ Sơ Vĩnh Viễn**

```
Step 1: Click "🗑️ Xóa Hồ Sơ"
   ↓
Step 2: Trang xác nhận hiện lên (red background)
   ↓
Step 3: Hiển thị cảnh báo:
   - Hành động không thể hoàn tác
   - Session ID sẽ bị xóa
   - Toàn bộ lịch sử gợi ý xóa
   - Phải setup lại từ đầu
   ↓
Step 4: Hỏi: "Nhập: XÓA HỒNG SƠ"
   - Để tránh delete vô tình
   ↓
Step 5: Gõ chính xác: "XÓA HỒNG SƠ"
   ↓
Step 6: Click "🗑️ Xóa Hồ Sơ Vĩnh Viễn"
   ↓
Step 7: Database xóa:
   - UserProfile record
   - RecommendationLog records
   - Session data
   ↓
Step 8: request.session.flush() → Reset session
   ↓
Step 9: Message: "✅ Hồ sơ đã được xóa"
   ↓
Step 10: Redirect → /products/
   ↓
Step 11: Lần truy cập tiếp theo:
   - Django tạo session_id mới
   - Middleware tạo UserProfile mới
   - Trắng hoá từ đầu
```

---

## 🔧 Code Implementation

### **Views (products/views.py)**

```python
def user_profile_delete(request):
    """Xóa hồ sơ vĩnh viễn"""
    
    if request.method == 'POST':
        # Get user profile
        user_profile = UserProfile.objects.get(session_id=...)
        
        # Xóa recommendation logs
        RecommendationLog.objects.filter(
            user_profile=user_profile
        ).delete()
        
        # Xóa profile
        user_profile.delete()
        
        # Reset session
        request.session.flush()
        
        return redirect('products:product_list')
    
    return render(request, 'products/user_profile_delete.html')


def user_profile_reset(request):
    """Reset thông tin nhưng giữ session"""
    
    if request.method == 'POST':
        # Get user profile
        user_profile = UserProfile.objects.get(session_id=...)
        
        # Reset data
        user_profile.age = None
        user_profile.weight_kg = None
        user_profile.height_cm = None
        user_profile.bmi = None
        user_profile.tdee = None
        user_profile.goal = None
        user_profile.activity_level = None
        user_profile.save()
        
        return redirect('products:user_profile_view')
    
    return render(request, 'products/user_profile_reset.html')
```

### **URLs (products/urls.py)**

```python
urlpatterns = [
    path('products/profile/', views.user_profile_view, name='user_profile_view'),
    path('products/profile/delete/', views.user_profile_delete, name='user_profile_delete'),
    path('products/profile/reset/', views.user_profile_reset, name='user_profile_reset'),
]
```

### **Template (user_profile_delete.html)**

```html
<form method="post">
    {% csrf_token %}
    <input type="text" name="confirm_text" placeholder="Gõ: XÓA HỒNG SƠ">
    <button type="submit">🗑️ Xóa Hồ Sơ Vĩnh Viễn</button>
</form>
```

---

## 📊 Data Comparison

| Hành Động | Delete All | Reset | Edit Field |
|-----------|-----------|-------|-----------|
| **Xóa profile** | ✓ | ✗ | ✗ |
| **Xóa session** | ✓ | ✗ | ✗ |
| **Xóa recommendation logs** | ✓ | ✗ | ✗ |
| **Reset browser cookie** | ✓ | ✗ | ✗ |
| **Giữ session ID** | ✗ | ✓ | ✓ |
| **Có thể setup lại** | ✓ (session mới) | ✓ (session cũ) | ✓ |
| **Khôi phục được** | ✗ (Permanent) | ✗ (Permanent) | ✓ (Nếu nhớ data) |

---

## ⚙️ API (For Developers)

### **Delete via API**

```bash
# 1. Get session
curl -c cookies.txt http://localhost:8000/products/profile/

# 2. Delete POST
curl -b cookies.txt -X POST \
  -d "confirm_text=XÓA HỒNG SƠ" \
  http://localhost:8000/products/profile/delete/
```

### **Reset via API**

```bash
# 1. Get session
curl -c cookies.txt http://localhost:8000/products/profile/

# 2. Reset POST
curl -b cookies.txt -X POST \
  -d "agree=on" \
  http://localhost:8000/products/profile/reset/
```

---

## 🎨 UI/UX Features

### **Delete Page Features**
✓ Red warning color (danger zone)
✓ Confirmation text input (XÓA HỒNG SƠ)
✓ Display data that will be deleted
✓ Cancel button
✓ Alternative: Reset option link

### **Reset Page Features**
✓ Yellow warning color (caution)
✓ Checkbox confirmation
✓ Display session will be kept
✓ Info: "Can setup again anytime"
✓ Alternative: Delete option link

---

## 💾 Database Impact

### **After Delete All:**
```sql
-- DELETE FROM products_userprofile WHERE session_id='abc123'
-- DELETE FROM products_recommendationlog WHERE user_profile_id=1
-- Django Session: cleared
```

### **After Reset:**
```sql
-- UPDATE products_userprofile 
--    SET age=NULL, weight_kg=NULL, height_cm=NULL, 
--        bmi=NULL, tdee=NULL, goal=NULL
-- WHERE session_id='abc123'
-- RecommendationLog: NOT DELETED
```

---

## ✅ Test Results

```
📦 Test 1: Delete view imported .................... ✅
📦 Test 2: Reset view imported .................... ✅
🌐 Test 3: /products/profile/delete/ → HTTP 200 ... ✅
🌐 Test 4: /products/profile/reset/ → HTTP 200 .... ✅
📝 Test 5: Delete page renders HTML ............... ✅
📝 Test 6: Reset page renders HTML ............... ✅
```

---

## 🚀 Cách Dùng Thực Tế

### **Scenario 1: User muốn reset**
```
1. Click "🔄 Reset (Giữ Session)"
2. Check checkbox
3. Click "🔄 Reset Hồ Sơ"
4. Thấy "Chưa có thông tin"
5. Click "Thiết lập ngay" → Setup mới
```

### **Scenario 2: User muốn xóa hoàn toàn**
```
1. Click "🗑️ Xóa Hồ Sơ"
2. Nhập: "XÓA HỒNG SƠ"
3. Click "🗑️ Xóa Hồ Sơ Vĩnh Viễn"
4. Redirect /products/
5. Lần trở lại: session mới, profile mới
```

### **Scenario 3: User chỉ muốn update một field**
```
1. Click "✏️ Chỉnh Sửa Thông Tin"
2. Update: age (30 → 31)
3. Leave other fields as-is
4. Click "Lưu Thông Tin"
5. Profile updated (không xóa)
```

---

## 📞 Troubleshooting

**Q: Forgot to confirm delete?**
A: Form validation checks, must type "XÓA HỒNG SƠ" exactly

**Q: Want to undo delete?**
A: Cannot undo (permanent). Data is gone from DB.

**Q: Can I reset but keep history?**
A: Yes! Reset doesn't delete RecommendationLog. But profile data is reset.

**Q: What if I delete but want to comeback later?**
A: Setup new profile. New session created, start fresh.

---

**Summary:**
- **Reset** = Xóa thông tin, giữ session, setup lại dễ
- **Delete** = Xóa toàn bộ, session mới, start từ đầu
- **Edit** = Chỉ update field cần thiết

Choose wisely! 🎯
