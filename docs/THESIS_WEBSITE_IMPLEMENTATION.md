# 🏋️ Fitblog - Thực Tế Triển Khai Website

> **Bản tóm tắt này được lập dựa trên code thực tế trong project, KHÔNG TỰ Ý VIẾT.**

---

## 📌 TỔNG QUAN HỆ THỐNG

**Fitblog** là một nền tảng **thương mại điện tử chuyên về sản phẩm fitness** với hệ thống gợi ý thông minh.

### Chức Năng Chính
1. **Lưu trữ & Hiển thị sản phẩm supplement** (Whey, Pre-workout, BCAA, Vitamins, etc.)
2. **Hệ thống đánh giá sản phẩm** từ người dùng
3. **Hệ thống gợi ý sản phẩm** (Content-based & Collaborative Filtering)
4. **Quản lý hồ sơ fitness người dùng** (Mục tiêu, chiều cao, cân nặng, BMI)
5. **Blog** để chia sẻ kiến thức fitness & dinh dưỡng
6. **Chatbot AI** (tùy chọn) để trả lời câu hỏi

---

## 🗄️ CẤU TRÚC DỮ LIỆU (MODELS)

Dựa trên `products/models.py`:

### 1. **ProductCategory Model**
- **Mục đích**: Phân loại supplement (Whey, Pre-workout, Vitamins, etc.)
- **Fields chính**:
  - `name`: Tên danh mục (vd: "Whey Protein")
  - `slug`: URL-friendly identifier (vd: "whey-protein")
  - `icon`: Ảnh icon danh mục
  - `color`: Hex color cho UI (vd: "#b39ddb")
  - `description`: Mô tả danh mục
- **Index**: slug (để search/filter nhanh)

### 2. **Product Model** (Chính)
- **Mục đích**: Lưu thông tin sản phẩm supplement
- **Fields thông tin cơ bản**:
  - `name`: Tên sản phẩm
  - `slug`: URL slug
  - `category`: Foreign Key → ProductCategory
  - `supplement_type`: Loại supplement (Whey Isolate, Pre-workout, etc.)
  - `status`: Trạng thái (active/inactive/outofstock)

- **Fields giá & khuyến mại**:
  - `price`: Giá (VND)
  - `discount_percent`: Phần trăm giảm giá

- **Fields thông tin dinh dưỡng** (per serving):
  - `serving_size`: Khẩu phần (vd: "30g")
  - `protein_per_serving`: Protein (g)
  - `carbs_per_serving`: Carbohydrates (g)
  - `fat_per_serving`: Fat (g)
  - `calories_per_serving`: Calories (kcal)

- **Fields mô tả**:
  - `description`: Mô tả chi tiết
  - `short_description`: Tóm tắt ngắn
  - `ingredients`: Thành phần
  - `flavor`: Hương vị
  - `image`: Hình ảnh chính

- **Metadata cho gợi ý**:
  - `suitable_for_goals`: Mục tiêu phù hợp (JSON hoặc text)
  - `embedding_vector`: Vector embedding cho recommendation (nếu có)

- **Quản lý**:
  - `created_at`: Ngày tạo
  - `rating_avg`: Trung bình đánh giá
  - `review_count`: Số lượt đánh giá

### 3. **ProductReview Model** (Quan trọng cho CF)
- **Mục đích**: Lưu đánh giá sản phẩm từ người dùng
- **Fields**:
  - `product`: Foreign Key → Product
  - `user`: Foreign Key → Django User (authenticated only)
  - `rating`: Rating 1-5 sao
  - `title`: Tiêu đề đánh giá
  - `content`: Nội dung đánh giá
  - `author_name`: Tên người đánh giá (anonymous users)
  - `author_email`: Email (anonymous users)
  - `is_approved`: Review đã duyệt hay chưa (moderator)
  - `helpful_count`: Số người tìm thấy hữu ích
  - `is_verified_purchase`: Đã mua sản phẩm này hay không (optional)
  - `created_at`: Ngày đánh giá

- **Constraint**: `UNIQUE(user_id, product_id)` - Mỗi user chỉ review 1 lần cho 1 product
- **Index**: `(product_id, rating)`, `(user_id, product_id)` để query nhanh

