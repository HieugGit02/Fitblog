# 🏋️ Fitblog - Fitness Product Recommendation System

**Nền tảng thương mại điện tử chuyên về sản phẩm fitness với hệ thống gợi ý thông minh dựa trên hồ sơ người dùng.**

---

## 📚 Tài Liệu Đầy Đủ

👉 **[Tài Liệu Chi Tiết](docs/README.md)** - Hướng dẫn hoàn chỉnh về hệ thống

### Hướng Dẫn Nhanh
- [User Profile Setup Guide](docs/USER_PROFILE_SETUP_GUIDE.md)
- [Delete Profile Guide](docs/DELETE_PROFILE_GUIDE.md)

---

## 🚀 Khởi Động Nhanh

```bash
# 1. Cài đặt dependencies
pip install -r requirements.txt

# 2. Migrate database
python manage.py migrate

# 3. Tạo super user
python manage.py createsuperuser

# 4. Chạy server
python manage.py runserver
```

**Truy cập**: http://127.0.0.1:8000/

---

## ✨ Tính Năng Chính

✅ **Hồ Sơ Cá Nhân** - Thông tin user, BMI, TDEE  
✅ **Danh Sách Sản Phẩm** - 8 sản phẩm/trang, lọc & tìm kiếm  
✅ **Gợi Ý Thông Minh** - Dựa trên mục tiêu fitness  
✅ **Lịch Sử Xem** - Theo dõi sản phẩm đã xem  
✅ **Đánh Giá Khách Hàng** - Reviews & ratings  
✅ **Admin Dashboard** - Quản lý sản phẩm & duyệt reviews  

---

## 📁 Cấu Trúc Dự Án

```
Fitblog/
├── docs/                    # 📚 Tài liệu
├── products/                # 📦 Module sản phẩm
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   └── middleware.py
├── blog/                    # 📝 Module blog
├── templates/               # 🎨 HTML templates
├── static/                  # 🎯 CSS, JavaScript
├── media/                   # 📷 Ảnh & media
└── fitblog_config/          # ⚙️ Django settings
```

---

## 🎨 Giao Diện Chính

- **Trang Chủ** - Navigation menu, search bar
- **Danh Sách Sản Phẩm** - Grid 8 items/page, filters, pagination
- **Chi Tiết Sản Phẩm** - Thông tin, reviews, 5 sản phẩm tương tự
- **Hồ Sơ Người Dùng** - Thông tin, BMI status, gợi ý, lịch sử xem

---

## 📊 Database

**Models Chính**:
- **Product** - Sản phẩm, category, supplement type, nutrition info
- **UserProfile** - Hồ sơ user (age, weight, height, goal, activity level)
- **RecommendationLog** - Lịch sử xem & gợi ý
- **ProductReview** - Đánh giá khách hàng

---

## 🔗 API Endpoints

- `GET /api/products/` - Danh sách sản phẩm
- `GET /api/products/{id}/` - Chi tiết sản phẩm
- `GET /api/products/personalized/` - Gợi ý cá nhân
- `POST /api/track-click/` - Theo dõi xem

---

## 📝 Version

**v1.0.0** | Last Updated: January 3, 2026

---

**Xem [docs/README.md](docs/README.md) để biết thêm chi tiết** 📖
