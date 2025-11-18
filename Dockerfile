# 1. Dùng Python 3.11 chính chủ từ Docker Hub (Server này không bao giờ sập)
FROM python:3.11-slim

# 2. Cài đặt các thư viện hệ thống cần thiết để nối database
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 3. Thiết lập thư mục làm việc
WORKDIR /app

# 4. Copy file requirements và cài thư viện Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy toàn bộ code dự án vào
COPY . .

# 6. Chạy lệnh thu thập file tĩnh (CSS/JS)
# Tạo thư mục để tránh lỗi quyền hạn
RUN mkdir -p staticfiles
# Set biến môi trường ảo để lệnh collectstatic chạy được lúc build
RUN SECRET_KEY=dummy-key-for-build python manage.py collectstatic --noinput

# 7. Mở cổng (Railway sẽ tự map cổng này)
ENV PORT=8000
EXPOSE 8000

# 8. Lệnh khởi động server (Thay fitblog_config bằng tên thư mục chứa wsgi.py của bạn)
CMD gunicorn fitblog_config.wsgi:application --bind 0.0.0.0:$PORT