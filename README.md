# 🥗 Fitblog - Django Nutrition & Fitness Blog

Full-stack Django blog về dinh dưỡng và thể hình với Messenger chatbot AI tích hợp, Ngrok tunnel và Colab LLM backend.

## ✨ Features

✅ **Blog System**
- Danh sách bài viết với pagination
- Chi tiết bài viết với bình luận
- Tìm kiếm và lọc theo danh mục
- Admin interface đầy đủ
- Lượt xem bài viết

✅ **Design**
- Màu mềm (soft pastels): Tím lavender, xanh nhạt, đỏ nhạt
- Animation mượt mà (fadeIn, slideUp, bounce, pulse)
- Responsive design (mobile-first)
- Gradient backgrounds
- Dark mode support

✅ **Chatbot Integration**
- Messenger widget góc phải (chat bubble)
- Real-time chat UI
- Tích hợp Colab LLM qua Ngrok
- Health check status
- Loading animation
- Error handling

✅ **Backend**
- Django 4.2
- Django REST Framework
- CORS middleware
- SQLite database
- Ngrok API integration

---

## 🚀 Quick Start

### 1️⃣ Clone & Setup

```bash
cd /home/hieuhome/CaoHoc/doanratruong/fitblog

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
# Username: admin
# Password: (your password)
```

### 2️⃣ Create Sample Data (Optional)

```bash
python manage.py shell
```

```python
from blog.models import Category, Post
from django.utils import timezone

# Create categories
cat_nutrition = Category.objects.create(
    name="Dinh Dưỡng",
    slug="dinh-duong",
    icon="🥗",
    color="#d1f0e8"
)

cat_fitness = Category.objects.create(
    name="Thể Hình",
    slug="the-hinh",
    icon="💪",
    color="#f5d0d0"
)

# Create post
Post.objects.create(
    title="Cơ Bản Về Protein - Chất Xây Dựng Cơ Bắp",
    slug="co-ban-protein",
    category=cat_nutrition,
    excerpt="Protein là gì? Tại sao nó quan trọng với thể hình?",
    content="""
# Protein là gì?

Protein là một trong 3 macronutrient quan trọng (cùng carbs và fat).

## Lợi ích của Protein

1. Xây dựng và sửa chữa cơ bắp
2. Tạo hormone và enzyme
3. Hỗ trợ hệ miễn dịch
4. ...

Hãy uống đủ protein mỗi ngày!
    """,
    author="Hinne 🥗",
    status="published",
    published_at=timezone.now(),
    tags="protein, nutrition, fitness"
)

exit()
```

### 3️⃣ Configure Ngrok URL

```bash
# In .env file
NGROK_LLM_API=https://xxxxx.ngrok-free.app/ask
```

Hoặc update via API:

```bash
curl -X POST http://localhost:8000/chatbot/update-ngrok/ \
  -H "Content-Type: application/json" \
  -d '{"ngrok_url": "https://xxxxx.ngrok-free.app/ask"}'
```

### 4️⃣ Run Server

```bash
python manage.py runserver
```

Truy cập:
- 🏠 Home: http://localhost:8000
- 📚 Blog: http://localhost:8000/blog
- ⚙️ Admin: http://localhost:8000/admin

---

## 📁 Project Structure

```
fitblog/
├── manage.py                          # Django CLI
├── requirements.txt                   # Dependencies
├── .env                              # Environment variables
├── setup.sh                          # Setup script
│
├── fitblog_config/                   # Django config
│   ├── settings.py                   # Settings
│   ├── urls.py                       # URL routing
│   └── wsgi.py                       # WSGI app
│
├── blog/                             # Blog app
│   ├── models.py                     # Post, Category, Comment, Newsletter
│   ├── views.py                      # Views (list, detail, home)
│   ├── urls.py                       # Blog URLs
│   ├── admin.py                      # Admin interface
│   └── migrations/
│
├── chatbot/                          # Chatbot app
│   ├── views.py                      # /api/chat/, /health/
│   ├── urls.py                       # Chatbot URLs
│   └── admin.py
│
├── templates/                        # Templates
│   ├── base.html                     # Base template
│   └── blog/
│       ├── home.html                 # Home page
│       ├── post_list.html            # Blog list
│       └── post_detail.html          # Post detail
│
└── static/                           # Static files
    ├── css/
    │   └── styles.css                # Global styles + animations
    └── js/
        └── messenger.js              # Chat widget (JS)
```

---

## 🔌 API Endpoints

### Chat Endpoint
```bash
POST /chatbot/api/chat/
Content-Type: application/json

{
  "query": "Bao nhiêu đạm có trong gà?"
}

Response:
{
  "success": true,
  "response": "Ức gà chứa khoảng 31g đạm trên 100g...",
  "timestamp": "2025-01-17T10:30:00.000000",
  "code": "LLM_SUCCESS"
}
```

