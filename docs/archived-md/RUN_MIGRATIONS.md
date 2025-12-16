# 🔧 Chạy Migrations trên Railway PostgreSQL

## Option 1: Dùng Railway CLI (Nhanh nhất)

```bash
# Kiểm tra Railway CLI đã install?
which railway

# Nếu chưa, cài:
curl -fsSL https://railway.app/install.sh | sh

# Login Railway
railway login

# Link tới project
railway link

# Chạy migrations
railway run python manage.py migrate --noinput

# Tạo superuser (nếu cần)
railway run python manage.py createsuperuser
```

## Option 2: Trigger từ UI (Web Dashboard)

1. Vào https://railway.app → Project
2. Chọn Service (web)
3. Vào **Deployments**
4. Click deployment mới nhất
5. Nếu có **"Railway Shell"** button → click → terminal mở
6. Chạy:
   ```bash
   python manage.py migrate --noinput
   python manage.py createsuperuser
   ```
7. Exit shell

## Option 3: Trigger Redeploy (Procfile sẽ chạy release)

```bash
cd project-root

# Commit trigger
git add .
git commit -m "Trigger migrations"
git push origin main
```

Sau đó Railway tự:
- Pull code
- Chạy: `release: python manage.py migrate --noinput` (Procfile)
- Chạy web server

## Kiểm tra migrations đã chạy?

- Vào Railway PostgreSQL logs (nên thấy "relation blog_post..." không có lỗi)
- Hoặc truy cập website → không thấy "ProgrammingError"

