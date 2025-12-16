# ⚡ Quick Start: Deploy Fitblog to Railway trong 5 phút

## 🎯 Yêu cầu
- ✅ GitHub account
- ✅ Railway account (https://railway.app)
- ✅ Code đã push lên GitHub

---

## 🚀 5 Bước Deploy

### Step 1️⃣: Đảm bảo code sạch trên GitHub
```bash
cd ~g/Fitblog

# Kiểm tra migrations
python manage.py showmigrations

# Nếu có thay đổi models
python manage.py makemigrations
python manage.py migrate

# Thêm và commit
git add .
git commit -m "Final update before Railway deployment"
git push origin main
```

---

### Step 2️⃣: Tạo dự án trên Railway
1. Truy cập https://railway.app
2. **Login with GitHub**
3. Click **"New Project"**
4. Chọn **"Deploy from GitHub repo"**
5. Chọn repo **"Fitblog"**
6. Railway auto-detect Dockerfile → Click **Deploy**

💡 Chờ 2-3 phút để Railway build image

---

### Step 3️⃣: Thêm PostgreSQL Database
1. Trong Railway dashboard, click **"+ Add Service"**
2. Chọn **"Add Plugin"** → **"PostgreSQL"**
3. Railway tự tạo database
4. Xem `DATABASE_URL` trong PostgreSQL plugin variables

✅ Django sẽ tự sử dụng `DATABASE_URL` từ `settings.py`

---

### Step 4️⃣: Cấu hình Environment Variables
1. Click vào **Web service** (Django app)
2. Mở tab **"Variables"**
3. Thêm các biến sau:

```
SECRET_KEY=dj-insecure-gen-secret-key-here-min-50-chars-or-use-python-command
DEBUG=False
ALLOWED_HOSTS=*.railway.app,localhost
NGROK_LLM_API=https://your-ngrok-url.ngrok-free.app/ask
CORS_ALLOWED_ORIGINS=https://fitblog.up.railway.app,http://localhost:3000
```

**Để tạo SECRET_KEY an toàn:**
```bash
python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```
Copy output và paste vào `SECRET_KEY`

---

### Step 5️⃣: Deploy & Test
1. Railway tự **auto-deploy** khi bạn thêm variables
2. Xem **Deployments** tab → chờ status thành **SUCCESS** ✅
3. Kiểm tra logs nếu có error:
   ```
   Deployments → (Click deployment) → View Logs
   ```

4. Truy cập website:
   ```
   https://fitblog-production.up.railway.app
   ```

5. **Tạo superuser** (optional - để vào /admin/)
   - Vào Railway web terminal hoặc CLI
   - Chạy: `python manage.py createsuperuser`

---

## ✅ Verification Checklist

Sau khi deploy xong, kiểm tra:

- [ ] Website load không lỗi: `https://fitblog-xxx.up.railway.app`
- [ ] Admin page: `https://fitblog-xxx.up.railway.app/admin/`
- [ ] Blog homepage: `https://fitblog-xxx.up.railway.app/`
- [ ] API categories: `https://fitblog-xxx.up.railway.app/api/categories/`
- [ ] API posts: `https://fitblog-xxx.up.railway.app/api/posts/`
- [ ] CSS/JS load (kiểm tra DevTools)
- [ ] Database connected (admin có data)
- [ ] Chatbot widget load (góc phải bottom)

---

## 🐛 Nếu có lỗi

| Lỗi | Giải pháp |
|-----|----------|
| "ModuleNotFoundError: django" | Check requirements.txt, Railway tự chạy pip install |
| "ImproperlyConfigured" | Set SECRET_KEY & DEBUG=False in Variables |
| Database connection error | Verify DATABASE_URL auto-set, check PostgreSQL service |
| Static files (CSS) không load | Collectstatic chạy automatically, check logs |
| 502 Bad Gateway | Check logs, restart deployment, increase RAM |

---

## 🌐 Custom Domain (Optional)

Muốn dùng domain riêng (e.g., fitblog.com) thay vì fitblog-xxx.up.railway.app:

1. Railway → Project → **Settings** → **Domains**
2. Click **"Add Domain"**
3. Thêm domain của bạn
4. Cập nhật DNS:
   - Thêm CNAME record chỉ đến Railway domain
   - VD: `fitblog.com CNAME fitblog-production.up.railway.app`
5. Cập nhật `ALLOWED_HOSTS` trong Variables:
   ```
   ALLOWED_HOSTS=fitblog.com,www.fitblog.com,fitblog-xxx.up.railway.app
   ```

---

## 💾 Railway Storage

| Thành phần | Storage | Ghi chú |
|-----------|---------|--------|
| Database | PostgreSQL (persistent) | ✅ Data lưu vĩnh viễn |
| Static files | `/staticfiles/` (persistent) | ✅ Collectstatic lưu vĩnh viễn |
| Media files | `/media/` (ephemeral) | ⚠️ Reset khi redeploy - cần S3 |
| Code | Git (auto-pulled) | ✅ Từ GitHub |

---

## 🔄 Auto-Deploy từ GitHub

**Railway tự động deploy mỗi khi:**
- Push lên branch được link (default: main)
- Revert về deployment cũ

**Manual deploy:**
- Railway dashboard → Deployments → Click → Redeploy

---

## 📚 File Hữu ích

Trong repo Fitblog:
- [`RAILWAY_DEPLOYMENT.md`](./RAILWAY_DEPLOYMENT.md) - Hướng dẫn chi tiết đầy đủ
- [`PROJECT_CHECKLIST.md`](./PROJECT_CHECKLIST.md) - Checklist cấu hình
- [`.env.example`](./.env.example) - Environment variables template
- [`Procfile`](./Procfile) - Production commands
- [`Dockerfile`](./Dockerfile) - Container configuration
- [`requirements.txt`](./requirements.txt) - Python dependencies

---

## 🎉 Xong!

Fitblog của bạn giờ đang chạy trên Railway! 🚀

### Bước tiếp theo:
1. Test tất cả features trên production
2. Cấu hình email (nếu cần)
3. Thiết lập custom domain
4. Monitor logs & performance
5. Setup S3 cho media files (nếu có upload ảnh)

---

## 📞 Cần giúp?

- Railway Docs: https://docs.railway.app
- Django Docs: https://docs.djangoproject.com
- Issues? Check Logs: Railway → Deployments → View Logs