### Health Check
```bash
GET /chatbot/health/

Response:
{
  "success": true,
  "status": "healthy",
  "message": "✅ Colab LLM online",
  "timestamp": "2025-01-17T10:30:00.000000"
}
```

### Update Ngrok URL
```bash
POST /chatbot/update-ngrok/
Content-Type: application/json

{
  "ngrok_url": "https://xxxxx.ngrok-free.app/ask"
}

Response:
{
  "success": true,
  "message": "✅ Ngrok URL cập nhật: https://xxxxx.ngrok-free.app/ask",
  "timestamp": "2025-01-17T10:30:00.000000"
}
```

---

## 🎨 Customization

### Color Palette (Soft)
Sửa trong `static/css/styles.css`:

```css
:root {
    --color-primary-light: #b39ddb;     /* Tím lavender */
    --color-primary-main: #ce93d8;      /* Tím nhạt */
    --color-primary-dark: #9c27b0;      /* Tím đậm */
    
    --color-secondary-light: #c8e6f5;   /* Xanh nhạt */
    --color-secondary-main: #7fc0d9;    /* Xanh trung bình */
    
    --color-accent-pink: #f5d0d0;       /* Đỏ nhạt */
    --color-accent-green: #d1f0e8;      /* Xanh nhạt/success */
}
```

### Messenger Widget Settings
Sửa trong `templates/base.html`:

```javascript
new MessengerWidget({
    apiUrl: '/chatbot/api/chat/',
    healthCheckUrl: '/chatbot/health/',
    botName: 'Hinne 🥗',
});
```

---

## 📝 Admin Interface

Đăng nhập: http://localhost:8000/admin

Features:
- ✏️ Tạo/sửa bài viết
- 📂 Quản lý danh mục
- 💬 Phê duyệt bình luận
- 📧 Quản lý subscribers

---

## 🌐 Publish to Web (Ngrok)

### Terminal 1: Run Django Server
```bash
source venv/bin/activate
python manage.py runserver 8000
```

### Terminal 2: Publish with Ngrok
```bash
ngrok http 8000
```

Output:
```
Forwarding    https://xxxxx.ngrok-free.app -> http://localhost:8000
```

Update Django settings nếu cần CORS:
```python
CORS_ALLOWED_ORIGINS = [
    "https://xxxxx.ngrok-free.app",
]
```

---

## 🤖 Colab Backend Integration

### Setup Colab (test2_router_base.ipynb)

Thêm vào cell cuối:

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from pydantic import BaseModel

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    query: str

@app.post("/ask")
async def ask(request: QueryRequest):
    """LLM endpoint"""
    answer = smart_ask(request.query)
    return {"answer": answer}

@app.get("/health")
async def health():
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000)
```

Chạy FastAPI:
```python
!pip install fastapi uvicorn -q
# Run above code
```

Expose qua Ngrok:
```python
!ngrok authtoken YOUR_TOKEN
!nohup ngrok http 5000 > ngrok.log 2>&1 &
import subprocess
result = subprocess.run(['curl', 'http://localhost:4040/api/tunnels'], capture_output=True, text=True)
import json
tunnels = json.loads(result.stdout)
print(tunnels['tunnels'][0]['public_url'])
```

Copy Ngrok URL vào `.env`:
```
NGROK_LLM_API=https://yyyyy.ngrok-free.app/ask
```

---

## ⚙️ Deployment

### Production Checklist

- [ ] `DEBUG=False` trong settings.py
- [ ] `SECRET_KEY` thay đổi
- [ ] `ALLOWED_HOSTS` cập nhật
- [ ] Database migrate
- [ ] Static files collect
- [ ] HTTPS enabled
- [ ] Environment variables secure

### Deploy to Heroku/Render/Railway

```bash
# Heroku
heroku create fitblog
git push heroku main

# Render
# Connect GitHub → Render → Deploy
```

---

## 🐛 Troubleshooting

### Chatbot không kết nối được Colab
1. Kiểm tra Ngrok URL có còn sống không
2. Kiểm tra Colab kernel còn chạy không
3. Check CORS settings
4. Xem logs: `/chatbot/health/`

### Database errors
```bash
python manage.py migrate --run-syncdb
```

### Static files không hiển thị
```bash
python manage.py collectstatic
```

### Migrations conflict
```bash
python manage.py showmigrations
python manage.py migrate app_name 0001
```

---

## 📚 Resources

- Django Docs: https://docs.djangoproject.com
- Ngrok: https://ngrok.com
- FastAPI: https://fastapi.tiangolo.com
- Tailwind CSS: https://tailwindcss.com

---

## 📄 License

MIT License - Feel free to use for personal & commercial projects

---

## 👨‍💻 Author

Made with ❤️ by Hinne AI

For more info: Check `fitblog_config/settings.py`
