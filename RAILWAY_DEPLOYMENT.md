# 🚀 Hướng dẫn Deploy Fitblog lên Railway

## 📋 Kiểm tra trước khi deploy

### ✅ Dự án hiện tại đã chuẩn bị:
- ✅ Django 4.2 + DRF (Django REST Framework)
- ✅ Procfile cấu hình cho production
- ✅ Dockerfile đầy đủ
- ✅ requirements.txt có tất cả thư viện cần thiết
- ✅ runtime.txt: Python 3.11.5
- ✅ settings.py đã cấu hình DATABASE_URL, ALLOWED_HOSTS, White Noise cho static files
- ✅ .env.example có sẵn
- ✅ Cấu trúc thư mục hợp lý

---

## 🔧 Bước 1: Chuẩn bị Local (Trước khi push)

### 1.1 Kiểm tra toàn bộ migrations
```bash
cd /home/hieuhome/CaoHoc/doanratruong/fitblog/Fitblog

# Kiểm tra trạng thái migrations
python manage.py showmigrations

# Nếu có thay đổi models, tạo migration mới
python manage.py makemigrations

# Áp dụng migrations
python manage.py migrate
```

### 1.2 Test server local
```bash
python manage.py collectstatic --noinput
python manage.py runserver
# Truy cập: http://localhost:8000
```

### 1.3 Commit và push code lên GitHub
```bash
git add .
git commit -m "Prepare for Railway deployment"
git push origin main
```

---

## 🌐 Bước 2: Tạo dự án trên Railway

### 2.1 Đăng ký/Đăng nhập Railway
- Truy cập: https://railway.app
- Đăng nhập bằng GitHub
- Cho phép Railway kết nối với GitHub account

### 2.2 Tạo New Project
1. Click **"New Project"**
2. Chọn **"Deploy from GitHub repo"**
3. Chọn repo **"Fitblog"**
4. Railway sẽ tự detect Dockerfile hoặc Procfile

---

## 🗄️ Bước 3: Cấu hình PostgreSQL Database

### 3.1 Thêm PostgreSQL Plugin
Trong Railway dashboard của dự án:
1. Click **"+ Add Service"** → **"Add Plugin"**
2. Chọn **"PostgreSQL"**
3. Railway sẽ tự tạo database và set biến môi trường `DATABASE_URL`

### 3.2 Xác nhận DATABASE_URL
- Mở tab **"Variables"** của PostgreSQL service
- Sẽ thấy: `DATABASE_URL=postgresql://user:password@host:5432/database`
- **Không cần copy/paste**, Railway tự inject vào Django app

---

## 📝 Bước 4: Cấu hình Environment Variables

### 4.1 Đặt biến môi trường trong Railway
1. Vào project → Click vào **Web service** (Django app)
2. Mở tab **"Variables"**
3. Thêm các biến sau:

