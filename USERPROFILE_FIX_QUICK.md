# 🔧 QUICK FIX SUMMARY: UserProfile Bị Tách Đôi

## 🎯 Vấn Đề
Khi user đăng kí, trong `/admin/products/userprofile/` thay vì hiển thị **1 profile** → lại hiển thị **2 profiles**:
- ✅ 1 cái liên kết với User
- ❌ 1 cái orphaned (không user, chỉ có session_id)

---

## ✅ Giải Pháp - 3 Bước

### 1. ✅ Đã Fix Signal (products/signals.py)
```python
# ❌ Cũ: Tạo được duplicate nếu signal chạy 2 lần
UserProfile.objects.create(user=instance, goal='general-health')

# ✅ Mới: Chỉ tạo 1 duy nhất
profile, was_created = UserProfile.objects.get_or_create(
    user=instance,
    defaults={'goal': 'general-health'}
)
```

### 2. ✅ Đã Xóa 5 Orphaned Profiles Cũ
```bash
$ python manage.py shell -c "
from products.models import UserProfile
orphaned = UserProfile.objects.filter(user__isnull=True)
orphaned.delete()  # Xóa 5 cái
"
```

### 3. ✅ Tạo Management Command Cleanup
```bash
# Dọn dẹp orphaned profiles cũ (> 7 ngày)
$ python manage.py cleanup_orphaned_profiles

# Dọn dẹp tất cả
$ python manage.py cleanup_orphaned_profiles --keep-days 0 --force
```

---

## ✅ Kết Quả
```
✅ Total users: 4
✅ Total profiles: 4 (1:1 mapping - hoàn hảo!)
✅ No orphaned profiles found!
```

---

## 📝 Các File Đã Sửa

| File | Thay Đổi |
|------|----------|
| `products/signals.py` | ✅ Sửa - dùng `get_or_create` |
| `products/management/commands/cleanup_orphaned_profiles.py` | ✅ Thêm - tool dọn dẹp |
| `docs/USERPROFILE_DUPLICATE_FIX.md` | ✅ Thêm - tài liệu chi tiết |

---

## 🧪 Test Ngay

1. **Kiểm tra admin panel**:
   - Truy cập: `http://localhost:8000/admin/products/userprofile/`
   - Mỗi user chỉ có **1 profile duy nhất** ✅

2. **Tạo user mới để test**:
   - Đăng kí user mới qua `http://localhost:8000/auth/register/`
   - Kiểm tra admin → chỉ có 1 profile được tạo ✅

3. **Monitor định kỳ**:
   - Chạy: `python manage.py cleanup_orphaned_profiles --keep-days 30`
   - Để dọn dẹp các profile cũ tích tụ

---

## 📚 Tài Liệu Chi Tiết
Xem: `docs/USERPROFILE_DUPLICATE_FIX.md`
