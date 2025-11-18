from django.contrib import admin
from .models import NgrokConfig, ChatMessage


@admin.register(NgrokConfig)
class NgrokConfigAdmin(admin.ModelAdmin):
    """Admin interface cho Ngrok Configuration"""
    
    list_display = ('name', 'ngrok_api_url', 'is_active', 'updated_at')
    list_filter = ('is_active', 'created_at', 'updated_at')
    search_fields = ('name', 'ngrok_api_url', 'description')
    
    fieldsets = (
        ('Thông Tin Cơ Bản', {
            'fields': ('name', 'description')
        }),
        ('Cấu Hình Ngrok', {
            'fields': ('ngrok_api_url', 'is_active'),
            'description': 'Nhập URL Ngrok đầy đủ (vd: https://abc123.ngrok-free.app/ask)'
        }),
        ('Thời Gian', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Hiển thị config active trước
        return qs.order_by('-is_active', '-updated_at')


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    """Admin interface cho Chat Messages"""
    
    list_display = ('timestamp', 'user_message_preview', 'bot_response_preview')
    list_filter = ('timestamp',)
    search_fields = ('user_message', 'bot_response')
    readonly_fields = ('user_message', 'bot_response', 'timestamp')
    
    def user_message_preview(self, obj):
        """Hiển thị preview user message"""
        return obj.user_message[:50] + '...' if len(obj.user_message) > 50 else obj.user_message
    user_message_preview.short_description = 'User Message'
    
    def bot_response_preview(self, obj):
        """Hiển thị preview bot response"""
        return obj.bot_response[:50] + '...' if len(obj.bot_response) > 50 else obj.bot_response
    bot_response_preview.short_description = 'Bot Response'
    
    def has_add_permission(self, request):
        # Không cho thêm message thủ công
        return False
    
    def has_delete_permission(self, request, obj=None):
        # Cho phép xóa message
        return True