```env
# Django Settings (BẮTBUỘC)
SECRET_KEY=your-very-long-random-secret-key-min-50-characters-e63f8a7b9c2e4d1a9b8c7f6e5d4c3b2a1f0e9d8c7b6a5f4e3d2c1b0a9f8e7d6c5b4a3f2e1d0c9b8a7f6e5d4c3b2a
DEBUG=False

# Được tự động set bởi Railway (không cần thêm)
# DATABASE_URL=...

# ALLOWED_HOSTS (cần cập nhật sau khi biết domain)
ALLOWED_HOSTS=fitblog.up.railway.app,yoursite.com,localhost,127.0.0.1

# Chatbot (thay bằng Ngrok URL thực)
NGROK_LLM_API=https://your-ngrok-url.ngrok-free.app/ask

# CORS (tùy theo frontend domain)
CORS_ALLOWED_ORIGINS=https://fitblog.up.railway.app,http://localhost:3000

# Email (tùy chọn)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

### 4.2 Tạo SECRET_KEY an toàn
```bash
python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```
Copy output và paste vào `SECRET_KEY` variable

### 4.3 Xác định ALLOWED_HOSTS
- Mở **"Deployments"** → xem **domain mặc định** của Railway
- Nó sẽ là dạng: `fitblog-production.up.railway.app`
- Thêm vào `ALLOWED_HOSTS`

---

## 🔄 Bước 5: Migrations trên Railway

Railway sẽ **tự động chạy** commands trong Procfile release phase:
```
release: python manage.py migrate --noinput; python manage.py collectstatic --clear --noinput
```

**Nếu quay lại không thấy database được tạo:**

1. Vào **"Deployments"** → xem logs
2. Tìm lỗi database connection
3. Kiểm tra `DATABASE_URL` được set đúng

---

## 🚀 Bước 6: Deploy

### 6.1 Automatic Deploy
- Cứ mỗi lần push lên `main` branch → Railway **tự động deploy**
- Xem progress trong **"Deployments"** tab

### 6.2 Manual Deploy
Nếu cần deploy từ một branch khác hoặc rebuild:
1. Vào Railway dashboard
2. Click **"Redeploy"** nút

### 6.3 Kiểm tra Logs
```
Deployments → click deployment → Logs
```

---

## ✅ Bước 7: Test & Verify

### 7.1 Truy cập website
```
https://fitblog-production.up.railway.app
```

### 7.2 Truy cập Admin
```
https://fitblog-production.up.railway.app/admin/
```
**Tạo superuser:**
- Vào Railway Logs
- Chạy command:
```bash
python manage.py createsuperuser
```

### 7.3 Kiểm tra API endpoints
```bash
curl https://fitblog-production.up.railway.app/api/categories/
curl https://fitblog-production.up.railway.app/api/posts/
curl https://fitblog-production.up.railway.app/chatbot/
```

---

## 🐛 Troubleshooting

### ❌ Error: "ModuleNotFoundError: No module named 'django'"
**Giải pháp:**
- Kiểm tra `requirements.txt` đầy đủ
- Railway sẽ tự chạy `pip install -r requirements.txt`

### ❌ Error: "django.core.exceptions.ImproperlyConfigured"
**Giải pháp:**
- Kiểm tra `SECRET_KEY` được set trong Variables
- Kiểm tra `DEBUG=False`
- Kiểm tra `ALLOWED_HOSTS` chứa domain Railway

### ❌ Database connection error
**Giải pháp:**
- Kiểm tra PostgreSQL plugin được thêm
- Kiểm tra `DATABASE_URL` environment variable
- Xem logs: `Deployments → Logs`

### ❌ Static files (CSS/JS) không load
**Giải pháp:**
- Kiểm tra `collectstatic` chạy thành công trong logs
- Kiểm tra `STATIC_ROOT` và `STATIC_URL` trong settings.py
- settings.py đã cấu hình White Noise (✅ có sẵn)

### ❌ Media uploads không hoạt động
**Giải pháp:**
- Railway có **ephemeral filesystem** (xóa khi redeploy)
- Cần dùng S3 hoặc CloudinaryAPI
- Tạm thời có thể dùng `/tmp` (sẽ reset mỗi deploy)

---

## 📊 Hiệu năng & Monitoring

### Monitor trong Railway:
- CPU usage
- Memory usage
- Network I/O
- Deploy history

### Kiểm tra logs:
```
Deployments → Recent deployments → View logs
```

---

## 🔐 Security Checklist

- ✅ `DEBUG = False`
- ✅ `SECRET_KEY` ngẫu nhiên, dài ≥ 50 ký tự
- ✅ `ALLOWED_HOSTS` chỉ chứa domain thực
- ✅ `SECURE_SSL_REDIRECT = True` (settings.py đã có)
- ✅ `SESSION_COOKIE_SECURE = True` (settings.py đã có)
- ✅ `CSRF_COOKIE_SECURE = True` (settings.py đã có)
- ✅ Database URL không hard-code

---

## 💡 Tips & Best Practices

### 1. Tự động cleanup old deployments
Railway tự giữ lại 5 deployments gần nhất

### 2. Health check
Railway tự check nếu port 8000 đáp ứng requests

### 3. Scale up/down
Vào Railway dashboard → "Settings" → "Plan" → chọn dung lượng RAM/vCPU

### 4. Custom domain
Railway → Project → "Settings" → "Domains" → thêm domain riêng

### 5. Rollback to previous deployment
Deployments → click deployment cũ → "Rollback"

---

## 🎯 Tóm tắt lệnh cần chạy

```bash
# 1. Chuẩn bị local
cd /home/hieuhome/CaoHoc/doanratruong/fitblog/Fitblog
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser  # (tạo tài khoản admin)

# 2. Push lên GitHub
git add .
git commit -m "Ready for Railway deployment"
git push origin main

# 3. Railway sẽ tự:
# - Clone repo
# - Chạy collectstatic
# - Chạy migrate
# - Start server với gunicorn
```

---

## 📧 Liên hệ hỗ trợ

- Railway Docs: https://docs.railway.app
- Django Docs: https://docs.djangoproject.com
- DRF Docs: https://www.django-rest-framework.org

