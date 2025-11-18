FROM python:3.11-slim

# Cài thư viện hệ thống
RUN apt-get update && apt-get install -y libpq-dev gcc && rm -rf /var/lib/apt/lists/*

# Thiết lập thư mục
WORKDIR /app

# Cài requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy code
COPY . .

# Tạo thư mục static và chạy collectstatic (dùng key giả để build)
RUN mkdir -p staticfiles
RUN SECRET_KEY=dummy-build-key python manage.py collectstatic --noinput

# Mở cổng và chạy server
ENV PORT=8000
EXPOSE 8000
CMD gunicorn fitblog_config.wsgi:application --bind 0.0.0.0:$PORT