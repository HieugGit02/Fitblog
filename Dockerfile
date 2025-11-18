# 1. Dùng Python chính chủ từ Docker Hub (Ổn định)
FROM python:3.11-slim

# 2. Cài đặt các thư viện hệ thống cần thiết cho Postgres và biên dịch
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 3. Thiết lập thư mục làm việc
WORKDIR /app

# 4. Copy file requirements và cài đặt thư viện
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy toàn bộ code vào
COPY . .

# 6. Thu thập static files (cho Whitenoise)
# Tạo thư mục staticfiles để tránh lỗi permission
RUN mkdir -p staticfiles
# Chạy lệnh collectstatic (cần set dummy secret key để lệnh này chạy đc khi build)
RUN SECRET_KEY=dummy python manage.py collectstatic --noinput

# 7. Mở cổng 8000 (hoặc cổng mà Railway cấp, thường là biến $PORT)
ENV PORT=8080
EXPOSE 8080

# 8. Lệnh chạy server (Sửa 'fitblog_config' thành tên project của bạn trong wsgi.py)
CMD python manage.py migrate && gunicorn fitblog_config.wsgi:application --bind 0.0.0.0:$PORT