from django.db import models
from django.utils.text import slugify
from django.urls import reverse

class Category(models.Model):
    """Danh mục bài viết (Dinh dưỡng, Thể hình, Công thức, vv)"""
    name = models.CharField(max_length=100, verbose_name="Tên danh mục")
    slug = models.SlugField(max_length=100, unique=True, verbose_name="URL Slug")
    description = models.TextField(blank=True, verbose_name="Mô tả")
    icon = models.CharField(
        max_length=50,
        default="",
        blank=True,
        verbose_name="Icon Emoji (tùy chọn)"
    )
    # Uploaded small icon image (required for new entries, but nullable in DB for migration safety)
    icon_image = models.ImageField(
        upload_to='category_icons/',
        blank=False,  # Required in forms
        null=True,    # Nullable in DB to avoid migration issues
        verbose_name="Icon Image (bắt buộc)"
    )
    color = models.CharField(
        max_length=7,
        default="#b39ddb",
        verbose_name="Màu sắc"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']
        verbose_name_plural = "Danh mục"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('blog:category_detail', kwargs={'slug': self.slug})


class Post(models.Model):
    """Bài viết blog"""
    STATUS_CHOICES = [
        ('draft', 'Nháp'),
        ('published', 'Đã xuất bản'),
    ]

    title = models.CharField(max_length=200, verbose_name="Tiêu đề")
    slug = models.SlugField(max_length=200, unique=True, verbose_name="URL Slug")
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name="Danh mục"
    )
    author = models.CharField(
        max_length=100,
        default="Hinne 🥗",
        verbose_name="Tác giả"
    )
    excerpt = models.CharField(
        max_length=300,
        blank=True,
        verbose_name="Tóm tắt"
    )
    content = models.TextField(verbose_name="Nội dung")
    
    # SEO & Display
    featured_image = models.ImageField(
        upload_to='blog_images/',
        blank=True,
        null=True,
        verbose_name="Hình ảnh nổi bật"
    )
    
    # Metadata
    tags = models.CharField(
        max_length=200,
        blank=True,
        help_text="Phân tách bằng dấu phẩy",
        verbose_name="Thẻ tag"
    )
    
    # Status & Timestamps
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='draft',
        verbose_name="Trạng thái"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Cập nhật lúc")
    published_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Ngày xuất bản"
    )
    
    # Engagement
    views = models.PositiveIntegerField(default=0, verbose_name="Lượt xem")

    class Meta:
        ordering = ['-published_at']
        verbose_name_plural = "Bài viết"
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['-published_at']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('blog:post_detail', kwargs={'slug': self.slug})

    def get_tags_list(self):
        return [tag.strip() for tag in self.tags.split(',') if tag.strip()]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)


class Comment(models.Model):
    """Bình luận trên bài viết"""
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name="Bài viết"
    )
    author = models.CharField(max_length=100, verbose_name="Tên tác giả")
    email = models.EmailField(verbose_name="Email")
    content = models.TextField(verbose_name="Nội dung")
    
    # Status
    is_approved = models.BooleanField(default=False, verbose_name="Được phê duyệt?")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Cập nhật lúc")

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Bình luận"

    def __str__(self):
        return f"Bình luận từ {self.author} trên {self.post.title}"


class NewsletterSubscriber(models.Model):
    """Người đăng ký newsletter"""
    email = models.EmailField(unique=True, verbose_name="Email")
    subscribed_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày đăng ký")
    is_active = models.BooleanField(default=True, verbose_name="Hoạt động?")

    class Meta:
        verbose_name_plural = "Người đăng ký"

    def __str__(self):
        return self.email


class SystemLog(models.Model):
    """Model để lưu log từ ứng dụng (có thể xem trong admin)"""
    LEVEL_CHOICES = [
        ('DEBUG', 'Debug'),
        ('INFO', 'Info'),
        ('WARNING', 'Warning'),
        ('ERROR', 'Error'),
        ('CRITICAL', 'Critical'),
    ]
    
    level = models.CharField(
        max_length=10,
        choices=LEVEL_CHOICES,
        default='INFO',
        verbose_name="Mức độ"
    )
    logger_name = models.CharField(
        max_length=255,
        verbose_name="Tên logger",
        default="django"
    )
    message = models.TextField(verbose_name="Nội dung log")
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="Thời gian")
    
    class Meta:
        verbose_name = "System Log"
        verbose_name_plural = "System Logs"
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['-timestamp']),
            models.Index(fields=['level']),
        ]
    
    def __str__(self):
        return f"[{self.level}] {self.logger_name} - {self.timestamp}"

