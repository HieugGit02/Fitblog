# 👥 User Management - Tách Admin & Customer

## 📋 Tổng Quan

Hệ thống Fitblog hiện đã tách biệt rõ ràng giữa:
- **👨‍💼 Admin Users** - Quản trị viên, toàn bộ quyền
- **👤 Customer Users** - Khách hàng thường, quyền giới hạn

---

## 🏗️ Cấu Trúc Hiện Tại

### Database Structure

```
Django User (auth.User)
├── Groups
│   ├── 👨‍💼 Admin (52 permissions)
│   └── 👤 Customer (3 permissions)
└── is_staff / is_superuser
    ├── True → Admin Group
    └── False → Customer Group
```

### User Separation

```
Database User (django.contrib.auth.models.User)
├── 1 table: auth_user
├── All users stored together
├── Separated by 'groups' field
└── Managed via Django Groups & Permissions
```

**Lợi ích:**
- ✅ Không cần migrate data
- ✅ Dùng Django built-in
- ✅ Dễ scale sau này
- ✅ Flexible permissions

---

## 🔐 Permissions

### Admin Group (52 permissions)
```python
# All permissions từ apps: products, blog, chatbot
- add_*, change_*, delete_*, view_* cho tất cả models
```

### Customer Group (3 permissions)
```python
- view_product
- view_productcategory
- view_productreview
```

---

## 💾 User Lookup

### Check User Type

```python
# In views/models
from django.contrib.auth.models import User

user = User.objects.get(username='john')

# Check if admin
is_admin = user.groups.filter(name='Admin').exists()

# Check if customer  
is_customer = user.groups.filter(name='Customer').exists()

# Better way: use decorator
from django.contrib.auth.decorators import permission_required

@permission_required('products.view_product')
def product_view(request):
    # Only customers & admins with this permission
    pass
```

### Admin Panel

```python
# Filter by user type in admin
admin_users = User.objects.filter(groups__name='Admin')
customer_users = User.objects.filter(groups__name='Customer')
```

### In Templates

```django
{% if user.groups.all|dictsort:"name"|join:"," == "Admin" %}
    <div>Admin Dashboard</div>
{% elif user.groups.all|dictsort:"name"|join:"," == "Customer" %}
    <div>Customer Portal</div>
{% endif %}
```

---

## 🛠️ Management

### Add New Admin User (via Django Admin)

1. Tạo user mới
2. Đánh dấu `is_staff = True` hoặc `is_superuser = True`
3. Save → Tự động được assign vào `Admin` group

### Add New Customer User

1. Tạo user mới (via signup form hoặc admin)
2. **Không** đánh dấu `is_staff`
3. Save → Tự động được assign vào `Customer` group

### Change User Type

```python
# Convert Customer → Admin
from django.contrib.auth.models import Group

user = User.objects.get(username='john')
user.is_staff = True
user.save()
# auto assign to Admin group via admin.save_model

# Convert Admin → Customer
user.is_staff = False
user.is_superuser = False
user.save()
# auto assign to Customer group via admin.save_model
```

---

## 📊 Verify Setup

```bash
# Check groups
python manage.py shell
```

```python
from django.contrib.auth.models import User, Group

# See all groups
groups = Group.objects.all()
for g in groups:
    print(f"{g.name}: {g.permissions.count()} perms")

# See user groups
user = User.objects.get(username='admin')
print(user.groups.all())

# Check current state
admin_users = User.objects.filter(groups__name='Admin')
customer_users = User.objects.filter(groups__name='Customer')
print(f"Admin: {admin_users.count()}, Customer: {customer_users.count()}")
```

---

## 🔄 Migration Path (If you want Custom User later)

Nếu sau này cần full `CustomUser` model (ví dụ: thêm `phone`, `avatar`, v.v.):

1. Tạo `CustomUser` model (AbstractUser)
2. Tạo migration: `python manage.py makemigrations`
3. Django tự động migrate data từ auth.User → CustomUser
4. Update `AUTH_USER_MODEL = 'products.CustomUser'`

**Nhưng hiện tại, dùng Groups là đủ!**

---

## 📝 Files

| File | Mục đích |
|------|---------|
| `setup_user_groups.py` | Tạo groups & assign users |
| `products/admin_user.py` | Custom User Admin |
| `products/admin.py` | Import UserAdmin |

---

## ✅ Checklist

- ✅ Groups tạo thành công
- ✅ Users assigned đúng group
- ✅ Admin panel có User Type filter
- ✅ Permissions set up
- ✅ Database data không bị thay đổi
- ✅ Không cần migrate dữ liệu

---

## 🎯 Next Steps

1. **Update Views** - Thêm `@permission_required` decorator nơi cần
2. **Update Templates** - Show/hide nội dung based on `user.groups`
3. **API Auth** - Restrict API endpoints by group
4. **Admin Separation** - Create separate admin URLs cho admin vs customer (optional)

---

## 📚 Useful Commands

```bash
# Create superuser
python manage.py createsuperuser

# Run setup
python manage.py shell < setup_user_groups.py

# Check admin
http://localhost:8000/admin/auth/user/
# Filter by "User Type"
```

---

## 🎉 Summary

Người dùng đã được tách biệt rõ ràng:
- **Database**: Lưu chung 1 bảng (auth_user)
- **Groups**: Tách riêng via Django Groups
- **Permissions**: Admin có full quyền, Customer có quyền giới hạn
- **Migration**: Không cần, dùng built-in Django features
