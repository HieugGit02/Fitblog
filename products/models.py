# -*- coding: utf-8 -*-
"""
Products app models for supplement e-commerce with recommendation system
"""

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.text import slugify
from django.urls import reverse
from datetime import timedelta
from django.utils import timezone

# ============================================================================
# PRODUCT CATEGORY MODEL
# ============================================================================

class ProductCategory(models.Model):
    """
    Danh mục sản phẩm (Whey, Pre-workout, Vitamins, etc)
    
    Example:
        - name: "Whey Protein"
        - slug: "whey-protein"
        - icon: "🥚"
        - color: "#b39ddb"
    """
    name = models.CharField(
        max_length=100,
        verbose_name="Tên danh mục",
        unique=True
    )
    slug = models.SlugField(
        unique=True,
        verbose_name="URL Slug"
    )
    description = models.TextField(
        blank=True,
        verbose_name="Mô tả"
    )
    icon = models.ImageField(
        upload_to='category_icons/',
        blank=True,
        null=True,
        verbose_name="Icon (PNG, JPG)"
    )
    color = models.CharField(
        max_length=7,
        default="#b39ddb",
        verbose_name="Màu sắc (Hex)"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Danh mục sản phẩm"
        ordering = ['name']
        indexes = [
            models.Index(fields=['slug']),
        ]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('products:category_detail', kwargs={'slug': self.slug})


# ============================================================================
# PRODUCT MODEL (Main model)
# ============================================================================

class Product(models.Model):
    """
    Sản phẩm Supplement với thông tin dinh dưỡng và recommendation metadata
    
    Fields breakdown:
    - Basic info: name, slug, category, supplement_type
    - Description: description, short_description
    - Pricing: price, discount_percent
    - Nutrition: protein_per_serving, carbs, fat, calories, serving_size
    - Metadata: tags, suitable_for_goals, embedding_vector (for recommendation)
    - Status: status, stock, created_at
    """
    
    STATUS_CHOICES = [
        ('active', 'Hoạt động'),
        ('inactive', 'Tạm ngừng'),
        ('outofstock', 'Hết hàng'),
    ]
    
    SUPPLEMENT_TYPE_CHOICES = [
        ('whey', 'Whey Protein'),
        ('isolate', 'Whey Isolate'),
        ('hydrolyzed', 'Whey Hydrolyzed'),
        ('concentrate', 'Whey Concentrate'),
        ('mass', 'Mass Gainer'),
        ('casein', 'Casein Protein'),
        ('creatine', 'Creatine'),
        ('preworkout', 'Pre-workout'),
        ('bcaa', 'BCAA'),
        ('eaa', 'EAA'),
        ('vitamins', 'Vitamins'),
        ('mineral', 'Mineral'),
        ('fatburner', 'Fat Burner'),
        ('gainer', 'Weight Gainer'),
        ('other', 'Khác'),
    ]

    # ========== BASIC INFO ==========
    name = models.CharField(
        max_length=255,
        verbose_name="Tên sản phẩm"
    )
    slug = models.SlugField(
        unique=True,
        verbose_name="URL Slug",
        max_length=255
    )
    category = models.ForeignKey(
        ProductCategory,
        on_delete=models.CASCADE,
        related_name='products',
        verbose_name="Danh mục"
    )
    supplement_type = models.CharField(
        max_length=20,
        choices=SUPPLEMENT_TYPE_CHOICES,
        verbose_name="Loại supplement"
    )

    # ========== DESCRIPTION ==========
    description = models.TextField(
        verbose_name="Mô tả chi tiết"
    )
    short_description = models.CharField(
        max_length=300,
        blank=True,
        verbose_name="Tóm tắt ngắn"
    )

    # ========== IMAGE ==========
    image = models.ImageField(
        upload_to='product_images/',
        verbose_name="Hình ảnh chính"
    )

    # ========== PRICING ==========
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Giá (VND)"
    )
    discount_percent = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name="Giảm giá (%)"
    )

    # ========== NUTRITION INFO (Per serving) ==========
    serving_size = models.CharField(
        max_length=50,
        default="30g",
        verbose_name="Khẩu phần (1 lần dùng)"
    )
    protein_per_serving = models.FloatField(
        validators=[MinValueValidator(0)],
        verbose_name="Protein (g)"
    )
    carbs_per_serving = models.FloatField(
        validators=[MinValueValidator(0)],
        verbose_name="Carbohydrates (g)"
    )
    fat_per_serving = models.FloatField(
        validators=[MinValueValidator(0)],
        verbose_name="Fat (g)"
    )
    calories_per_serving = models.FloatField(
        validators=[MinValueValidator(0)],
        verbose_name="Calories (kcal)"
    )

    # ========== INGREDIENTS & DETAILS ==========
    ingredients = models.TextField(
        blank=True,
        verbose_name="Thành phần"
    )
    flavor = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Hương vị"
    )

    # ========== MANAGEMENT ==========
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active',
        verbose_name="Trạng thái"
    )
    stock = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name="Số lượng tồn kho"
    )

    # ========== RECOMMENDATION METADATA ==========
    tags = models.CharField(
        max_length=300,
        blank=True,
        help_text="Phân tách bằng dấu phẩy (ví dụ: muscle-gain,weight-gain,lean, vegan,... )",
        verbose_name="Tags"
    )
    suitable_for_goals = models.CharField(
        max_length=300,
        blank=True,
        help_text="Phân tách bằng dấu phẩy (ví dụ: muscle-gain, weight-gain, fat-loss, strength, recovery, maintenance, free-lactose, whey-protein,...)",
        verbose_name="Phù hợp cho mục tiêu"
    )
    embedding_vector = models.JSONField(
        null=True,
        blank=True,
        verbose_name="Vector embedding (từ LLM)"
    )

    # ========== TIMESTAMPS ==========
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Cập nhật lúc")

    # ========== SEO ==========
    seo_title = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="SEO Title"
    )
    seo_description = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="SEO Description"
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Sản phẩm"
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['status']),
            models.Index(fields=['supplement_type']),
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('products:product_detail', kwargs={'slug': self.slug})

    def get_discounted_price(self):
        """Tính giá sau khi giảm"""
        if self.discount_percent > 0:
            return float(self.price) * (1 - self.discount_percent / 100)
        return float(self.price)
    
    @property
    def discounted_price(self):
        """Property để dùng trong template"""
        return self.get_discounted_price()
    
    def get_tags_list(self):
        """Return tags as list"""
        return [tag.strip() for tag in self.tags.split(',') if tag.strip()]
    
    def get_goals_list(self):
        """Return suitable goals as list"""
        return [goal.strip() for goal in self.suitable_for_goals.split(',') if goal.strip()]
    
    def save(self, *args, **kwargs):
        """Auto-generate slug from name nếu chưa có"""
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_average_rating(self):
        """Get average rating from reviews"""
        reviews = self.reviews.filter(is_approved=True)
        if not reviews.exists():
            return 0
        return reviews.aggregate(models.Avg('rating'))['rating__avg']

    def get_review_count(self):
        """Get total approved reviews count"""
        return self.reviews.filter(is_approved=True).count()


