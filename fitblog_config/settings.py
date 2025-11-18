import os
from pathlib import Path
from dotenv import load_dotenv
from decouple import config
import dj_database_url
# import cloudinary
# import cloudinary.uploader
# from cloudinary.utils import cloudinary_url
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY', default='django-insecure-your-secret-key-change-in-production-12345')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=True, cast=bool)

# ALLOWED_HOSTS configuration - strip whitespace from split values
# In production, set ALLOWED_HOSTS with your domain
_allowed_hosts_str = config('ALLOWED_HOSTS', default='localhost,127.0.0.1,0.0.0.0,*.railway.app,fitblog-production.up.railway.app')
ALLOWED_HOSTS = [host.strip() for host in _allowed_hosts_str.split(',')]

# Allow all hosts in development mode
if DEBUG:
    ALLOWED_HOSTS = ['*']


# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'blog',
    'chatbot',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'corsheaders.middleware.CorsMiddleware',
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


# Database
# On Railway, prefer PostgreSQL via DATABASE_URL
# Fallback to SQLite in /tmp for local/development
import tempfile

# # Check if DATABASE_URL is set (Railway/production)
# database_url = os.getenv('DATABASE_URL')

# 1. Cấu hình mặc định (Local): Lưu vào BASE_DIR để giữ dữ liệu
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3', # <-- Sửa dòng này (quan trọng)
    }
}

# 2. Cấu hình Railway (Production)
database_url = os.getenv('DATABASE_URL')

if database_url:
    try:
        # Parse URL thành config dictionary
        db_config = dj_database_url.config(
            default=database_url,
            conn_max_age=600,
            conn_health_checks=True,
            ssl_require=True,
        )
        
        # FIX LỖI: Nếu config trả về thiếu tên DB, tự gán mặc định
        if db_config and not db_config.get('NAME'):
            db_config['NAME'] = 'railway'
            
        DATABASES['default'] = db_config
        
    except Exception as e:
        # Fallback an toàn: In lỗi ra console thay vì sập web ngay lập tức
        print(f"❌ Error configuring database from URL: {e}")


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


# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Create staticfiles directory if it doesn't exist
os.makedirs(STATIC_ROOT, exist_ok=True)

# Don't ignore SVG and other files during collectstatic
STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ===== CORS Configuration =====
CORS_ALLOWED_ORIGINS = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

CORS_ALLOW_CREDENTIALS = True

# ===== REST Framework =====
REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
}

# ===== Chatbot Settings =====
NGROK_LLM_API = os.getenv(
    'NGROK_LLM_API',
    'https://yyyyy.ngrok-free.app/ask'  # Sẽ cập nhật sau
)

# ===== Logging =====
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{levelname}] {name} - {message}',
            'style': '{',
        },
        'simple': {
            'format': '{message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'database': {
            'class': 'blog.logging_handlers.DatabaseLogHandler',
            'formatter': 'verbose',
            'level': 'INFO',  # Only log INFO and above to DB to avoid noise
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],  # Disable database handler for now
            'level': 'INFO',
            'propagate': False,
        },
        'blog': {
            'handlers': ['console'],  # Disable database handler for now
            'level': 'INFO',
            'propagate': False,
        },
        'chatbot': {
            'handlers': ['console'],  # Disable database handler for now
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# CORS Settings
CORS_ALLOWED_ORIGINS = config(
    'CORS_ALLOWED_ORIGINS', 
    default='http://localhost:3000,http://localhost:8000'
).split(',')

# Security Settings for Production
if not DEBUG:
    # Disable SSL redirect on Railway (Railway handles SSL termination)
    SECURE_SSL_REDIRECT = False
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_SECURITY_POLICY = {
        'default-src': ("'self'",),
    }

# WhiteNoise Settings
if DEBUG:
    STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'
else:
    # Use WhiteNoise without manifest for production
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'

# Chatbot API
NGROK_LLM_API = config('NGROK_LLM_API', default='http://localhost:8001/ask')

# Thêm vào INSTALLED_APPS
INSTALLED_APPS = [
    # ...
    'cloudinary_storage',
    'cloudinary',
    # ...
]

# Cấu hình key (Lấy từ Dashboard Cloudinary)
CLOUDINARY_STORAGE = {
    'CLOUD_NAME': 'dt7txilej',
    'API_KEY': '233841116172244',
    'API_SECRET': 'qE3BX_pvuI-xZvlAZAT46-zMP1o'
}

DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'