### 4. **UserProfile Model** (Dữ liệu Fitness)
- **Mục đích**: Lưu thông tin fitness & mục tiêu của người dùng
- **Fields**:
  - `user`: One-to-One → Django User
  - `age`: Tuổi
  - `weight_kg`: Cân nặng (kg)
  - `height_cm`: Chiều cao (cm)
  - `gender`: Giới tính (male/female/other)
  - `goal`: Mục tiêu fitness (muscle_gain, fat_loss, strength, etc.)
  - `activity_level`: Mức độ hoạt động (sedentary, light, moderate, active, very_active)
  - `bmi`: BMI (tính toán tự động)
  - `tdee`: TDEE - Tổng năng lượng tiêu thụ (calories/day)
  - `session_id`: Session ID cho anonymous users
  - `created_at` / `updated_at`

- **Auto-create**: Signal tự động tạo UserProfile khi User được tạo (trong `products/signals.py`)

### 5. **RecommendationLog Model** (Tracking)
- **Mục đích**: Ghi log mỗi recommendation để tracking
- **Fields**:
  - `user_profile`: Foreign Key → UserProfile
  - `product`: Foreign Key → Product
  - `algorithm_type`: Loại algorithm (content_based, collab_filtering, hybrid)
  - `predicted_rating`: Rating dự đoán (float)
  - `score`: Điểm tương đồng/relevance (0-1)
  - `created_at`

### 6. **EventLog Model** (User Interaction Tracking)
- **Mục đích**: Ghi log MỌI tương tác người dùng (views, clicks, reviews, purchases, etc.)
- **Cấu trúc**:
  - `user_profile`: Foreign Key → UserProfile (user who triggered event)
  - `product`: Foreign Key → Product (related product, optional)
  - `event_type`: Loại event (CharField with choices)
  - `metadata`: JSON field (flexible context data)
  - `timestamp`: Ngày/giờ tự động

- **Event Types**:
  ```
  • product_view    - User viewed product detail
  • product_click   - User clicked product
  • review_submit   - User submitted review
  • review_helpful  - Review marked helpful
  • rec_shown       - Recommendation shown to user
  • rec_clicked     - User clicked recommendation
  • rec_purchased   - User bought recommended product
  • search          - Search performed
  • filter_apply    - Filter applied
  • login/logout    - Auth events
  • profile_setup   - User setup fitness profile
  • profile_update  - Profile updated
  ```

- **Design**: Lightweight, no UNIQUE constraint (allow duplicates for comprehensive history)

### 7. **PasswordResetToken Model** (Auth)
- **Mục đích**: Xác minh đặt lại mật khẩu
- **Fields**:
  - `user`: Foreign Key → Django User
  - `token`: Token ngẫu nhiên unique
  - `created_at`
  - `expires_at`: Hết hạn (thường 24h)
  - `is_used`: Đã dùng hay chưa

---

## 🎯 FEATURES (TÍNH NĂNG THỰC TẾ)

Dựa trên `products/views.py`:

### 1. **ProductViewSet (REST API)**
```python
# Base: GET /api/products/
```
- **Endpoints**:
  - `GET /api/products/` - List sản phẩm (filter, search, paginate)
  - `GET /api/products/{id}/` - Chi tiết sản phẩm
  - `GET /api/products/{id}/recommendations/` - Gợi ý based on product
  - `GET /api/products/personalized/` - Gợi ý cá nhân (auth users)
  - `GET /api/products/categories/` - Danh sách danh mục

- **Features**:
  - **Filtering**: Theo category, supplement_type, price, status
  - **Search**: Tìm kiếm trong name, description, ingredients
  - **Sorting**: Theo price, created_at, rating
  - **Pagination**: Mặc định 8-10 items/page
  - **Caching**: Cache 5 phút cho categories
  - **Rate limiting**: 100 req/h cho anonymous, 200 req/h cho authenticated

- **Content-Based Recommendations** (logic trong `recommendations()` action):
  ```python
  # Query: Sản phẩm cùng danh mục OR cùng loại OR cùng mục tiêu
  recommendations = Product.objects.filter(
      Q(category=product.category) |
      Q(supplement_type=product.supplement_type) |
      Q(suitable_for_goals__icontains=product.suitable_for_goals)
  )[:limit]
  ```