# ============================================================================
# PRODUCT REVIEW MODEL
# ============================================================================

class ProductReview(models.Model):
    """
    Review & rating cho sản phẩm
    
    Dùng cho Collaborative Filtering recommendation:
    - user_id: Để xác định người đánh giá (dùng làm input cho collab filtering)
    - product_id: Sản phẩm được đánh giá
    - rating: Điểm đánh giá (1-5 sao) - tạo user-item matrix
    
    Example:
        - user: User(id=1, username="john_doe")
        - product: Whey Protein Gold (id=5)
        - rating: 5
        - content: "Sản phẩm rất tốt, giao nhanh"
        - is_approved: True (chỉ show review approved)
    """
    # ========== USER & PRODUCT ==========
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='product_reviews',
        verbose_name="Người dùng",
        null=True,
        blank=True,
        help_text="User đã đăng nhập - dùng cho Collaborative Filtering"
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name="Sản phẩm"
    )
    author_name = models.CharField(
        max_length=100,
        verbose_name="Tên người review"
    )
    author_email = models.EmailField(verbose_name="Email")

    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name="Đánh giá (1-5 sao)"
    )
    title = models.CharField(
        max_length=200,
        verbose_name="Tiêu đề review"
    )
    content = models.TextField(verbose_name="Nội dung review")

    is_verified_purchase = models.BooleanField(
        default=False,
        verbose_name="Mua xác minh?"
    )
    is_approved = models.BooleanField(
        default=False,
        verbose_name="Được phê duyệt?"
    )

    helpful_count = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name="Số người tìm hữu ích"
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày review")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Cập nhật lúc")

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Review sản phẩm"
        indexes = [
            models.Index(fields=['product', '-rating']),
            models.Index(fields=['-created_at']),
            models.Index(fields=['user', 'product']),  # Dùng cho Collaborative Filtering
            models.Index(fields=['user', '-created_at']),  # Tìm review của user
        ]
        # Mỗi user chỉ có 1 review cho 1 sản phẩm
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'product'],
                name='unique_user_product_review',
                condition=models.Q(user__isnull=False)
            )
        ]

    def __str__(self):
        user_str = self.user.username if self.user else self.author_name
        return f"{self.rating}⭐ - {user_str} - {self.title}"


