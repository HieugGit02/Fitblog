from django import forms
from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Post, Comment, NewsletterSubscriber, SystemLog


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = '__all__'
        widgets = {
            'color': forms.TextInput(attrs={'type': 'color'}),
        }

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    form = CategoryForm
    list_display = ['name', 'colored_icon', 'slug', 'post_count']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['icon_preview']
    fieldsets = (
        (None, {
            'fields': ('name', 'slug', 'description')
        }),
        ('Icon & Color', {
            'fields': ('icon', 'icon_image', 'icon_preview', 'color'),
            'description': 'Bạn có thể tải lên một file ảnh nhỏ cho icon (ưu tiên), hoặc dùng emoji ở trên'
        }),
    )
    
    def colored_icon(self, obj):
        if obj.icon_image:
            return format_html('<img src="{}" style="width:28px;height:28px;border-radius:6px;object-fit:cover;"/>', obj.icon_image.url)
        return format_html('<span style="font-size: 24px;">{}</span>', obj.icon)
    colored_icon.short_description = "Icon"

    def icon_preview(self, obj):
        if obj.icon_image:
            return format_html('<img src="{}" style="max-width:120px;height:auto;border:1px solid #ddd;padding:4px;background:white;"/>', obj.icon_image.url)
        return "(No image uploaded)"
    icon_preview.short_description = "Preview Icon"
    
    def post_count(self, obj):
        return obj.posts.count()
    post_count.short_description = "Số bài viết"


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'status_badge', 'author', 'views', 'published_at']
    list_filter = ['status', 'category', 'created_at']
    search_fields = ['title', 'content']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['views', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Thông tin cơ bản', {
            'fields': ('title', 'slug', 'category', 'author', 'status')
        }),
        ('Nội dung', {
            'fields': ('excerpt', 'content', 'featured_image')
        }),
        ('Metadata', {
            'fields': ('tags',),
            'classes': ('collapse',)
        }),
        ('Thống kê', {
            'fields': ('views', 'created_at', 'updated_at', 'published_at'),
            'classes': ('collapse',)
        }),
    )
    
    def status_badge(self, obj):
        if obj.status == 'published':
            color = '#28a745'
            text = '✓ Xuất bản'
        else:
            color = '#ffc107'
            text = '◇ Nháp'
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px;">{}</span>',
            color, text
        )
    status_badge.short_description = "Trạng thái"


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['author', 'post_title', 'approval_status', 'created_at']
    list_filter = ['is_approved', 'created_at']
    search_fields = ['author', 'content', 'post__title']
    readonly_fields = ['created_at', 'updated_at']
    
    def post_title(self, obj):
        return obj.post.title
    post_title.short_description = "Bài viết"
    
    def approval_status(self, obj):
        if obj.is_approved:
            return format_html('<span style="color: #28a745;">✓ Được phê duyệt</span>')
        return format_html('<span style="color: #dc3545;">✗ Chờ duyệt</span>')
    approval_status.short_description = "Trạng thái"


@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(admin.ModelAdmin):
    list_display = ['email', 'subscribed_at', 'is_active']
    list_filter = ['is_active', 'subscribed_at']
    search_fields = ['email']
    readonly_fields = ['subscribed_at']


@admin.register(SystemLog)
class SystemLogAdmin(admin.ModelAdmin):
    list_display = ['log_level_badge', 'logger_name', 'message_preview', 'timestamp']
    list_filter = ['level', 'logger_name', 'timestamp']
    search_fields = ['message', 'logger_name']
    readonly_fields = ['level', 'logger_name', 'message', 'timestamp']
    date_hierarchy = 'timestamp'
    
    def has_add_permission(self, request):
        return False  # Không cho thêm log thủ công
    
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser  # Chỉ superuser mới xóa log
    
    def log_level_badge(self, obj):
        colors = {
            'DEBUG': '#0099cc',
            'INFO': '#28a745',
            'WARNING': '#ffc107',
            'ERROR': '#dc3545',
            'CRITICAL': '#721c24',
        }
        color = colors.get(obj.level, '#999')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px; font-weight: bold;">{}</span>',
            color, obj.level
        )
    log_level_badge.short_description = "Level"
    
    def message_preview(self, obj):
        preview = obj.message[:100] + ('...' if len(obj.message) > 100 else '')
        return preview
    message_preview.short_description = "Message"
