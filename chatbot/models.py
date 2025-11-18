from django.db import models
from django.core.exceptions import ValidationError

class NgrokConfig(models.Model):
    """Model để lưu cấu hình Ngrok API URL"""
    
    name = models.CharField(
        max_length=255, 
        default="Ngrok LLM API",
        help_text="Tên cấu hình"
    )
    ngrok_api_url = models.URLField(
        help_text="URL Ngrok đầy đủ (vd: https://abc123.ngrok-free.app/ask)",
        verbose_name="Ngrok API URL"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Kích hoạt cấu hình này"
    )
    description = models.TextField(
        blank=True,
        help_text="Mô tả về cấu hình này"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Ngrok Configuration"
        verbose_name_plural = "Ngrok Configurations"
        ordering = ['-is_active', '-updated_at']
    
    def __str__(self):
        return f"{self.name} - {'🟢 Active' if self.is_active else '🔴 Inactive'}"
    
    def save(self, *args, **kwargs):
        # Chỉ cho phép 1 config active duy nhất
        if self.is_active:
            NgrokConfig.objects.filter(is_active=True).exclude(pk=self.pk).update(is_active=False)
        super().save(*args, **kwargs)
    
    @classmethod
    def get_active_url(cls):
        """Lấy URL Ngrok active hiện tại"""
        config = cls.objects.filter(is_active=True).first()
        if config:
            return config.ngrok_api_url
        return None


class ChatMessage(models.Model):
    """Model để lưu lịch sử chat (tùy chọn)"""
    
    user_message = models.TextField()
    bot_response = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Chat Message"
        verbose_name_plural = "Chat Messages"
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"Chat at {self.timestamp}"
