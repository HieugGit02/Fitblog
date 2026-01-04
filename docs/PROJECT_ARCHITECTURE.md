# 📋 Fitblog - Kiến Trúc Dự Án Chi Tiết

**Cập nhật: 4 tháng 1, 2026**

---

## 📑 Mục Lục

1. [Tổng Quan Dự Án](#tổng-quan-dự-án)
2. [Kiến Trúc Hệ Thống](#kiến-trúc-hệ-thống)
3. [Cấu Trúc Thư Mục](#cấu-trúc-thư-mục)
4. [Database Models](#database-models)
5. [API Endpoints](#api-endpoints)
6. [Frontend Views](#frontend-views)
7. [Hệ Thống Gợi Ý (Recommendation)](#hệ-thống-gợi-ý-recommendation)
8. [Authentication & Sessions](#authentication--sessions)
9. [Tối Ưu Hóa Performance](#tối-ưu-hóa-performance)
10. [Deployment](#deployment)

---

## 🎯 Tổng Quan Dự Án

**Fitblog** là một **nền tảng thương mại điện tử chuyên biệt về sản phẩm fitness/supplement** với:

- ✅ **Hệ thống gợi ý cá nhân hóa** (Personalized Recommendation System)
- ✅ **Hồ sơ người dùng tự động** dựa trên Session (không cần đăng nhập)
- ✅ **Danh sách sản phẩm thông minh** với lọc, tìm kiếm, phân trang
- ✅ **Hệ thống đánh giá** (Reviews & Ratings)
- ✅ **Admin Dashboard** để quản lý sản phẩm
- ✅ **Blog** với danh mục bài viết về dinh dưỡng, thể hình

### 📊 Thống Kê Dự Án

| Metric | Giá Trị |
|--------|--------|
| **Backend** | Django 4.2.7 |
| **Frontend** | Django Templates + HTML/CSS/JS |
| **Database** | SQLite (local) / PostgreSQL (Railway) |
| **API** | Django REST Framework |
| **Modules** | 4 (products, blog, chatbot, fitblog_config) |
| **Models** | 8+ (Product, UserProfile, Review, Category, Post, etc.) |
| **API Endpoints** | 15+ endpoints |

---

## 🏗️ Kiến Trúc Hệ Thống

```
┌─────────────────────────────────────────────────────────────┐
│                    FRONT END (HTML/CSS/JS)                   │
│  - Templates: base.html, product_list.html, user_profile.html│
│  - Static: CSS (styles.css), JS (header.js, messenger.js)   │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                  DJANGO VIEWS & VIEWSETS                     │
│  - products/views.py (ProductViewSet, ProductCategoryViewSet)│
│  - blog/views.py (BlogViewSet)                              │
│  - products/views_categories.py (CategoryDetailView)        │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                     REST API LAYER                           │
│  - ProductSerializer, ProductDetailSerializer              │
│  - ProductReviewSerializer, ProductCategorySerializer      │
│  - Filtering, Searching, Pagination, Throttling            │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    BUSINESS LOGIC                            │
│  - Recommendation Engine (content-based)                     │
│  - User Profile Middleware                                  │
│  - Review Management                                        │
│  - Product Filtering & Search                               │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                  ORM MODELS (Django Models)                  │
│  - Product, ProductCategory, ProductReview, ProductFlavor   │
│  - UserProfile, RecommendationLog                           │
│  - Post, Category (Blog)                                    │
│  - SystemLog (Logging)                                      │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                   DATABASE LAYER                             │
│  - SQLite (development): /Fitblog/db.sqlite3               │
│  - PostgreSQL (production on Railway)                       │
└─────────────────────────────────────────────────────────────┘
```

---

## 📁 Cấu Trúc Thư Mục

```
Fitblog/
│
├── 📚 DOCUMENTATION
│   ├── docs/
│   │   ├── README.md                          # 👈 Start here
│   │   ├── PROJECT_ARCHITECTURE.md            # 👈 This file
│   │   ├── USER_PROFILE_SETUP_GUIDE.md
│   │   ├── DELETE_PROFILE_GUIDE.md
│   │   └── archived-md/                       # Archived docs
│   │
│   ├── README.md                              # Main readme
│   ├── README.backup.md
│   └── .env.example                           # Environment template
│
├── 🔧 CONFIGURATION
│   ├── manage.py                              # Django CLI
│   ├── requirements.txt                       # Dependencies
│   ├── runtime.txt                            # Python version (Railway)
│   ├── Procfile                               # Process definition (Railway)
│   ├── Dockerfile                             # Docker config
│   │
│   └── fitblog_config/                        # Django config
│       ├── __init__.py
│       ├── settings.py                        # ⚙️ MAIN CONFIG
│       ├── urls.py                            # URL routing
│       └── wsgi.py                            # WSGI entry point
│
├── 🛒 PRODUCTS APP (Main Feature)
│   ├── models.py                              # 📊 Product, UserProfile, Review models
│   ├── views.py                               # 🎯 ProductViewSet, recommendation logic
│   ├── views_categories.py                    # Category views
│   ├── serializers.py                         # DRF serializers
│   ├── urls.py                                # API routes
│   ├── forms.py                               # Django forms (UserProfile)
│   ├── admin.py                               # Admin panel config
│   ├── apps.py
│   ├── middleware.py                          # UserProfileMiddleware
│   ├── tests.py                               # Unit tests
│   │
│   ├── management/
│   │   └── __init__.py
│   │
│   ├── migrations/
│   │   ├── 0001_initial.py
│   │   ├── 0002_alter_productcategory_icon.py
│   │   ├── 0003_productflavor.py
│   │   └── 0004_userprofile_gender.py
│   │
│   └── templatetags/
│       ├── __init__.py
│       └── product_filters.py                 # Custom template filters
│
├── 📝 BLOG APP
│   ├── models.py                              # Post, Category models
│   ├── views.py                               # Blog views
│   ├── urls.py
│   ├── serializers.py
│   ├── admin.py
│   ├── apps.py
│   ├── logging_handlers.py                    # Custom logging
│   ├── tests.py
│   │
│   ├── migrations/
│   │   ├── 0001_initial.py
│   │   ├── 0002_category_icon_image.py
│   │   └── 0003_alter_category_icon_alter_category_icon_image.py
│   │
│   └── __init__.py
│
├── 🤖 CHATBOT APP
│   ├── models.py                              # Chat models
│   ├── views.py
│   ├── urls.py
│   ├── admin.py
│   ├── apps.py
│   ├── migrations/
│   └── __init__.py
│
├── 🎨 FRONTEND (Templates & Static)
│   ├── templates/
│   │   ├── base.html                          # Base template
│   │   │
│   │   ├── products/                          # Product templates
│   │   │   ├── product_list.html              # Product listing page
│   │   │   ├── product_detail.html            # Product detail page
│   │   │   ├── _product_list_partial.html     # Reusable product item
│   │   │   ├── _pagination_partial.html       # Pagination
│   │   │   ├── user_profile_setup.html        # Profile setup form
│   │   │   ├── user_profile_quick_setup.html  # Quick setup
│   │   │   ├── user_profile_view.html         # Profile view
│   │   │   ├── user_profile_reset.html        # Profile reset
│   │   │   └── user_profile_delete.html       # Profile delete
│   │   │
│   │   └── blog/                              # Blog templates
│   │       ├── home.html
│   │       ├── post_list.html
│   │       ├── post_detail.html
│   │       ├── categories.html
│   │       └── subscribe_message.html
│   │
│   ├── static/
│   │   ├── css/
│   │   │   ├── styles.css                     # Main stylesheet
│   │   │   ├── products.css                   # Product styles
│   │   │   └── product_detail.css             # Detail page styles
│   │   │
│   │   ├── js/
│   │   │   ├── header.js                      # Header interactions
│   │   │   └── messenger.js                   # Chat interactions
│   │   │
│   │   └── img/                               # Images
│   │
│   └── media/                                 # Uploaded files
│       ├── product_images/                    # Product images
│       └── category_icons/                    # Category icons
│
├── 🚀 DEPLOYMENT & SCRIPTS
│   ├── setup_railway.sh                       # Railway setup
│   ├── run_migrations.sh                      # Migration script
│   ├── cleanup_script.py                      # Cleanup utility
│   │
│   └── .gitignore
│   └── .env                                   # Environment variables
│
└── 🗄️ DATABASE
    └── db.sqlite3                             # Local SQLite database
```

---

## 📊 Database Models

### 1️⃣ **Product Model** (Sản Phẩm)

```python
class Product(models.Model):
    # ========== BASIC INFO ==========
    name: CharField(255)
    slug: SlugField (unique)
    category: ForeignKey(ProductCategory)
    supplement_type: CharField (whey, isolate, bcaa, preworkout, ...)
    
    # ========== DESCRIPTION ==========
    description: TextField
    short_description: CharField(300)
    image: ImageField
    
    # ========== PRICING ==========
    price: DecimalField (VND)
    discount_percent: IntegerField (0-100)
    
    # ========== NUTRITION INFO (Per serving) ==========
    serving_size: CharField (e.g., "30g")
    protein_per_serving: FloatField
    carbs_per_serving: FloatField
    fat_per_serving: FloatField
    calories_per_serving: FloatField
    
    # ========== INGREDIENTS & DETAILS ==========
    ingredients: TextField
    flavor: CharField
    
    # ========== MANAGEMENT ==========
    status: CharField (active, inactive, outofstock)
    stock: IntegerField
    
    # ========== RECOMMENDATION METADATA ==========
    tags: CharField (e.g., "muscle-gain,lean,vegan")
    suitable_for_goals: CharField (e.g., "muscle-gain,fat-loss")
    embedding_vector: JSONField (for future ML)
    
    # ========== TIMESTAMPS ==========
    created_at: DateTimeField (auto_now_add)
    updated_at: DateTimeField (auto_now)
    
    # ========== SEO ==========
    seo_title: CharField
    seo_description: CharField
    
    # ========== METHODS ==========
    get_discounted_price() -> float
    get_average_rating() -> float
    get_review_count() -> int
    get_tags_list() -> list
    get_goals_list() -> list
```

**Indexes**: slug, status, supplement_type, -created_at

---

### 2️⃣ **ProductCategory Model** (Danh Mục)

```python
class ProductCategory(models.Model):
    name: CharField(100, unique)
    slug: SlugField (unique)
    description: TextField
    icon: ImageField (PNG, JPG)
    color: CharField (Hex color, e.g., "#b39ddb")
    created_at: DateTimeField
    
    # ========== METHODS ==========
    get_absolute_url() -> str
```

---

### 3️⃣ **ProductReview Model** (Đánh Giá)

```python
class ProductReview(models.Model):
    product: ForeignKey(Product)
    author_name: CharField(100)
    rating: IntegerField (1-5)
    title: CharField(255)
    content: TextField
    
    helpful_count: IntegerField (default=0)
    is_approved: BooleanField (default=False)
    
    created_at: DateTimeField
    updated_at: DateTimeField
    
    # ========== METHODS ==========
    get_rating_stars() -> str (⭐ formatting)
```

---

### 4️⃣ **UserProfile Model** (Hồ Sơ Người Dùng)

```python
class UserProfile(models.Model):
    # ========== SESSION-BASED (không cần login) ==========
    session_id: CharField (unique)
    
    # ========== PERSONAL INFO ==========
    age: IntegerField (18-100)
    gender: CharField (male, female, other)
    weight_kg: FloatField (kg)
    height_cm: IntegerField (cm)
    
    # ========== FITNESS INFO ==========
    goal: CharField (muscle_gain, fat_loss, strength, general_fitness)
    activity_level: CharField (sedentary, light, moderate, active, very_active)
    dietary_restrictions: CharField (vegan, gluten_free, lactose_free, etc.)
    
    # ========== CALCULATED FIELDS ==========
    bmi: FloatField (auto-calculated)
    bmi_status: CharField (underweight, normal, overweight, obese)
    tdee: IntegerField (Total Daily Energy Expenditure)
    
    # ========== TIMESTAMPS ==========
    created_at: DateTimeField
    updated_at: DateTimeField
    
    # ========== METHODS ==========
    calculate_bmi() -> float
    calculate_tdee() -> int
    get_recommendations() -> QuerySet (Product)
```

---

### 5️⃣ **RecommendationLog Model** (Lịch Sử Gợi Ý)

```python
class RecommendationLog(models.Model):
    user_profile: ForeignKey(UserProfile)
    recommended_product: ForeignKey(Product)
    
    recommendation_type: CharField (content_based, personalized, trending)
    score: FloatField (0-1.0, confidence score)
    reason: CharField (explanation)
    
    created_at: DateTimeField
    
    # ========== METHODS ==========
    __str__() -> str (formatted log)
```

---

### 6️⃣ **ProductFlavor Model** (Phiên Bản Sản Phẩm)

```python
class ProductFlavor(models.Model):
    product: ForeignKey(Product)
    flavor_name: CharField (e.g., "Chocolate", "Vanilla")
    stock: IntegerField
    added_date: DateTimeField
```

---

### 7️⃣ **Post Model** (Bài Viết Blog)

```python
class Post(models.Model):
    title: CharField(200)
    slug: SlugField(unique)
    category: ForeignKey(Category)
    author: CharField(100)
    content: TextField (HTML/Markdown)
    excerpt: CharField(500)
    featured_image: ImageField
    
    status: CharField (draft, published)
    views: IntegerField (default=0)
    
    created_at: DateTimeField
    updated_at: DateTimeField
    published_at: DateTimeField (nullable)
    
    # ========== METHODS ==========
    get_absolute_url() -> str
    increment_views() -> None
```

---

### 8️⃣ **SystemLog Model** (Logging)

```python
class SystemLog(models.Model):
    log_type: CharField (info, warning, error)
    message: CharField
    details: JSONField
    ip_address: CharField
    created_at: DateTimeField
```

---

## 🔌 API Endpoints

### 📦 **Products API**

| Method | Endpoint | Description | Authentication |
|--------|----------|-------------|-----------------|
| GET | `/api/products/` | List all active products (filtered) | ❌ Public |
| GET | `/api/products/?category=whey` | Filter by category | ❌ Public |
| GET | `/api/products/?search=protein` | Search products | ❌ Public |
| GET | `/api/products/?ordering=-price` | Sort by price | ❌ Public |
| GET | `/api/products/{id}/` | Get product details | ❌ Public |
| GET | `/api/products/{id}/recommendations/` | Content-based recommendations | ❌ Public |
| GET | `/api/products/personalized/` | Personalized recommendations (session-based) | ❌ Session |
| GET | `/api/products/categories/` | List all categories | ❌ Public |

---

### ⭐ **Product Review API**

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/reviews/` | List approved reviews |
| GET | `/api/reviews/?product=1` | Reviews for product |
| POST | `/api/reviews/` | Create new review |
| POST | `/api/reviews/{id}/mark_helpful/` | Mark review as helpful |

---

### 👤 **User Profile API/Views**

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/products/setup/` | Show profile setup form |
| POST | `/products/setup/` | Save profile info |
| GET | `/products/quick-setup/` | Quick setup page |
| GET | `/products/profile/` | View user profile |
| GET | `/products/profile/reset/` | Reset profile page |
| GET | `/products/profile/delete/` | Delete profile page |

---

### 📝 **Blog API**

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/blog/posts/` | List blog posts |
| GET | `/api/blog/posts/{id}/` | Get post details |
| GET | `/api/blog/categories/` | List categories |
| GET | `/blog/` | Home page |
| GET | `/blog/categories/` | All categories |
| GET | `/blog/{slug}/` | Category details |

---

### 🔧 **Admin API**

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/admin/` | Django admin panel |
| GET | `/admin/products/product/` | Manage products |
| GET | `/admin/products/userprofile/` | Manage user profiles |
| GET | `/admin/products/productreview/` | Review management |

---

## 🎨 Frontend Views

### **Product List Page** (`/products/`)

```
┌─────────────────────────────────────────┐
│            HEADER & NAVIGATION           │
│  - Logo, Search bar, User menu           │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│         FILTERS & SEARCH SECTION         │
│  - Category filter                       │
│  - Supplement type filter                │
│  - Price range slider                    │
│  - Search textbox                        │
│  - Sort options                          │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│      PRODUCT GRID (8 items per page)     │
│  ┌──────┐  ┌──────┐  ┌──────┐  ┌──────┐ │
│  │ Item │  │ Item │  │ Item │  │ Item │ │
│  └──────┘  └──────┘  └──────┘  └──────┘ │
│  ┌──────┐  ┌──────┐  ┌──────┐  ┌──────┐ │
│  │ Item │  │ Item │  │ Item │  │ Item │ │
│  └──────┘  └──────┘  └──────┘  └──────┘ │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│         PAGINATION CONTROLS              │
│  < 1  2  3  4  5 >                       │
└─────────────────────────────────────────┘
```

**Template**: `products/product_list.html`

**Context**:
- `products`: Paginated product list
- `categories`: All categories
- `filters`: Current filter values
- `search_query`: Current search term
- `total_count`: Total products found

---

### **Product Detail Page** (`/products/{slug}/`)

```
┌─────────────────────────────────────────┐
│      PRODUCT IMAGE & BASIC INFO          │
│  - Large product image                   │
│  - Price & discount                      │
│  - Stock status                          │
│  - Add to cart button                    │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│       NUTRITION INFORMATION               │
│  - Protein, Carbs, Fat per serving      │
│  - Calories                              │
│  - Serving size                          │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│      PRODUCT DESCRIPTION & DETAILS       │
│  - Full description                      │
│  - Ingredients list                      │
│  - Flavor options                        │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│         CUSTOMER REVIEWS SECTION         │
│  - Average rating (⭐)                    │
│  - Review count                          │
│  - List of approved reviews              │
│  - "Add review" form                     │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│    SIMILAR PRODUCTS (5 recommendations)  │
│  Based on: category, supplement type    │
└─────────────────────────────────────────┘
```

**Template**: `products/product_detail.html`

**Context**:
- `product`: Product instance
- `reviews`: Approved reviews
- `avg_rating`: Average rating
- `recommendations`: Similar products

---

### **User Profile Setup Page** (`/products/setup/`)

**Features**:
- 📋 Form to collect user info (age, weight, height, goal, activity level)
- 🧮 Auto-calculate BMI & TDEE
- 💾 Save to UserProfile (session-based)
- 🎯 Redirect to product list after setup

**Form Fields**:
```
- Age: IntegerField (18-100)
- Gender: ChoiceField (male, female, other)
- Weight (kg): DecimalField
- Height (cm): IntegerField
- Goal: ChoiceField (muscle_gain, fat_loss, strength, general_fitness)
- Activity Level: ChoiceField (sedentary, light, moderate, active, very_active)
- Dietary Restrictions: CharField (optional, comma-separated)
```

---

## 🧠 Hệ Thống Gợi Ý (Recommendation)

### **🔹 Content-Based Recommendation**

**Location**: `ProductViewSet.recommendations()` method

**Logic**:
```python
# Get products with similar characteristics:
recommendations = Product.objects.filter(
    Q(category=product.category) |                    # Same category
    Q(supplement_type=product.supplement_type) |      # Same supplement type
    Q(suitable_for_goals__icontains=product.suitable_for_goals)  # Same goals
).exclude(id=product.id)

# Sort by rating & popularity
recommendations.order_by('-review_count', '-avg_rating')[:limit]
```

**Endpoint**: `GET /api/products/{id}/recommendations/?limit=5`

**Response**:
```json
{
  "count": 5,
  "current_product": { /* product data */ },
  "recommendations": [ /* similar products */ ],
  "reason": "Content-based: Similar category, supplement type, or fitness goals"
}
```

---

### **🔹 Personalized Recommendation (Session-Based)**

**Location**: `ProductViewSet.personalized()` method

**Logic**:
```python
# 1. Get or create UserProfile from session_id
user_profile, created = UserProfile.objects.get_or_create(
    session_id=request.session.session_key,
    defaults={'goal': goal or 'general_fitness'}
)

# 2. Filter products by user's goal
query = Q(status='active')
query &= Q(suitable_for_goals__icontains=user_profile.goal)

# 3. Exclude dietary restrictions
if user_profile.dietary_restrictions:
    for restriction in restrictions:
        query &= ~Q(suitable_for_goals__icontains=restriction)

# 4. Sort by rating & popularity
recommendations = Product.objects.filter(query)\
    .annotate(avg_rating=Avg('reviews__rating'))\
    .order_by('-review_count', '-avg_rating')[:limit]

# 5. Log recommendation
RecommendationLog.objects.bulk_create([
    RecommendationLog(
        user_profile=user_profile,
        recommended_product=product,
        recommendation_type='personalized',
        reason=f'Personalized for goal: {goal}'
    ) for product in recommendations
])
```

**Endpoint**: `GET /api/products/personalized/?goal=muscle_gain&limit=5`

**Response**:
```json
{
  "count": 5,
  "user_profile": {
    "session_id": "abc123",
    "goal": "muscle_gain",
    "dietary_restrictions": ""
  },
  "recommendations": [ /* personalized products */ ],
  "reason": "Personalized recommendations for goal: muscle_gain"
}
```

---

### **🔹 Recommendation Log Tracking**

**Purpose**: Track recommendation history for analytics & future ML improvements

**Model**:
```python
class RecommendationLog(models.Model):
    user_profile: ForeignKey(UserProfile)
    recommended_product: ForeignKey(Product)
    recommendation_type: CharField (content_based, personalized, trending)
    score: FloatField (confidence score)
    reason: CharField (explanation)
    created_at: DateTimeField
```

**Data Collection Points**:
- When user views product details
- When personalized recommendations are generated
- When similar products are shown

---

## 🔐 Authentication & Sessions

### **Session-Based User Profile** (No Login Required ✅)

**Workflow**:

```
1. User visits website
   ↓
2. Django auto-creates session (COOKIES)
   ↓
3. UserProfileMiddleware checks session_id in UserProfile table
   ↓
4. If UserProfile doesn't exist → create empty one (NOT saved yet)
   ↓
5. User fills profile form → POST /products/setup/
   ↓
6. Profile gets saved to database
   ↓
7. Personalized recommendations available
```

### **Middleware**: `products/middleware.py`

```python
class UserProfileMiddleware:
    """
    Auto-create UserProfile from session_id
    Triggers on every request if not exists
    """
    def __call__(self, request):
        if not request.session.session_key:
            request.session.create()
        
        session_id = request.session.session_key
        user_profile, created = UserProfile.objects.get_or_create(
            session_id=session_id,
            defaults={'goal': 'general_fitness'}
        )
        request.user_profile = user_profile
```

### **Admin Login** (Optional ✅)

- `/admin/` - Django admin panel
- Only staff users can manage products/reviews
- No customer login required

---

## ⚡ Tối Ưu Hóa Performance

### **1️⃣ Database Optimization**

#### **Select Related** (Reduce N+1 queries)
```python
# ✅ GOOD: 1 query instead of N+1
Product.objects.select_related('category')\
    .prefetch_related('reviews')

# ❌ BAD: N+1 queries (category loaded separately for each product)
Product.objects.all()
```

#### **Indexes** (Speed up queries)
```python
class Meta:
    indexes = [
        models.Index(fields=['slug']),
        models.Index(fields=['status']),
        models.Index(fields=['supplement_type']),
        models.Index(fields=['-created_at']),
    ]
```

#### **Bulk Operations** (Fast inserts)
```python
# ✅ GOOD: 1 query
RecommendationLog.objects.bulk_create(logs, ignore_conflicts=True)

# ❌ BAD: N queries (one per item)
for log in logs:
    log.save()
```

---

### **2️⃣ API Response Optimization**

#### **Pagination** (Limit data per request)
```python
# In settings.py:
REST_FRAMEWORK = {
    'PAGE_SIZE': 8,  # 8 products per page
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination'
}
```

#### **Throttling** (Rate limiting)
```python
class ProductListThrottle(AnonRateThrottle):
    scope = 'product_list'
    # 100 requests per hour

class ProductDetailThrottle(AnonRateThrottle):
    scope = 'product_detail'
    # 200 requests per hour
```

#### **Caching** (Cache expensive queries)
```python
@action(detail=False, methods=['get'])
@method_decorator(cache_page(60 * 5))  # Cache 5 minutes
def categories(self, request):
    categories = ProductCategory.objects.all()
    return Response(...)
```

---

### **3️⃣ Frontend Optimization**

- **Static Files**: WhiteNoise middleware serves CSS/JS efficiently
- **Cloudinary**: CDN for product images (fast delivery)
- **Lazy Loading**: Images load only when visible
- **CSS Minification**: Reduce CSS file size
- **JavaScript Bundling**: Combine JS files

---

## 🚀 Deployment

### **Local Development**

```bash
# 1. Setup virtual environment
python -m venv venv
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Create .env file
cp .env.example .env
# Edit .env with your values

# 4. Run migrations
python manage.py migrate

# 5. Create superuser (admin)
python manage.py createsuperuser

# 6. Start server
python manage.py runserver
# Visit: http://127.0.0.1:8000/
```

---

### **Production Deployment (Railway)**

**Railway** adalah platform cloud yang menyediakan:
- ✅ Auto-scaling
- ✅ PostgreSQL database
- ✅ Environment variables management
- ✅ CI/CD deployment

**Steps**:
1. Push code ke GitHub
2. Connect GitHub repo to Railway
3. Set environment variables in Railway dashboard
4. Railway auto-deploys on push

**Key Files**:
- `Procfile` - Define how to run app
- `runtime.txt` - Specify Python version
- `requirements.txt` - Python dependencies
- `setup_railway.sh` - Run migrations on Railway

---

## 📚 Key Files Summary

| File | Purpose | Key Functions |
|------|---------|----------------|
| `settings.py` | Django configuration | Database, apps, middleware, static files |
| `products/models.py` | Database models | Product, UserProfile, Review, RecommendationLog |
| `products/views.py` | API viewsets & logic | ProductViewSet, recommendation engine |
| `products/serializers.py` | DRF serializers | Convert models to JSON |
| `products/forms.py` | Django forms | UserProfileForm for profile setup |
| `products/middleware.py` | Request middleware | Auto-create UserProfile from session |
| `templates/base.html` | Base template | Navigation, styling, structure |
| `templates/products/` | Product templates | List, detail, setup pages |
| `static/css/` | CSS stylesheets | Product page styles |
| `static/js/` | JavaScript | Frontend interactions |

---

## 🎯 Next Steps & Future Features

1. **🛒 Shopping Cart** - Add to cart functionality
2. **💳 Payment Gateway** - Stripe/VNPay integration
3. **📧 Email Notifications** - Order confirmation, promotional emails
4. **🤖 AI Recommendations** - ML-based personalized recommendations
5. **📊 Analytics Dashboard** - Track user behavior, sales trends
6. **⭐ Wishlist** - Save favorite products
7. **📱 Mobile App** - React Native mobile version
8. **🌍 Multi-language** - Support Vietnamese, English, etc.

---

## 📞 Support & Resources

- **Main README**: `/README.md`
- **User Profile Guide**: `docs/USER_PROFILE_SETUP_GUIDE.md`
- **Deployment Guide**: `docs/RAILWAY_CLEANUP_SETUP.md`
- **API Docs**: `/api/` (browsable API in development)
- **Admin Panel**: `/admin/` (Django admin)

---

**Last Updated**: January 4, 2026  
**Version**: 1.0.0  
**Author**: Fitblog Team