- **Personalized Recommendations** (logic trong `personalized()` action):
  ```python
  # Chỉ cho authenticated users
  # Lấy user_profile, filter sản phẩm theo fitness goal
  ```

### 2. **Authentication Views** (từ `auth_views.py`)
- **Register**: `/auth/register/`
  - Validate email/username unique
  - Auto-create UserProfile (via signal)
  - Auto-login sau khi register
  - Redirect to profile setup

- **Login**: `/auth/login/`
  - Login với username hoặc email
  - "Remember me" checkbox
  - Rate limiting: 5 attempts/15 minutes
  - Redirect to next page

- **Password Reset**: `/auth/password_reset/`
  - Send email với token
  - Verify token (24h expiry)
  - Update password

### 3. **Các Views Frontend HTML** (từ `templates/products/`)
- `product_list.html` - Danh sách sản phẩm (filter, pagination)
- `product_detail.html` - Chi tiết sản phẩm (reviews, recommendations)
- `user_profile_setup.html` - Setup hồ sơ fitness
- `user_profile_view.html` - Xem hồ sơ & lịch sử xem
- `user_profile_edit.html` - Chỉnh sửa hồ sơ

---

## 🧠 HỆ THỐNG GỢI Ý (RECOMMENDATION SYSTEM)

Dựa trên `products/recommendation_service.py`:

### 1. **UserItemMatrix**
- **Xây dựng từ**: ProductReview table (authenticated users only)
- **Cấu trúc**: 
  ```
  rows = user_ids
  cols = product_ids
  values = ratings (1-5) hoặc 0 (chưa review)
  ```
- **Ví dụ**:
  ```
           Prod1  Prod2  Prod3
  User1      5      3      -
  User2      4      -      5
  User3      -      2      4
  ```

### 2. **CollaborativeFilteringEngine**
- **Algorithm**: User-based Collaborative Filtering
- **Steps**:
  1. Tìm K users tương tự (default K=5)
  2. Tính cosine similarity giữa user vectors
  3. Xem những product mà similar users rate cao
  4. Predict rating của target user
  5. Recommend top N products

- **Code**:
  ```python
  engine = CollaborativeFilteringEngine(k_neighbors=5)
  recommendations = engine.recommend(user_id, limit=5)
  ```

