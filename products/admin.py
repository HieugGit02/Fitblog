# -*- coding: utf-8 -*-
"""
Admin interface for products app
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import path
from django.shortcuts import render
from django.contrib.auth.models import User
from django.db.models import Count, Q
from datetime import timedelta
from django.utils import timezone
from .models import ProductCategory, Product, ProductReview, UserProfile, RecommendationLog, ProductFlavor
from .admin_user import UserAdmin, AdminUserFilter


# ========== CUSTOM ADMIN SITE ==========
class FitblogAdminSite(admin.AdminSite):
    """Custom admin site với dashboard"""
    site_header = "🏋️ FITBLOG ADMIN"
    site_title = "Fitblog Admin Portal"
    index_title = "Dashboard Quản Trị"
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('dashboard/', self.admin_view(self.dashboard_view), name='dashboard'),
        ]
        return custom_urls + urls
    
    def index(self, request, extra_context=None):
        """Override index để hiển thị dashboard"""
        return self.dashboard_view(request)
    
    def dashboard_view(self, request):
        """Dashboard thống kê user"""
        # Thống kê cơ bản
        total_users = User.objects.count()
        total_profiles = UserProfile.objects.count()
        admin_users = User.objects.filter(Q(is_staff=True) | Q(is_superuser=True)).count()
        regular_users = total_users - admin_users
        
        # User mới trong 7 ngày
        seven_days_ago = timezone.now() - timedelta(days=7)
        new_users_7days = User.objects.filter(date_joined__gte=seven_days_ago).count()
        
        # User mới hôm nay
        today = timezone.now().date()
        new_users_today = User.objects.filter(date_joined__date=today).count()
        
        # Active users (có profile được update)
        thirty_days_ago = timezone.now() - timedelta(days=30)
        active_users = UserProfile.objects.filter(
            last_activity__gte=thirty_days_ago
        ).select_related('user').count()
        
        # Users by goal
        users_by_goal = UserProfile.objects.values('goal').annotate(count=Count('goal')).order_by('-count')
        
        # Top goals
        top_goals = []
        goal_names = {
            'muscle-gain': 'Tăng cơ',
            'fat-loss': 'Giảm cân',
            'strength': 'Tăng sức mạnh',
            'endurance': 'Tăng sức bền',
            'body-recomposition': 'Vừa tăng cơ vừa giảm mỡ',
            'maintenance': 'Duy trì thể trạng',
            'general-health': 'Sức khỏe chung',
            'athletic': 'Thể thao',
        }
        for goal_data in users_by_goal:
            goal_key = goal_data['goal']
            top_goals.append({
                'goal': goal_names.get(goal_key, goal_key),
                'count': goal_data['count']
            })
        
        # Profile completion
        profiles_with_age = UserProfile.objects.filter(age__isnull=False).count()
        profiles_with_weight = UserProfile.objects.filter(weight_kg__isnull=False).count()
        completion_rate = round((profiles_with_weight / total_profiles * 100) if total_profiles > 0 else 0, 1)
        
        context = {
            'site_header': self.site_header,
            'site_title': self.site_title,
            'total_users': total_users,
            'total_profiles': total_profiles,
            'admin_users': admin_users,
            'regular_users': regular_users,
            'new_users_7days': new_users_7days,
            'new_users_today': new_users_today,
            'active_users': active_users,
            'top_goals': top_goals,
            'completion_rate': completion_rate,
            'profiles_with_weight': profiles_with_weight,
        }
        return render(request, 'admin/dashboard.html', context)


# Tạo instance custom admin site
fitblog_admin_site = FitblogAdminSite(name='fitblog_admin')


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
        'user_or_author',
        'verified_badge',
        'approved_badge',
        'helpful_count',
        'created_at'
    ]
    list_filter = ['rating', 'is_approved', 'is_verified_purchase', 'created_at', 'user']
    search_fields = ['product__name', 'author_name', 'user__username', 'title', 'content']
    readonly_fields = ['created_at', 'updated_at']
    list_per_page = 20
    date_hierarchy = 'created_at'
    actions = ['approve_reviews', 'reject_reviews']

    fieldsets = (
        ('� User & Sản phẩm', {
            'fields': ('user', 'product', 'is_verified_purchase'),
            'description': 'Chọn user đã đăng nhập (dùng cho Collaborative Filtering) và sản phẩm'
        }),
        ('📝 Thông tin tác giả', {
            'fields': ('author_name', 'author_email'),
            'description': 'Tên & email - dùng nếu user không được chọn'
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

    def user_or_author(self, obj):
        """Hiển thị user hoặc tên tác giả"""
        if obj.user:
            return format_html(
                '<strong style="color:#0066cc;">👤 {}</strong><br/><small>(uid: {})</small>',
                obj.user.username,
                obj.user.id
            )
        else:
            return format_html(
                '<em>{}</em>',
                obj.author_name
            )
    user_or_author.short_description = "Người dùng / Tác giả"

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
        'username_display',
        'user_type',
        'age',
        'gender',
        'bmi_display',
        'goal',
        'activity_level',
        'profile_completion',
        'last_activity'
    ]
    list_filter = ['goal', 'activity_level', 'gender', 'created_at', 'last_activity']
    search_fields = ['user__username', 'user__email', 'session_id']
    readonly_fields = ['session_id', 'created_at', 'last_activity', 'session_info', 'bmi']
    
    fieldsets = (
        ('👤 Thông tin người dùng', {
            'fields': ('user',)
        }),
        ('🔐 Session (Legacy)', {
            'fields': ('session_id', 'session_info', 'created_at', 'last_activity'),
            'classes': ('collapse',)
        }),
        ('📊 Thông số cơ thể', {
            'fields': ('age', 'gender', 'weight_kg', 'height_cm', 'bmi', 'tdee')
        }),
        ('🎯 Mục tiêu & Hoạt động', {
            'fields': ('goal', 'activity_level')
        }),
        ('❤️ Sở thích', {
            'fields': ('preferred_supplement_types', 'dietary_restrictions')
        }),
    )
    
    actions = ['delete_old_sessions']

    def username_display(self, obj):
        """Hiển thị username hoặc session_id"""
        if obj.user:
            return format_html(
                '<strong>{}</strong><br/><small style="color:#999;">{}</small>',
                obj.user.username,
                obj.user.email
            )
        if obj.session_id:
            return format_html('<small style="color:#999;">{}...</small>', obj.session_id[:20])
        return '—'
    username_display.short_description = "👤 Username / Email"

    def user_type(self, obj):
        """Hiển thị loại người dùng: Admin hoặc User"""
        if obj.user:
            if obj.user.is_staff or obj.user.is_superuser:
                return format_html(
                    '<span style="background-color:#FF6B6B;color:white;padding:4px 8px;border-radius:4px;font-weight:bold;">👨‍💼 Admin</span>'
                )
            else:
                return format_html(
                    '<span style="background-color:#51CF66;color:white;padding:4px 8px;border-radius:4px;font-weight:bold;">👤 User</span>'
                )
        return format_html('<span style="background-color:#999;color:white;padding:4px 8px;border-radius:4px;">—</span>')
    user_type.short_description = "Loại"

    def profile_completion(self, obj):
        """Hiển thị % hoàn thành hồ sơ"""
        fields = [obj.age, obj.weight_kg, obj.height_cm, obj.gender, obj.goal, obj.activity_level]
        completed = sum(1 for f in fields if f)
        total = len(fields)
        percentage = round((completed / total) * 100)
        
        if percentage >= 80:
            color = '#51CF66'  # Green
        elif percentage >= 50:
            color = '#FFA500'  # Orange
        else:
            color = '#FF6B6B'  # Red
        
        return format_html(
            '<div style="background-color:{};color:white;padding:4px 8px;border-radius:4px;text-align:center;font-weight:bold;min-width:50px;">{}%</div>',
            color,
            percentage
        )
    profile_completion.short_description = "Hoàn thành"

    def session_id_short(self, obj):
        if obj.session_id:
            return '{}...'.format(obj.session_id[:12])
        return '(No session)'
    session_id_short.short_description = "Session ID"
    
    def session_age_display(self, obj):
        """Hiển thị tuổi session và cảnh báo nếu quá cũ"""
        age_display = obj.get_session_age_display()
        age_days = obj.get_session_age_days()
        
        if age_days is None:
            return "—"
        
        # Cảnh báo nếu session > 30 ngày
        if age_days > 30:
            return format_html(
                '<span style="color:red;font-weight:bold;">{} ⚠️</span>',
                age_display
            )
        elif age_days > 14:
            return format_html(
                '<span style="color:orange;font-weight:bold;">{}</span>',
                age_display
            )
        else:
            return format_html(
                '<span style="color:green;">{}</span>',
                age_display
            )
    session_age_display.short_description = "Tuổi Session"
    
    def session_info(self, obj):
        """Hiển thị thông tin chi tiết về session"""
        if not obj.created_at:
            return "—"
        
        age_days = obj.get_session_age_days()
        created = obj.created_at.strftime('%d/%m/%Y %H:%M')
        last_active = obj.last_activity.strftime('%d/%m/%Y %H:%M')
        
        if obj.is_session_expired(30):
            status = '<span style="color:red;font-weight:bold;">Hết hạn (>30 ngày)</span>'
        elif obj.is_session_expired(14):
            status = '<span style="color:orange;font-weight:bold;">Sắp hết hạn (>14 ngày)</span>'
        else:
            status = '<span style="color:green;font-weight:bold;">Còn hiệu lực</span>'
        
        info = f"""
        <div style="background:#f9f9f9;padding:10px;border-radius:4px;font-size:0.9rem;">
            <p><strong>Tuổi Session:</strong> {age_days} ngày</p>
            <p><strong>Ngày tạo:</strong> {created}</p>
            <p><strong>Hoạt động cuối:</strong> {last_active}</p>
            <p><strong>Trạng thái:</strong> {status}</p>
        </div>
        """
        return format_html(info)
    session_info.short_description = "Thông tin Session"

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
    
    def delete_old_sessions(self, request, queryset):
        """Action: Xóa sessions cũ hơn 30 ngày"""
        from django.utils import timezone
        from datetime import timedelta
        
        cutoff_date = timezone.now() - timedelta(days=30)
        old_profiles = UserProfile.objects.filter(created_at__lt=cutoff_date)
        count = old_profiles.count()
        old_profiles.delete()
        
        self.message_user(request, f"Đã xóa {count} session cũ hơn 30 ngày")
    delete_old_sessions.short_description = "Xóa sessions cũ hơn 30 ngày"


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


# ============================================================================
# PASSWORD RESET TOKEN ADMIN
# ============================================================================

class PasswordResetTokenAdmin(admin.ModelAdmin):
    """Admin interface for password reset tokens"""
    list_display = (
        'user',
        'created_at',
        'expires_at',
        'is_used',
        'used_at',
        'token_status',
    )
    list_filter = ('is_used', 'created_at', 'expires_at')
    search_fields = ('user__username', 'user__email', 'token')
    readonly_fields = ('token', 'created_at', 'used_at', 'is_valid', 'is_expired')
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Thông tin Token', {
            'fields': ('user', 'token')
        }),
        ('Thời gian', {
            'fields': ('created_at', 'expires_at', 'used_at')
        }),
        ('Trạng thái', {
            'fields': ('is_used', 'is_valid', 'is_expired')
        }),
    )
    
    def token_status(self, obj):
        """Display token status with color coding"""
        if obj.is_used:
            return format_html('<span style="color:gray;">🔒 Đã dùng</span>')
        elif obj.is_expired:
            return format_html('<span style="color:red;">⏰ Hết hạn</span>')
        else:
            return format_html('<span style="color:green;">✅ Hợp lệ</span>')
    token_status.short_description = "Trạng thái"
    
    def get_readonly_fields(self, request, obj=None):
        """Prevent editing of most fields"""
        if obj:  # Editing an existing object
            return self.readonly_fields + ['user', 'expires_at']
        return self.readonly_fields


# ============================================================================
# REGISTER ALL MODELS
# ============================================================================

from .models import PasswordResetToken

# Register with custom admin site
fitblog_admin = FitblogAdminSite(name='fitblog_admin')

# User management
fitblog_admin.register(User, UserAdmin)

# Products
fitblog_admin.register(ProductCategory, ProductCategoryAdmin)
fitblog_admin.register(Product, ProductAdmin)

# User profiles & reviews
fitblog_admin.register(UserProfile, UserProfileAdmin)
fitblog_admin.register(ProductReview, ProductReviewAdmin)

# Recommendations
fitblog_admin.register(RecommendationLog, RecommendationLogAdmin)

# Password reset tokens
fitblog_admin.register(PasswordResetToken, PasswordResetTokenAdmin)