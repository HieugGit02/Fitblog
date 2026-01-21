# 📁 FITBLOG PROJECT STRUCTURE - Giải Thích Chi Tiết

## 🎯 Tổng Quan Dự Án

**Fitblog** là một nền tảng thương mại điện tử kết hợp blog về fitness, dinh dưỡng và công nghệ. Cho phép users xem sản phẩm supplement, đọc bài viết, để lại đánh giá, và nhận được gợi ý cá nhân hóa.

---

## 📂 CẤU TRÚC THƯMỤC CHÍNH

### 1. **ROOT LEVEL FILES** (Tệp cấp cao nhất)

```
├── manage.py                 ⚙️ Django management script
├── requirements.txt          📦 Python dependencies
├── db.sqlite3               🗄️ Local database (development only)
├── Dockerfile               🐳 Docker configuration for Railway
├── Procfile                 🚀 Heroku/Railway deployment config
├── runtime.txt              🔢 Python version specification
├── setup_railway.sh         🔧 Railway deployment script
├── run_migrations.sh        📝 Database migration runner
└── .gitignore              🚫 Git ignore patterns
```

**Mục đích:**
- `manage.py`: Chạy lệnh Django (migrate, runserver, shell, etc.)
- `requirements.txt`: Quản lý dependencies (Django, DRF, Pillow, sklearn, etc.)
- `Dockerfile`: Build Docker image cho Railway deployment
- `Procfile`: Định nghĩa cách chạy app trên Railway
- `setup_railway.sh`: Script khởi tạo Railway database

---

## 📦 MAIN APP DIRECTORIES

### 2. **fitblog_config/** - Django Project Settings

```
fitblog_config/
├── __init__.py
├── settings.py              🎛️ Project configuration
│   ├── Installed apps (blog, products, chatbot)
│   ├── Database settings
│   ├── Static/Media files
│   ├── Authentication backends
│   └── CORS & Security settings
├── urls.py                  🔗 Root URL routing
│   └── Include URLs from blog/, products/, chatbot/
├── wsgi.py                  🌐 WSGI application entry point
└── __pycache__/
```

**Mục đích:**
- Tất cả cấu hình chung của Django project
- Quản lý installed apps, middleware, static files
- Cài đặt database, email, cache

---

### 3. **products/** - Ecommerce & User Management Module

```
products/
├── models.py                📊 Database models
│   ├── Product              (id, name, price, description, status)
│   ├── ProductCategory      (name, icon, color, slug)
│   ├── ProductFlavor        (name, grams)
│   ├── ProductReview        (rating, content, author_name, helpful_count)
│   ├── UserProfile          (user, goal, fitness_level, gender, session_id)
│   ├── RecommendationLog    (user_profile, product, type, score)
│   └── PasswordResetToken   (token, user, created_at, expires_at)
│
├── views.py                 👁️ Main views
│   ├── product_list()       (Pagination, filters, AJAX)
│   ├── product_detail()     (Reviews, recommendations)
│   ├── user_profile_view()  (User dashboard, history)
│   ├── track_product_click()
│   └── mark_review_helpful()
│
├── urls.py                  🔗 URL routing
├── forms.py                 📝 User input forms
├── auth_views.py            🔐 Authentication views
│   ├── Register user
│   ├── Login/Logout
│   ├── Password reset
│   └── Profile update
├── auth_forms.py            📋 Auth form classes
├── auth_throttle.py         ⏱️ Rate limiting for auth
├── admin.py                 🛠️ Django admin config
├── admin_user.py            👤 User admin customization
├── apps.py                  ⚙️ App configuration
├── models.py                📊 Database models
├── middleware.py            🔄 Custom middleware
├── recommendation_service.py 🧠 ML-based recommendations
├── signals.py               📡 Django signals (post_save, etc.)
├── serializers.py           📤 DRF serializers
├── tests.py                 ✅ Unit tests
├── templatetags/
│   └── product_filters.py   🏷️ Custom template filters
├── management/
│   └── commands/            🎯 (Development-only commands removed)
├── migrations/              📝 Database migrations
├── __pycache__/
└── __init__.py
```

**Mục đích:**
- **Models**: Định nghĩa cấu trúc dữ liệu (Product, Review, User, Recommendation)
- **Views**: Xử lý logic (product listing, user dashboard, recommendations)
- **Auth**: User registration, login, password reset
- **Recommendation**: Gợi ý sản phẩm dựa trên mục tiêu fitness
- **Admin**: Tùy chỉnh Django admin dashboard

---

### 4. **blog/** - Blog Management Module

