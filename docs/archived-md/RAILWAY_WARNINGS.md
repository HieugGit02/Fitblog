# ⚠️ Railway Deployment - Important Notes & Optimizations

## 🚨 Critical Issues to Fix Before Deploy

### 1. Media Files Storage (CRITICAL - ⚠️)

**Problem:** Railway has ephemeral filesystem
- Uploaded files (category icons, blog images) **will be deleted** when:
  - You redeploy
  - Railway restarts the container
  - Scale up/down

**Current Status:** ❌ Not configured for production

**Solutions:**

#### Option A: Use AWS S3 (Recommended)
```bash
pip install boto3 django-storages
```

Update `requirements.txt` and modify settings:
```python
if not DEBUG:
    # Use S3 for media storage
    STORAGES = {
        'default': {
            'BACKEND': 'storages.backends.s3boto3.S3Boto3Storage',
            'OPTIONS': {
                'AWS_ACCESS_KEY_ID': os.getenv('AWS_ACCESS_KEY_ID'),
                'AWS_SECRET_ACCESS_KEY': os.getenv('AWS_SECRET_ACCESS_KEY'),
                'AWS_STORAGE_BUCKET_NAME': os.getenv('AWS_STORAGE_BUCKET_NAME'),
                'AWS_S3_REGION_NAME': 'us-east-1',
                'AWS_S3_CUSTOM_DOMAIN': f"{os.getenv('AWS_STORAGE_BUCKET_NAME')}.s3.amazonaws.com",
            }
        }
    }
    MEDIA_URL = f"https://{os.getenv('AWS_STORAGE_BUCKET_NAME')}.s3.amazonaws.com/media/"
```

#### Option B: Use Cloudinary
```bash
pip install cloudinary
```

Update settings:
```python
import cloudinary
cloudinary.config(
    cloud_name=os.getenv('CLOUDINARY_NAME'),
    api_key=os.getenv('CLOUDINARY_API_KEY'),
    api_secret=os.getenv('CLOUDINARY_API_SECRET'),
)
```

#### Option C: Temporary (for testing only)
- Files stored in `/tmp/` (will be reset on redeploy)
- Not suitable for production

**Recommendation:** Use S3 or Cloudinary for real deployment

---

### 2. PostgreSQL Backups

**Current Status:** ✅ PostgreSQL plugin includes backups

Railway automatically:
- Creates daily backups
- Retains 7-day history
- Can restore from backup

**To restore:**
1. Railway dashboard → PostgreSQL → Backups
2. Select backup date
3. Click "Restore"

---

### 3. Email Configuration (Important)

**Current Status:** ❌ Not tested

If you use email (newsletters, notifications):

```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587))
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', True)
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'noreply@fitblog.com')
```

Set in Railway Variables:
```env
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-specific-password
DEFAULT_FROM_EMAIL=noreply@fitblog.com
```

**For Gmail:** Use app-specific password, not account password

---

## 🔒 Security Considerations

### 1. SECRET_KEY Rotation
```bash
# Generate new SECRET_KEY periodically
python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```
Update in Railway Variables every 6 months

### 2. ALLOWED_HOSTS
```env
ALLOWED_HOSTS=fitblog.com,www.fitblog.com,fitblog.up.railway.app,localhost
```
Keep only actual domains you control