### 3. **HybridRecommendationEngine**
- **Kết hợp**:
  - Content-based (same category/goals)
  - Collaborative filtering (similar users)
  - Personalized (user's fitness goal)
- **Weight**: Tuỳ chỉnh trọng số của từng algorithm

---

## 🔐 AUTHENTICATION & SECURITY

Dựa trên `products/auth_views.py` & `products/middleware.py`:

### Features:
1. **Django built-in authentication** (Django User model)
2. **Rate limiting** cho login (5 attempts/15 min)
3. **Password reset via email**
4. **Session-based UserProfile** (middleware auto-create)
5. **CSRF protection** (Django middleware)
6. **Password validation** (strength check)
7. **Email validation** (unique check)

---

## 📝 BLOG MODULE

Dựa trên `blog/models.py`:

### Models:
1. **Category** (Blog categories)
   - `name`, `slug`, `description`
   - `icon_image`: Uploaded icon
   - `color`: Hex color

2. **Post** (Blog posts)
   - `title`, `slug`, `content`
   - `category`: Foreign Key → Category
   - `author`: Tác giả
   - `excerpt`: Tóm tắt
   - `featured_image`: Ảnh nổi bật
   - `tags`: Tags (comma-separated)
   - `status`: draft/published
   - `views`: Số lượt xem
   - `published_at`: Ngày xuất bản

---

## 💬 CHATBOT MODULE

Dựa trên `chatbot/models.py`:

### Models:
1. **NgrokConfig** (Cấu hình API)
   - `ngrok_api_url`: URL Ngrok LLM API
   - `is_active`: Kích hoạt hay không
   - `name`, `description`

2. **ChatMessage** (Lịch sử chat - optional)
   - `user_message`: Tin nhắn từ user
   - `bot_response`: Phản hồi từ bot
   - `created_at`: Timestamp

---

## ⚙️ CẤU HÌNH DJANGO

Dựa trên `fitblog_config/settings.py`:

### Installed Apps:
```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',        # DRF
    'corsheaders',          # CORS
    'django_filters',       # Filtering
    'cloudinary_storage',   # Image storage
    'cloudinary',           # Image CDN
    'blog',
    'chatbot',
    'products',
]
```

### Middleware:
```python
MIDDLEWARE = [
    'whitenoise.middleware.WhiteNoiseMiddleware',     # Static files
    'corsheaders.middleware.CorsMiddleware',          # CORS
    'products.middleware.UserProfileMiddleware',      # Auto-create UserProfile
]
```

### REST Framework Config:
```python
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 8,
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'product_list': '100/hour',
        'product_detail': '200/hour',
        'login': '5/15min',
    }
}
```

### Database:
- **Development**: SQLite3 (db.sqlite3)
- **Production** (Railway): PostgreSQL (via DATABASE_URL)

---

## 🚀 DEPLOYMENT

Dựa trên `Dockerfile`, `Procfile`, `runtime.txt`:

### Stack:
- **Python**: 3.11 (runtime.txt)
- **Framework**: Django 4.x
- **Server**: Gunicorn (production)
- **Database**: PostgreSQL (Railway)
- **Image Storage**: Cloudinary
- **Deployment**: Railway.app

### Procfile:
```
web: gunicorn fitblog_config.wsgi
```

### Docker:
- Build Python image
- Install dependencies (requirements.txt)
- Collect static files
- Run Gunicorn

---

## 📊 URL ROUTING

Dựa trên `fitblog_config/urls.py`:

```python
urlpatterns = [
    path('admin/', admin.site.urls),          # Django admin
    path('', include('blog.urls')),            # Blog (home, posts, etc.)
    path('chatbot/', include('chatbot.urls')), # Chatbot
    path('', include('products.urls')),        # Products + Auth
]
```

### Products URLs:
- `/products/` - Danh sách sản phẩm
- `/products/{slug}/` - Chi tiết sản phẩm
- `/api/products/` - REST API
- `/auth/register/` - Đăng kí
- `/auth/login/` - Đăng nhập

---

## 🎨 FRONTEND STRUCTURE

```
templates/
├── base.html              # Base template (navigation, footer)
├── auth/
│   ├── login.html
│   ├── register.html
│   ├── password_reset_request.html
│   └── password_reset_confirm.html
├── products/
│   ├── product_list.html
│   ├── product_detail.html
│   ├── user_profile_setup.html
│   ├── user_profile_view.html
│   └── user_profile_edit.html
├── blog/
│   ├── home.html
│   ├── post_list.html
│   ├── post_detail.html
│   └── categories.html
└── admin/
    └── (Django admin templates)

static/
├── css/
│   ├── style.css
│   ├── product_detail.css
│   └── ...
├── js/
│   ├── header.js
│   └── ...
└── img/
    └── (Static images)
```

---

## 📦 DEPENDENCIES (requirements.txt)

**Main packages**:
- `Django` - Web framework
- `djangorestframework` - REST API
- `django-filters` - Filtering
- `django-cors-headers` - CORS
- `Pillow` - Image processing
- `python-decouple` - .env config
- `dj-database-url` - Database URL parsing
- `gunicorn` - Production server
- `cloudinary` - Image CDN
- `whitenoise` - Static files
- `numpy` - Matrix operations (recommendation)
- `scikit-learn` (optional) - ML algorithms

---

## ✅ SUMMARY

| Khía Cạnh | Chi Tiết |
|-----------|---------|
| **Framework** | Django 4.x + DRF |
| **Database** | SQLite3 (dev) / PostgreSQL (prod) |
| **Models** | 6 chính (Product, Category, Review, UserProfile, RecommendationLog, PasswordResetToken) |
| **API** | REST API với filtering, search, pagination |
| **Recommendation** | Content-based + Collaborative Filtering |
| **Auth** | Django auth + email password reset |
| **Frontend** | Django templates + Bootstrap |
| **Deployment** | Railway.app (Docker) |
| **Features** | Product catalog, user reviews, recommendations, blog, chatbot |