# ============================================================================
# USER PROFILE MODEL (Anonymous, session-based)
# ============================================================================

class UserProfile(models.Model):
    """
    Hồ sơ người dùng (Authentication-based).
    Liên kết với Django User model qua OneToOne relationship.
    
    Dùng để:
    1. Track user metrics (age, weight, goal, etc)
    2. Provide personalized recommendations
    3. Analytics & user behavior analysis
    
    Example:
        - user: User(username="john_doe")
        - age: 30
        - weight_kg: 75
        - height_cm: 175
        - goal: "muscle-gain"
        - tdee: 2500
        - bmi: 24.5
    """
    
    GOAL_CHOICES = [
        ('muscle-gain', 'Tăng cơ'),
        ('fat-loss', 'Giảm cân'),
        ('strength', 'Tăng sức mạnh'),
        ('endurance', 'Tăng sức bền'),
        ('body-recomposition', 'Vừa tăng cơ vừa giảm mỡ'),
        ('maintenance', 'Duy trì thể trạng'),
        ('general-health', 'Sức khỏe chung'),
        ('athletic', 'Thể thao'),  
    ]
    
    ACTIVITY_CHOICES = [
        ('sedentary', 'Ít vận động (< 1.5 h/tuần)'),
        ('light', 'Nhẹ (1-3 h/tuần)'),
        ('moderate', 'Vừa phải (3-5 h/tuần)'),
        ('active', 'Tích cực (5-6 h/tuần)'),
        ('intense', 'Cực kỳ tích cực (6-7 h/tuần)'),
    ]
    
    GENDER_CHOICES = [
        ('male', 'Nam'),
        ('female', 'Nữ'),
    ]

    # ========== USER AUTHENTICATION ==========
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
        null=True,
        blank=True,
        verbose_name="Người dùng"
    )
    
    # ========== SESSION TRACKING (Deprecated, for backward compatibility) ==========
    session_id = models.CharField(
        max_length=255,
        unique=True,
        null=True,
        blank=True,
        verbose_name="Session ID (Legacy, không sử dụng)"
    )

    # ========== PHYSICAL METRICS ==========
    age = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(16), MaxValueValidator(120)],
        verbose_name="Tuổi"
    )
    weight_kg = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(30), MaxValueValidator(200)],
        verbose_name="Cân nặng (kg)"
    )
    height_cm = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(100), MaxValueValidator(250)],
        verbose_name="Chiều cao (cm)"
    )
    gender = models.CharField(
        max_length=10,
        choices=GENDER_CHOICES,
        null=True,
        blank=True,
        verbose_name="Giới tính"
    )
    bmi = models.FloatField(
        null=True,
        blank=True,
        verbose_name="BMI"
    )
    tdee = models.FloatField(
        null=True,
        blank=True,
        verbose_name="TDEE (kcal/ngày)"
    )

    # ========== GOALS & PREFERENCES ==========
    goal = models.CharField(
        max_length=50,
        choices=GOAL_CHOICES,
        null=True,
        blank=True,
        verbose_name="Mục tiêu"
    )
    activity_level = models.CharField(
        max_length=50,
        choices=ACTIVITY_CHOICES,
        null=True,
        blank=True,
        verbose_name="Mức độ hoạt động"
    )

    # ========== DIETARY PREFERENCES ==========
    preferred_supplement_types = models.CharField(
        max_length=300,
        blank=True,
        help_text="Phân tách bằng dấu phẩy (ví dụ: whey, creatine, vitamins)",
        verbose_name="Loại supplement ưa thích"
    )
    dietary_restrictions = models.CharField(
        max_length=300,
        blank=True,
        help_text="Phân tách bằng dấu phẩy (ví dụ: vegan, gluten-free, dairy-free)",
        verbose_name="Hạn chế chế độ ăn"
    )

    # ========== TRACKING ==========
    last_activity = models.DateTimeField(
        auto_now=True,
        verbose_name="Hoạt động cuối"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")

    class Meta:
        verbose_name_plural = "Hồ sơ người dùng"
        ordering = ['-last_activity']
        indexes = [
            models.Index(fields=['session_id']),
        ]

    def __str__(self):
        if self.user:
            return f"{self.user.username} (Goal: {self.goal or 'Not set'})"
        elif self.session_id:
            return f"User {self.session_id[:8]}... (Goal: {self.goal or 'Not set'})"
        else:
            return f"Profile #{self.id} (Goal: {self.goal or 'Not set'})"

    def get_session_age_days(self):
        """Tính tuổi session (số ngày từ khi tạo đến giờ)"""
        if self.created_at:
            age = timezone.now() - self.created_at
            return age.days
        return None

    def get_session_age_display(self):
        """Hiển thị tuổi session dạng text"""
        age_days = self.get_session_age_days()
        if age_days is None:
            return "—"
        if age_days == 0:
            return "Hôm nay"
        elif age_days == 1:
            return "1 ngày"
        elif age_days <= 7:
            return f"{age_days} ngày"
        elif age_days <= 30:
            weeks = age_days // 7
            return f"{weeks} tuần"
        else:
            months = age_days // 30
            return f"{months} tháng"

    def is_session_expired(self, days=30):
        """Kiểm tra session có hết hạn không (mặc định 30 ngày)"""
        if not self.created_at:
            return False
        expiry_date = self.created_at + timedelta(days=days)
        return timezone.now() > expiry_date

    def calculate_bmi(self):
        """Calculate BMI từ weight & height"""
        if self.weight_kg and self.height_cm:
            self.bmi = self.weight_kg / ((self.height_cm / 100) ** 2)
            return self.bmi
        return None

    def calculate_tdee(self):
        """
        Calculate TDEE using Mifflin-St Jeor equation
        TDEE = BMR × Activity Factor
        """
        if not all([self.weight_kg, self.height_cm, self.age]):
            return None

        # BMR calculation (Mifflin-St Jeor)
        # BMR = (10 × weight) + (6.25 × height) - (5 × age) + 5 (for men) / -161 (for women)
        gender_factor = 5 if self.gender == 'male' else -161
        bmr = (10 * self.weight_kg) + (6.25 * self.height_cm) - (5 * self.age) + gender_factor

        # Activity factor
        activity_map = {
            'sedentary': 1.2,
            'light': 1.375,
            'moderate': 1.55,
            'active': 1.725,
            'intense': 1.9,
        }
        multiplier = activity_map.get(self.activity_level, 1.55)

        self.tdee = bmr * multiplier
        return self.tdee


# ============================================================================
# ============================================================================
# EVENT LOG MODEL (User Interaction Tracking - Optimized)
# ============================================================================

class EventLog(models.Model):
    """
    Track ALL user interactions: views, clicks, reviews, purchases, etc.
    
    More flexible than RecommendationLog:
    - Can track ANY event type, not just recommendations
    - No UNIQUE constraint (allow duplicate events)
    - Lightweight: only essential fields
    
    Example events:
    - user: User 123
    - product: Whey Gold  
    - event_type: 'product_view'
    - metadata: {'page': 'product_list', 'from_recommendation': 'personalized'}
    - timestamp: 2025-01-21 10:30:45
    """
    
    EVENT_TYPE_CHOICES = [
        # Product interactions
        ('product_view', 'Product viewed'),
        ('product_click', 'Product clicked'),
        ('review_submit', 'Review submitted'),
        ('review_helpful', 'Review marked helpful'),
        
        # Recommendation interactions
        ('rec_shown', 'Recommendation shown to user'),
        ('rec_clicked', 'Recommendation clicked'),
        ('rec_purchased', 'Recommended product purchased'),
        
        # Search & filter
        ('search', 'Search performed'),
        ('filter_apply', 'Filter applied'),
        ('sort_applied', 'Sort applied'),
        
        # Auth events
        ('login', 'User logged in'),
        ('logout', 'User logged out'),
        ('register', 'User registered'),
        ('profile_setup', 'Profile setup completed'),
        ('profile_update', 'Profile updated'),
        
        # Other
        ('page_load', 'Page loaded'),
        ('api_call', 'API called'),
    ]

    # ========== CORE FIELDS ==========
    user_profile = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE,
        related_name='events',
        verbose_name="Hồ sơ người dùng",
        null=True,
        blank=True
    )
    
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='events',
        verbose_name="Sản phẩm",
        null=True,
        blank=True
    )

    event_type = models.CharField(
        max_length=30,
        choices=EVENT_TYPE_CHOICES,
        db_index=True,
        verbose_name="Loại event"
    )

    # ========== OPTIONAL CONTEXT ==========
    # JSON field to store flexible metadata
    metadata = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Metadata (JSON)",
        help_text="Thông tin thêm: {'page': '...', 'from_rec': '...', 'score': ...}"
    )

    # ========== TIMESTAMP ==========
    timestamp = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name="Thời gian"
    )

    class Meta:
        verbose_name_plural = "Event Logs"
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user_profile', '-timestamp']),
            models.Index(fields=['event_type', '-timestamp']),
            models.Index(fields=['product', '-timestamp']),
            models.Index(fields=['-timestamp']),  # For recent events query
        ]

    def __str__(self):
        user = self.user_profile.user.username if self.user_profile else "anonymous"
        product = self.product.name if self.product else "N/A"
        return f"{user} | {self.event_type} | {product} | {self.timestamp.strftime('%Y-%m-%d %H:%M')}"

    def save(self, *args, **kwargs):
        """Auto-set timestamp if not provided"""
        if not self.id and not self.timestamp:
            self.timestamp = timezone.now()
        super().save(*args, **kwargs)


