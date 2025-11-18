import os
from pathlib import Path
import dj_database_url
from dotenv import load_dotenv

# Tải biến môi trường từ file .env (cho local)
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# ==========================================
# 1. BẢO MẬT & CẤU HÌNH CƠ BẢN
# ==========================================

# Lấy SECRET_KEY từ biến môi trường, nếu không có thì dùng key tạm (chỉ cho local)
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-key-mac-dinh-thay-doi-ngay')

# Tắt DEBUG trên Railway (Mặc định là True nếu không set biến môi trường)
# Trên Railway bạn nhớ set biến DEBUG = False
DEBUG = os.environ.get('DEBUG', 'True') == 'True'

ALLOWED_HOSTS = ['*']  # Cho phép tất cả host để tránh lỗi 400 Bad Request trên Railway

# QUAN TRỌNG CHO RAILWAY: Tránh lỗi 403 Forbidden khi submit form
CSRF_TRUSTED_ORIGINS = [
    'https://*.railway.app',
    'https://fitblog-production.up.railway.app',
]

# ==========================================
# 2. ỨNG DỤNG & MIDDLEWARE
# ==========================================

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Third party
    'rest_framework',
    'corsheaders',
    # Apps
    'blog',
    'chatbot',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # <-- Whitenoise phải ở ngay sau Security
    'corsheaders.middleware.CorsMiddleware',       # <-- Cors phải ở trên Common
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'fitblog_config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'fitblog_config.wsgi.application'


# ==========================================
# 3. DATABASE (FIX LỖI QUAN TRỌNG)
# ==========================================

# Cấu hình mặc định là SQLite (cho local)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Cấu hình cho Railway (PostgreSQL)
database_url = os.environ.get("DATABASE_URL")

if database_url:
    try:
        # Parse URL thành config dictionary
        db_from_env = dj_database_url.config(
            default=database_url,
            conn_max_age=600,
            ssl_require=True
        )
        
        # FIX LỖI: Tự động thêm tên DB 'railway' nếu bị thiếu
        if db_from_env and not db_from_env.get('NAME'):
            db_from_env['NAME'] = 'railway'
            
        DATABASES['default'] = db_from_env
        print("✅ Database configured successfully for Railway.")
    except Exception as e:
        print(f"❌ Error configuring database: {e}")


# ==========================================
# 4. STATIC FILES (CSS/JS/IMAGES)
# ==========================================

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

# Cấu hình Whitenoise để phục vụ file tĩnh
if not DEBUG:
    # STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
    #  web vẫn chạy dù thiếu ảnh:
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# ==========================================
# 5. CÁC CẤU HÌNH KHÁC
# ==========================================

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
LANGUAGE_CODE = 'vi-VN'
TIME_ZONE = 'Asia/Ho_Chi_Minh'
USE_I18N = True
USE_TZ = True

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# CORS Configuration
CORS_ALLOW_ALL_ORIGINS = True # Đơn giản hóa cho môi trường dev/test
CORS_ALLOW_CREDENTIALS = True

# REST Framework
REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
}

# Chatbot API
NGROK_LLM_API = os.environ.get('NGROK_LLM_API', 'http://localhost:8001')

# Logging cơ bản (Tránh lỗi DatabaseLogHandler khi chưa có bảng)
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}