```
blog/
├── models.py                📊 Blog models
│   ├── Category             (name, slug, icon, color, description)
│   └── Post                 (title, slug, content, category, status, published_at)
│
├── views.py                 👁️ Blog views
│   ├── HomeView()           (Home page with featured posts)
│   ├── PostListView()       (All posts listing)
│   ├── PostDetailView()     (Single post detail)
│   ├── CategoryDetailView() (Posts by category)
│   └── CategoriesView()     (All categories overview)
│
├── urls.py                  🔗 Blog URL routing
├── admin.py                 🛠️ Blog admin config
├── apps.py                  ⚙️ App configuration
├── logging_handlers.py      📝 Custom logging
├── tests.py                 ✅ Blog tests
├── views_categories.py      👁️ Category-specific views
├── migrations/              📝 Blog migrations
├── __pycache__/
└── __init__.py
```

**Mục đích:**
- **Models**: Post và Category cho blog
- **Views**: Trang home, danh sách bài, chi tiết bài, danh mục
- **Admin**: Quản lý bài viết trong Django admin

---

### 5. **chatbot/** - Chatbot Module (Optional)

```
chatbot/
├── models.py                💬 Chat message model
├── views.py                 👁️ Chatbot endpoints
├── urls.py                  🔗 Chatbot routes
├── admin.py                 🛠️ Admin config
├── apps.py                  ⚙️ App configuration
├── migrations/              📝 Chatbot migrations
└── __init__.py
```

**Mục đích:**
- Chatbot messaging system (prep cho tương lai)

---

### 6. **templates/** - HTML Templates

```
templates/
├── base.html                🏠 Base template (navigation, footer)
│
├── auth/                    🔐 Authentication pages
│   ├── login.html           (Login form với password toggle 👁️)
│   ├── register.html        (User registration)
│   ├── logout_confirm.html  (Confirm logout)
│   ├── password_reset_request.html
│   └── password_reset_confirm.html
│
├── blog/                    📝 Blog pages
│   ├── home.html            (Home page)
│   ├── post_list.html       (All posts)
│   ├── post_detail.html     (Single post)
│   ├── categories.html      (All categories overview)
│   └── subscribe_message.html
│
├── products/                🛍️ Product pages
│   ├── product_list.html    (Products with filters, pagination)
│   ├── product_detail.html  (Product detail, reviews, recommendations)
│   ├── user_profile_view.html (User dashboard, viewing history)
│   ├── _product_list_partial.html (AJAX-loaded product grid)
│   ├── _pagination_partial.html   (Pagination UI)
│   └── admin/
│       └── dashboard.html   (Admin dashboard)
```

**Mục đích:**
- Tất cả HTML pages của ứng dụng
- `_partial.html`: Partial templates cho AJAX loading (không reload page)
- `base.html`: Template chung để inherit

---

### 7. **static/** - Static Assets

```
static/
├── css/
│   ├── styles.css           🎨 Main styles (layout, colors)
│   ├── products.css         🛍️ Product page styles
│   ├── product_detail.css   📄 Product detail page styles
│   │   ├── Reviews section styling
│   │   ├── Collapsible reviews (view more functionality)
│   │   ├── Recommendations grid
│   │   └── Responsive design
│   └── header.js            (Legacy, can be removed)
│
├── js/
│   ├── header.js            (Navigation interactions)
│   ├── messenger.js         (Chat/messaging)
│   └── (Inline scripts in templates for AJAX)
│
└── img/                      📸 Images
```

**Mục đích:**
- CSS: Styling website (mint green + coral theme)
- JS: Interactivity (AJAX, filtering, pagination)
- Img: Static images

---

### 8. **docs/** - Documentation

```
docs/
├── PROJECT_STRUCTURE.md     📋 This file!
├── DATABASE_SCHEMA.md       🗄️ Database schema documentation
├── PROJECT_ARCHITECTURE.md  🏗️ System architecture
├── README.md                📖 Project overview
├── USER_PROFILE_SETUP_GUIDE.md
├── DELETE_PROFILE_GUIDE.md
├── diagram/
│   └── db_schema_1_erd.erd.json (ERD diagram)
└── DATABASE_SCHEMA_FOR_THESIS.md
```

**Mục đích:**
- Tài liệu và hướng dẫn dự án
- Schema database
- Architecture diagrams

---

## 🗄️ DATABASE MODELS (Mối Quan Hệ)

### Products App

```
ProductCategory (Danh mục sản phẩm)
├─ id, name, icon, color, slug, description
├─ has_many: Product
└─ has_many: ProductFlavor

Product (Sản phẩm)
├─ id, name, price, description, status, created_at
├─ belongs_to: ProductCategory
├─ has_many: ProductReview
├─ has_many: ProductFlavor
├─ has_many: RecommendationLog
└─ metadata: suitable_for_goals, supplement_type

ProductReview (Đánh giá)
├─ id, rating, title, content, author_name, author_email
├─ belongs_to: Product
├─ is_verified_purchase: Boolean
└─ helpful_count: Integer

UserProfile (Hồ sơ người dùng)
├─ id, user_id, goal, fitness_level, gender, session_id
├─ belongs_to: User
└─ has_many: RecommendationLog

RecommendationLog (Ghi nhật ký gợi ý)
├─ id, user_profile_id, product_id
├─ belongs_to: UserProfile
├─ belongs_to: Product
├─ type: 'personalized', 'popular', 'trending'
├─ score: Float (0-1)
└─ clicked: Boolean

PasswordResetToken (Token reset password)
├─ id, token, user_id, expires_at
└─ belongs_to: User
```