# ============================================================================
# PRODUCT FLAVOR MODEL
# ============================================================================

class ProductFlavor(models.Model):
    """
    Hương vị cho mỗi sản phẩm
    
    Example:
        - product: "Whey Gold"
        - flavor: "Vanilla"
        - is_available: True
        
    Một sản phẩm có thể có nhiều hương vị khác nhau
    """
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='flavors',
        verbose_name="Sản phẩm"
    )
    flavor = models.CharField(
        max_length=100,
        verbose_name="Tên hương vị"
    )
    is_available = models.BooleanField(
        default=True,
        verbose_name="Còn hàng"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Ngày tạo"
    )

    class Meta:
        verbose_name_plural = "Hương vị sản phẩm"
        ordering = ['product', 'flavor']
        unique_together = ['product', 'flavor']
        indexes = [
            models.Index(fields=['product', 'flavor']),
        ]

    def __str__(self):
        return f"{self.product.name} - {self.flavor}"


# ============================================================================
# PASSWORD RESET TOKEN MODEL
# ============================================================================

class PasswordResetToken(models.Model):
    """
    Mã token để reset mật khẩu.
    Mỗi token hợp lệ trong 1 giờ.
    
    Fields:
    - user: User requesting password reset
    - token: Unique token (generated from UID + timestamp)
    - created_at: When token was created
    - is_used: Whether token has been used
    - used_at: When token was used
    - expires_at: When token expires
    
    Example:
        - user: User(username="john_doe")
        - token: "abc123def456"
        - expires_at: 2026-01-04 15:00:00 (1 hour from now)
        - is_used: False
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='password_reset_tokens',
        verbose_name="Người dùng"
    )
    token = models.CharField(
        max_length=255,
        unique=True,
        verbose_name="Token Reset"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Thời gian tạo"
    )
    expires_at = models.DateTimeField(
        verbose_name="Hết hạn lúc"
    )
    is_used = models.BooleanField(
        default=False,
        verbose_name="Đã sử dụng"
    )
    used_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Thời gian sử dụng"
    )
    
    class Meta:
        verbose_name_plural = "Mã Reset Mật Khẩu"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['token']),
            models.Index(fields=['user', 'is_used']),
            models.Index(fields=['expires_at']),
        ]
    
    def __str__(self):
        return f"Reset token for {self.user.username}"
    
    @property
    def is_valid(self):
        """Check if token is still valid (not expired and not used)"""
        return not self.is_used and timezone.now() < self.expires_at
    
    @property
    def is_expired(self):
        """Check if token has expired"""
        return timezone.now() > self.expires_at
    
    def mark_as_used(self):
        """Mark token as used"""
        self.is_used = True
        self.used_at = timezone.now()
        self.save()
