# Fitblog - Fitness Product Recommendation System

## 📋 Tổng Quan Hệ Thống

Fitblog là một nền tảng thương mại điện tử chuyên biệt cho các sản phẩm fitness (whey protein, creatine, BCAA, v.v.) với hệ thống gợi ý sản phẩm dựa trên **hồ sơ người dùng** và **lịch sử xem sản phẩm**.

## 🎯 Tính Năng Chính

### 1. **Hồ Sơ Cá Nhân (User Profile)**
- Quản lý thông tin cá nhân: tuổi, cân nặng, chiều cao
- Tính toán **BMI** tự động
- Tính toán **TDEE** (Tổng năng lượng tiêu thụ hàng ngày)
- Lựa chọn mục tiêu fitness (Tăng Cơ, Giảm Cân, Tăng Sức Mạnh, v.v.)
- Chọn mức độ hoạt động (Sedentary, Light, Moderate, Active, Very Active)

### 2. **Danh Sách Sản Phẩm**
- Hiển thị **8 sản phẩm/trang** với phân trang
- Lọc theo danh mục, loại supplement, giá
- Tìm kiếm sản phẩm
- Sắp xếp: giá thấp→cao, giá cao→thấp, rating cao→thấp, mới nhất

### 3. **Chi Tiết Sản Phẩm**
- Thông tin dinh dưỡng (protein, carbs, fat, calories)
- Đánh giá và nhận xét từ khách hàng
- Hiển thị **5 sản phẩm tương tự** cùng danh mục (random)
- Gợi ý tự động dựa trên mục tiêu người dùng

### 4. **Hệ Thống Gợi Ý (Recommendations)**
- **Gợi ý cá nhân**: Dựa trên mục tiêu fitness của người dùng
- **Lịch sử xem**: Theo dõi tất cả sản phẩm đã xem
- **Tự động tracking**: Khi người dùng xem sản phẩm hoặc nhấp chuột

## 🏗️ Kiến Trúc Hệ Thống

```
Fitblog/
├── blog/                    # Blog posts & categories
├── chatbot/                 # Chatbot integration
├── products/                # Main product module
│   ├── models.py           # Product, Category, Review, UserProfile, RecommendationLog
│   ├── views.py            # Views for listing, detail, recommendations
│   ├── serializers.py      # DRF serializers
│   ├── urls.py             # Product URLs
│   └── middleware.py       # Session-based user profile middleware
├── fitblog_config/         # Django settings
├── templates/              # HTML templates
├── static/                 # CSS, JS
├── media/                  # User uploads (images)
└── docs/                   # Documentation
```

## 📊 Cơ Sở Dữ Liệu

### Models Chính

**1. Product**
- name, description, price, discount_percent
- image, supplement_type, category
- suitable_for_goals (JSON field)
- nutrition info (protein, carbs, fat, calories per serving)

**2. UserProfile**
- age, weight_kg, height_cm
- goal, activity_level
- tdee (calculated), bmi (calculated)
- session_id (for anonymous users)

**3. RecommendationLog**
- session_id, user_profile (FK)
- recommended_product (FK)
- recommendation_type ('personalized', 'content-based')
- clicked, purchased, created_at

**4. ProductReview**
- product (FK), author_name, author_email
- rating, title, content
- is_approved, is_verified_purchase
- created_at, helpful_count

## 🚀 Hướng Dẫn Sử Dụng

### Cho Người Dùng

#### 1. Thiết Lập Hồ Sơ
- Truy cập `/products/user-profile-setup/`
- Nhập thông tin cá nhân (tuổi, cân nặng, chiều cao)
- Chọn mục tiêu fitness
- Chọn mức độ hoạt động
- Hệ thống sẽ tính toán **BMI** và **TDEE** tự động

#### 2. Duyệt Sản Phẩm
- Truy cập `/products/` để xem danh sách
- Lọc theo danh mục, giá, loại supplement
- Tìm kiếm sản phẩm cụ thể
- Nhấp vào sản phẩm để xem chi tiết

#### 3. Xem Gợi Ý
- Truy cập `/products/user-profile/` để xem hồ sơ
- **"Gợi Ý Cho Bạn"**: Sản phẩm phù hợp với mục tiêu
- **"Lịch Sử Xem"**: Tất cả sản phẩm đã xem

### Cho Admin