### Blog App

```
Category (Danh mục bài viết)
├─ id, name, slug, icon, color, description
└─ has_many: Post

Post (Bài viết)
├─ id, title, slug, content, excerpt, featured_image
├─ belongs_to: Category
├─ status: 'draft', 'published'
├─ published_at: DateTime
├─ views: Integer
├─ author: String
└─ tags: String (comma-separated)
```

---

## 🔄 KEY FEATURES IMPLEMENTATION

### ✨ Features Implemented

| Feature | Files | Mô Tả |
|---------|-------|-------|
| **Product Listing** | `products/views.py`, `product_list.html` | Lọc theo danh mục, sắp xếp, phân trang (8 items/page) |
| **Product Detail** | `product_detail.html`, `product_detail.css` | Chi tiết sản phẩm, đánh giá (collapsible), gợi ý |
| **User Authentication** | `auth_views.py`, `login.html` | Đăng nhập (password toggle 👁️), đăng ký, reset password |
| **User Dashboard** | `user_profile_view.html` | Lịch sử xem (5 items/page), gợi ý cá nhân |
| **Reviews System** | `ProductReview` model, `product_detail.html` | Đánh giá sản phẩm (3 initial + view more) |
| **Recommendation** | `recommendation_service.py` | Gợi ý dựa trên mục tiêu fitness của user |
| **Blog System** | `blog/` app | Bài viết, danh mục, trang chủ |
| **AJAX Pagination** | `product_list.html` JS | Phân trang không reload page |
| **Responsive Design** | `products.css`, `product_detail.css` | Mobile-first, breakpoints 768px/1024px |

---

## 🚀 DEPLOYMENT CONFIGURATION

```
Railway Deployment Files:
├── Dockerfile           (Build Docker image)
├── Procfile            (Run command: python manage.py runserver 0.0.0.0:8000)
├── runtime.txt         (Python 3.12)
├── requirements.txt    (Dependencies)
└── setup_railway.sh    (Initialization script)
```

**Quy trình:**
1. Push to GitHub
2. Railway tự động build Docker image
3. Chạy migrations
4. Deploy app

---

## 📊 KEY DEPENDENCIES

```python
# Core
Django==4.2
djangorestframework  # REST API

# Frontend
Pillow               # Image processing
django-cors-headers # CORS support

# ML & Analytics
scikit-learn         # Recommendation algorithm
numpy                # Numerical computing

# Utilities
python-decouple      # Environment variables
gunicorn             # Production server
```

---

## 🎯 USER WORKFLOW

```
┌─────────────┐
│  Home Page  │
└──────┬──────┘
       │
       ├─→ 📝 Blog (Read articles)
       │   └─→ Categories view
       │
       ├─→ 🛍️ Products (Browse)
       │   ├─→ Filter by category
       │   ├─→ Sort by price/rating
       │   ├─→ Pagination (8 items)
       │   └─→ View product detail
       │       ├─→ See reviews (3 + view more)
       │       ├─→ Leave review
       │       └─→ See recommendations
       │
       └─→ 👤 User Profile (if logged in)
           ├─→ Viewing history (5 items/page)
           ├─→ Personal recommendations
           ├─→ Update profile
           └─→ Logout
```

---

## 📝 CÁCH SỬ DỤNG TỪng FILE

### Thêm sản phẩm mới
```bash
# Django admin
python manage.py runserver
# Vào /admin → Products → Add Product
```

### Thêm bài viết mới
```bash
# Django admin
# Vào /admin → Blog → Posts → Add Post
```

### Chạy server locally
```bash
python manage.py runserver 8000
```

### Deploy to Railway
```bash
git push github main
# Railway auto-deploys from GitHub
```

---

## 🔐 SECURITY FEATURES

- ✅ CSRF protection ({% csrf_token %})
- ✅ Password hashing (Django default)
- ✅ Rate limiting on auth endpoints
- ✅ SQL injection prevention (Django ORM)
- ✅ CORS configured
- ✅ Environment variables (.env)

---

## 📈 PERFORMANCE OPTIMIZATIONS

- ✅ Database query optimization (select_related, prefetch_related)
- ✅ Pagination (8 items/page)
- ✅ AJAX loading (no full page reload)
- ✅ Collapsible sections (reviews, recommendations)
- ✅ Static files minified
- ✅ Lazy loading images

---

## 🧪 TESTING

```bash
# Run tests
python manage.py test

# Run specific app tests
python manage.py test products
python manage.py test blog
```

Test files:
- `products/tests.py`
- `blog/tests.py`

---

**Cuối cùng:** Dự án này là một **full-stack ecommerce + blog platform** được tối ưu cho **performance**, **user experience**, và **deployment**. 🚀

