# -*- coding: utf-8 -*-
"""
Admin interface for products app
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import ProductCategory, Product, ProductReview, UserProfile, RecommendationLog, ProductFlavor


class ProductFlavorInline(admin.TabularInline):
    """Inline admin cho hương vị sản phẩm"""
    model = ProductFlavor
    extra = 1
    fields = ['flavor', 'is_available']
    list_display = ['flavor', 'is_available']


@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    """Quản lý danh mục sản phẩm"""
    list_display = ['name', 'slug', 'icon_display', 'color_display', 'product_count', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at', 'product_count']
    list_per_page = 20

    fieldsets = (
        ('ℹ️ Thông tin cơ bản', {
            'fields': ('name', 'slug', 'description'),
            'description': 'Nhập tên danh mục, slug sẽ tự tạo từ tên'
        }),
        ('🎨 Hiển thị', {
            'fields': ('icon', 'color'),
            'description': 'Icon: dùng emoji (😊, 💪, 🏋️, 🥗, v.v.), Color: chọn màu hex'
        }),
        ('📊 Thống kê', {
            'fields': ('product_count',),
            'classes': ('collapse',)
        }),
        ('🔐 Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

    def icon_display(self, obj):
        return f"{obj.icon} {obj.icon}" if obj.icon else "—"
    icon_display.short_description = "Icon"

    def color_display(self, obj):
        return format_html(
            '<div style="width:30px;height:30px;background-color:{};border:1px solid #ccc;border-radius:4px;"></div>',
            obj.color
        )
    color_display.short_description = "Màu"

    def product_count(self, obj):
        return obj.products.count()
    product_count.short_description = "Số sản phẩm"


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Quản lý sản phẩm - Dễ dàng thêm, sửa, xóa sản phẩm"""
    list_display = [
        'product_icon',
        'name',
        'category_name',
        'supplement_type',
        'price_display',
        'stock_display',
        'status',
        'created_at'
    ]
    list_display_links = ['product_icon', 'name']  # Click vào icon hoặc name để mở detail
    list_filter = [
        'status',
        'supplement_type',
        'category',
        'created_at'
    ]
    search_fields = ['name', 'description', 'tags', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at', 'updated_at', 'get_tags_list', 'get_goals_list']
    list_editable = ['status']
    list_per_page = 20
    date_hierarchy = 'created_at'
    inlines = [ProductFlavorInline]  # Thêm inline admin cho flavors
    
    # Add button to change status
    actions = ['mark_available', 'mark_unavailable']

    fieldsets = (
        ('📦 Thông tin cơ bản', {
            'fields': ('name', 'slug', 'category', 'supplement_type', 'status'),
            'description': 'Nhập thông tin sản phẩm. Slug sẽ tự tạo từ tên.'
        }),
        ('💬 Mô tả & Hình ảnh', {
            'fields': ('short_description', 'description', 'image'),
            'description': 'Mô tả chi tiết về sản phẩm'
        }),
        ('💰 Giá & Tồn kho', {
            'fields': ('price', 'discount_percent', 'stock'),
            'description': 'Giá gốc, giảm giá (%), và số lượng tồn kho'
        }),
        ('🥗 Dinh dưỡng (mỗi khẩu phần)', {
            'fields': (
                'serving_size',
                'protein_per_serving',
                'carbs_per_serving',
                'fat_per_serving',
                'calories_per_serving'
            ),
            'description': 'Nhập thông tin dinh dưỡng cho 1 khẩu phần (ví dụ: 30g) - để trống nếu không có'
        }),
        ('🍫 Thành phần', {
            'fields': ('ingredients', 'flavor'),
            'description': 'Danh sách thành phần & hương vị sản phẩm'
        }),
        ('🎯 Tags & Mục tiêu (cho hệ thống gợi ý)', {
            'fields': (
                'tags',
                'suitable_for_goals',
                'get_tags_list',
                'get_goals_list'
            ),
            'description': 'Phân tách bằng dấu phẩy<br/>Tags: muscle-gain, lean, vegan<br/>Goals: muscle-gain, fat-loss, strength'
        }),
        ('🔍 SEO', {
            'fields': ('seo_title', 'seo_description'),
            'classes': ('collapse',),
            'description': 'Tiêu đề & mô tả cho công cụ tìm kiếm'
        }),
        ('📅 Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def product_icon(self, obj):
        """Hiển thị icon category next to product"""
        if obj.category and obj.category.icon:
            return format_html(
                '<span style="font-size:18px; margin-right:5px;">{}</span>',
                obj.category.icon
            )
        return "—"
    product_icon.short_description = "Icon"

    def category_name(self, obj):
        """Hiển thị tên category với badge"""
        if obj.category:
            return format_html(
                '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px; font-size: 11px;">{}</span>',
                obj.category.color,
                obj.category.name
            )
        return "—"
    category_name.short_description = "Danh mục"

    def stock_display(self, obj):
        """Hiển thị tồn kho với màu sắc"""
        if obj.stock > 5:
            color = 'green'
            text = f'✅ {obj.stock}'
        elif obj.stock > 0:
            color = 'orange'
            text = f'⚠️ {obj.stock}'
        else:
            color = 'red'
            text = '❌ Hết'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            text
        )
    stock_display.short_description = "Tồn kho"

    def status_display(self, obj):
        """Hiển thị trạng thái với emoji"""
        status_map = {
            'active': ('✅ Có sẵn', 'green'),
            'inactive': ('❌ Không có sẵn', 'gray'),
            'discontinued': ('⛔ Ngừng bán', 'red'),
        }
        text, color = status_map.get(obj.status, ('❓ Không rõ', 'gray'))
        return format_html(
            '<span style="color: {};">{}</span>',
            color,
            text
        )
    status_display.short_description = "Trạng thái"

    def price_display(self, obj):
        """Hiển thị giá với giảm giá"""
        discounted = obj.get_discounted_price()
        if obj.discount_percent > 0:
            return format_html(
                '<span style="color:green;font-weight:bold;">{} ₫</span> <del style="color:#999">{} ₫</del> <span style="color:red">-{}%</span>',
                '{:,.0f}'.format(discounted),
                '{:,.0f}'.format(obj.price),
                obj.discount_percent
            )
        return format_html(
            '<span style="color:green;font-weight:bold;">{} ₫</span>',
            '{:,.0f}'.format(obj.price)
        )
    price_display.short_description = "Giá"

    def rating_display(self, obj):
        """Hiển thị đánh giá"""
        avg = obj.get_average_rating()
        if avg:
            return format_html(
                '⭐ {:.1f}',
                avg
            )
        return "—"
    rating_display.short_description = "Đánh giá"

    def review_count(self, obj):
        """Số lượng review"""
        return obj.get_review_count()
    review_count.short_description = "Reviews"

    def mark_available(self, request, queryset):
        """Bulk action: Đánh dấu sản phẩm có sẵn"""
        updated = queryset.update(status='active')
        self.message_user(request, f'✅ Đã cập nhật {updated} sản phẩm thành "Có sẵn"')
    mark_available.short_description = "✅ Đánh dấu sản phẩm có sẵn"

    def mark_unavailable(self, request, queryset):
        """Bulk action: Đánh dấu sản phẩm không có sẵn"""
        updated = queryset.update(status='inactive')
        self.message_user(request, f'❌ Đã cập nhật {updated} sản phẩm thành "Không có sẵn"')
    mark_unavailable.short_description = "❌ Đánh dấu sản phẩm không có sẵn"


@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    """Quản lý đánh giá & nhận xét sản phẩm từ khách hàng"""
    list_display = [
        'product_name',
        'rating_stars',
        'author_name',
        'verified_badge',
        'approved_badge',
        'helpful_count',
        'created_at'
    ]
    list_filter = ['rating', 'is_approved', 'is_verified_purchase', 'created_at']
    search_fields = ['product__name', 'author_name', 'title', 'content']
    readonly_fields = ['created_at', 'updated_at']
    list_per_page = 20
    date_hierarchy = 'created_at'
    actions = ['approve_reviews', 'reject_reviews']

    fieldsets = (
        ('📦 Sản phẩm &  Tác giả', {
            'fields': ('product', 'author_name', 'author_email', 'is_verified_purchase'),
            'description': 'Chọn sản phẩm và nhập thông tin tác giả review'
        }),
        ('💬 Nội dung đánh giá', {
            'fields': ('title', 'rating', 'content'),
            'description': 'Tiêu đề, điểm đánh giá (1-5), và nội dung chi tiết'
        }),
        ('✅ Phê duyệt & Tương tác', {
            'fields': ('is_approved', 'helpful_count'),
            'description': 'Duyệt review trước khi hiển thị, đếm số người thấy hữu ích'
        }),
        ('📅 Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def product_name(self, obj):
        """Hiển thị sản phẩm được đánh giá"""
        return format_html(
            '<strong>{}</strong>',
            obj.product.name
        )
    product_name.short_description = "Sản phẩm"

    def rating_stars(self, obj):
        """Hiển thị sao đánh giá"""
        stars = "⭐" * obj.rating + "☆" * (5 - obj.rating)
        return format_html(
            '<span style="color:gold;font-size:16px;letter-spacing:2px;">{}</span> <strong>{}/5</strong>',
            stars,
            obj.rating
        )
    rating_stars.short_description = "⭐ Đánh giá"

    def verified_badge(self, obj):
        """Hiển thị xác minh mua hàng"""
        if obj.is_verified_purchase:
            return format_html('<span style="background-color:#4caf50;color:white;padding:3px 8px;border-radius:3px;font-size:11px;">✓ Xác minh</span>')
        return format_html('<span style="color:#999;">—</span>')
    verified_badge.short_description = "Xác minh"

    def approved_badge(self, obj):
        """Hiển thị trạng thái phê duyệt"""
        if obj.is_approved:
            return format_html('<span style="background-color:#4caf50;color:white;padding:3px 8px;border-radius:3px;font-size:11px;">✅ Duyệt</span>')
        return format_html('<span style="background-color:#ff9800;color:white;padding:3px 8px;border-radius:3px;font-size:11px;">⏳ Chờ</span>')
    approved_badge.short_description = "Trạng thái"

    def approve_reviews(self, request, queryset):
        updated = queryset.update(is_approved=True)
        self.message_user(request, f"✅ Đã phê duyệt {updated} review")
    approve_reviews.short_description = "✅ Phê duyệt review"

    def reject_reviews(self, request, queryset):
        updated = queryset.update(is_approved=False)
        self.message_user(request, f"❌ Đã từ chối {updated} review")
    reject_reviews.short_description = "❌ Từ chối review"


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """Quản lý hồ sơ người dùng"""
    list_display = [
        'session_id_short',
        'age',
        'gender',
        'bmi_display',
        'goal',
        'activity_level',
        'tdee_display',
        'last_activity'
    ]
    list_filter = ['goal', 'activity_level', 'created_at']
    search_fields = ['session_id']
    readonly_fields = ['session_id', 'created_at', 'last_activity']
    
    fieldsets = (
        ('Session', {
            'fields': ('session_id', 'created_at', 'last_activity')
        }),
        ('Thông số cơ thể', {
            'fields': ('age', 'gender', 'weight_kg', 'height_cm', 'bmi', 'tdee')
        }),
        ('Mục tiêu & Hoạt động', {
            'fields': ('goal', 'activity_level')
        }),
        ('Sở thích', {
            'fields': ('preferred_supplement_types', 'dietary_restrictions')
        }),
    )

    def session_id_short(self, obj):
        return '{}...'.format(obj.session_id[:12])
    session_id_short.short_description = "Session ID"

    def bmi_display(self, obj):
        if obj.bmi:
            if obj.bmi < 18.5:
                color = 'blue'
            elif obj.bmi < 23:
                color = 'green'
            else:
                color = 'orange'
            bmi_text = '{:.1f}'.format(obj.bmi)
            return format_html(
                '<span style="color:{};font-weight:bold;">{}</span>',
                color,
                bmi_text
            )
        return "—"
    bmi_display.short_description = "BMI"

    def tdee_display(self, obj):
        if obj.tdee:
            tdee_text = '{:.0f}'.format(obj.tdee)
            return format_html(
                '<span style="color:purple;font-weight:bold;"> {} kcal/day</span>',
                tdee_text
            )
        return "—"
    tdee_display.short_description = "TDEE"


@admin.register(RecommendationLog)
class RecommendationLogAdmin(admin.ModelAdmin):
    """Quản lý logs recommendation (Analytics)"""
    list_display = [
        'recommended_product',
        'recommendation_type',
        'score_display',
        'clicked_status',
        'purchased_status',
        'created_at'
    ]
    list_filter = ['recommendation_type', 'clicked', 'purchased', 'created_at']
    search_fields = ['recommended_product__name', 'reason']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Recommendation', {
            'fields': ('user_profile', 'recommended_product', 'recommendation_type')
        }),
        ('Thông tin gợi ý', {
            'fields': ('score', 'reason')
        }),
        ('Engagement', {
            'fields': ('clicked', 'purchased')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at')
        }),
    )

    def score_display(self, obj):
        color = 'green' if obj.score >= 0.8 else 'orange' if obj.score >= 0.5 else 'red'
        score_text = '{:.2f}'.format(obj.score)
        return format_html(
            '<span style="color:{};font-weight:bold;">{}</span>',
            color,
            score_text
        )
    score_display.short_description = "Score"

    def clicked_status(self, obj):
        if obj.clicked:
            return format_html('<span style="color:green;font-weight:bold;">✅ Clicked</span>')
        return "—"
    clicked_status.short_description = "Clicked"

    def purchased_status(self, obj):
        if obj.purchased:
            return format_html('<span style="color:green;font-weight:bold;">✅ Purchased</span>')
        return "—"
    purchased_status.short_description = "Purchased"