#### 1. Quản Lý Sản Phẩm
```bash
python manage.py shell
from products.models import Product, ProductCategory

# Tạo danh mục
category = ProductCategory.objects.create(name="Whey Protein")

# Tạo sản phẩm
product = Product.objects.create(
    name="Whey Gold Standard",
    category=category,
    price=150000,
    protein_per_serving=24,
    suitable_for_goals=["muscle-gain", "strength"]
)
```

#### 2. Phê Duyệt Đánh Giá
- Truy cập Django Admin: `/admin/`
- Phê duyệt reviews từ ProductReview

#### 3. Xem Thống Kê
- Kiểm tra RecommendationLog để xem hành vi người dùng
- Phân tích sản phẩm nào được xem nhiều nhất

## 🛠️ Setup và Chạy

### 1. Cài Đặt Môi Trường
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# hoặc
venv\Scripts\activate  # Windows

pip install -r requirements.txt
```

### 2. Migrate Database
```bash
python manage.py makemigrations
python manage.py migrate
```

### 3. Tạo Super User
```bash
python manage.py createsuperuser
```

### 4. Chạy Server
```bash
python manage.py runserver
```

### 5. Truy Cập
- Trang chủ: http://127.0.0.1:8000/
- Sản phẩm: http://127.0.0.1:8000/products/
- Hồ sơ: http://127.0.0.1:8000/products/user-profile/
- Admin: http://127.0.0.1:8000/admin/

## 📱 API Endpoints

### Products
- `GET /api/products/` - Danh sách sản phẩm
- `GET /api/products/{id}/` - Chi tiết sản phẩm
- `GET /api/products/{id}/recommendations/` - Sản phẩm tương tự

### Recommendations
- `GET /api/products/personalized/` - Gợi ý cá nhân
- `POST /api/track-click/` - Theo dõi xem sản phẩm
- `POST /api/reviews/` - Gửi đánh giá

## 🎨 Giao Diện

### Trang Chính
- Header: Navigation menu, logo
- Hero section: Banner, search bar
- Danh sách sản phẩm với filter sidebar

### Chi Tiết Sản Phẩm
- Ảnh sản phẩm (sticky bên trái)
- Thông tin giá, mô tả
- Thông tin dinh dưỡng
- Đánh giá khách hàng
- Sản phẩm tương tự (carousel)

### Hồ Sơ Người Dùng
- Thông tin cơ bản (2 cột: tuổi, cân nặng | chiều cao, BMI)
- Thực trạng BMI (badge)
- Mục tiêu, mức độ hoạt động
- TDEE highlight
- Nút chỉnh sửa, reset, xóa
- Gợi ý sản phẩm (carousel 8 sản phẩm)
- Lịch sử xem (bảng)

## 📊 Phân Trang

- **Danh sách sản phẩm**: 8 sản phẩm/trang
- **Lịch sử xem**: 20 mục/trang
- **Gợi ý cá nhân**: 6 sản phẩm max

## 🔒 Bảo Mật

- Sử dụng session Django cho người dùng ẩn danh
- CSRF protection cho form submissions
- Input validation và sanitization
- Permission-based access control

## 📝 Tài Liệu Thêm

- [User Profile Setup Guide](docs/USER_PROFILE_SETUP_GUIDE.md)
- [Delete Profile Guide](docs/DELETE_PROFILE_GUIDE.md)
- [API Reference](docs/archived-md/API_REFERENCE.md)

## 🐛 Troubleshooting

### Lỗi: "Session not initialized"
- Hãy truy cập trang chủ `/` trước để khởi tạo session

### Lỗi: "Profile not found"
- Hãy tạo hồ sơ tại `/products/user-profile-setup/`

### Lỗi: "Database locked"
- Xóa file `db.sqlite3` và chạy migrations lại

## 👨‍💻 Phát Triển Thêm

### Tính Năng Được Lên Kế Hoạch
- [ ] Tích hợp thanh toán (Stripe/Momo)
- [ ] User authentication (Login/Register)
- [ ] Wishlist
- [ ] Product comparison
- [ ] Email notifications
- [ ] Mobile app
- [ ] AI-based recommendations

## 📞 Liên Hệ & Support

Nếu có vấn đề hoặc đóng góp, vui lòng tạo issue hoặc liên hệ admin.

---

**Version**: 1.0.0  
**Last Updated**: January 3, 2026  
**Author**: Development Team