### 3. Database URL Protection
- Never commit `.env` file
- Use `.env.example` for template
- Railway auto-generates DATABASE_URL (don't expose it)

### 4. SSL/HTTPS
- ✅ Railway auto-provides SSL certificate
- ✅ settings.py configured for HTTPS
- Ensure: `SECURE_SSL_REDIRECT = True` (when not DEBUG)

### 5. CSRF Protection
- ✅ `CSRF_COOKIE_SECURE = True` (HTTPS only)
- ✅ `CSRF_COOKIE_HTTPONLY = True` (can't access from JS)

---

## ⚡ Performance Optimizations

### 1. Database Connection Pooling
✅ Already enabled in settings.py:
```python
DATABASES = {
    'default': dj_database_url.config(
        conn_max_age=600,  # 10 minutes
        conn_health_checks=True,
    )
}
```

### 2. Query Optimization
Add to views:
```python
from django.db.models import Prefetch, F, Count
from django.views.decorators.cache import cache_page

# Cache homepage for 1 hour
@cache_page(60 * 60)
def home(request):
    posts = Post.objects.filter(status='published').select_related('category').prefetch_related('comments')
    return render(request, 'blog/home.html', {'posts': posts})
```

### 3. Enable Caching
Add to settings.py:
```python
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}
```

### 4. Static Files Compression
✅ Already enabled:
```python
STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'
```

### 5. Database Query Limit
Add `settings.py`:
```python
DEBUG = False  # Disable query history in production
```

### 6. Gunicorn Workers
Increase in Procfile if needed:
```
web: gunicorn fitblog_config.wsgi --workers 4 --threads 2 --worker-class gthread --bind 0.0.0.0:$PORT
```

---

## 📊 Monitoring & Logging

### 1. Railway Monitoring
- CPU usage
- Memory usage
- Network I/O
- Deploy history
- Logs

**Access:** Railway dashboard → Project → Metrics

### 2. Application Logging
✅ Configured in settings.py:
```python
LOGGING = {
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
}
```

View logs:
```bash
railway logs
```

### 3. Error Tracking (Optional)
```bash
pip install sentry-sdk
```

```python
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

sentry_sdk.init(
    dsn=os.getenv('SENTRY_DSN'),
    integrations=[DjangoIntegration()],
    environment='production',
    traces_sample_rate=0.1,
)
```

---

## 🔧 Maintenance Tasks

### Weekly
- [ ] Check Railway logs for errors
- [ ] Monitor CPU/Memory usage
- [ ] Test email notifications

### Monthly
- [ ] Review and update dependencies:
  ```bash
  pip list --outdated
  pip install --upgrade [package]
  ```
- [ ] Check for security updates:
  ```bash
  pip install -U pip setuptools
  safety check
  ```

### Quarterly
- [ ] Rotate SECRET_KEY
- [ ] Review database size
- [ ] Optimize slow queries
- [ ] Update Django version (if minor update available)

---

## 🚀 Scaling Strategies

### If site gets slow:

#### Option 1: Increase RAM (Easy)
Railway → Project → Settings → Plan
- Start: Starter tier (512 MB)
- Scale up: Pro tier (1 GB or more)

#### Option 2: Add Celery for Background Tasks
```bash
pip install celery redis
```

#### Option 3: Add Redis Cache
Railway → Add Plugin → Redis

#### Option 4: Database Optimization
- Add indexes on frequently queried fields
- Archive old data
- Optimize N+1 queries

---

## 🐛 Common Issues & Fixes

### Issue 1: "Bad request" or "Disallowed host"
**Fix:** Check `ALLOWED_HOSTS` in Variables
```env
ALLOWED_HOSTS=fitblog.up.railway.app,yoursite.com,localhost
```

### Issue 2: Static files (CSS/JS) not loading
**Fix:** Check `collectstatic` in logs
```bash
railway logs | grep collectstatic
```

### Issue 3: Database migrations not running
**Fix:** Check Procfile release command
```
release: python manage.py migrate --noinput
```

### Issue 4: Upload files disappear after redeploy
**Fix:** Use S3 or Cloudinary (see Media Files Storage above)

### Issue 5: Site loads but admin is broken
**Fix:** Create new superuser
```bash
railway shell
python manage.py createsuperuser
```

---

## 📱 Frontend Integration

### CORS Configuration
Set in Railway Variables:
```env
CORS_ALLOWED_ORIGINS=https://yourfrontend.com,http://localhost:3000
```

### API Endpoints Available
```
GET  /api/categories/ - List all categories
GET  /api/posts/ - List all posts (paginated)
POST /chatbot/ask/ - Send message to chatbot
```

### Media URLs
```
https://fitblog.up.railway.app/media/blog_images/[filename]
https://fitblog.up.railway.app/media/category_icons/[filename]
```

---

## 🎯 Pre-Production Checklist

Before going live:

- [ ] Database backups configured (Railway default)
- [ ] Email sender configured
- [ ] Media storage (S3/Cloudinary) setup
- [ ] Custom domain pointing to Railway
- [ ] SSL certificate working (Railway auto)
- [ ] All sensitive data in environment variables
- [ ] Admin user created
- [ ] Database initialized with initial data
- [ ] Static files collecting successfully
- [ ] All endpoints tested
- [ ] Performance acceptable (<2 second response time)
- [ ] Error logging working
- [ ] Backup/restore tested

---

## 🔗 Useful Resources

- **Railway Docs:** https://docs.railway.app
- **Django Security:** https://docs.djangoproject.com/en/4.2/topics/security/
- **DRF Guide:** https://www.django-rest-framework.org/
- **PostgreSQL Tips:** https://www.postgresql.org/docs/
- **AWS S3 Setup:** https://docs.aws.amazon.com/s3/
- **Cloudinary:** https://cloudinary.com/documentation

---

## 📞 Getting Help

- **Railway Support:** https://railway.app/support
- **Django Community:** https://www.djangoproject.com/
- **Stack Overflow:** Search `django railway` or `django deployment`
- **Project Issues:** Check GitHub repository for known issues

