# 🔐 Hướng Dẫn Thêm Đăng Nhập/Đăng Kí Vào Fitblog

## 📋 Phân Tích Tình Hình Hiện Tại

### ❌ **Hệ Thống Cũ (Session-Based)**
- Người dùng **không cần đăng nhập**
- UserProfile được tạo từ `session_id` (cookie)
- Không lưu vào Django User model
- Vấn đề: Không có tính xác thực, dữ liệu mất khi xóa cookie

### ✅ **Hệ Thống Mới (Authentication-Based)**
- Người dùng **phải đăng kí/đăng nhập**
- Lưu vào **Django User model** (username, email, password)
- UserProfile liên kết với **User model** qua ForeignKey
- Lợi ích: Secure, persistent, proper authentication

---

## 🎯 Kế Hoạch Triển Khai

### **Phase 1: Update Database Models**
1. Thêm `user` ForeignKey vào UserProfile
2. Tạo signal tự động tạo UserProfile khi User được tạo

### **Phase 2: Tạo Authentication Views**
1. **Đăng Kí** (`/auth/register/`) - Tạo User & UserProfile
2. **Đăng Nhập** (`/auth/login/`) - Django authentication
3. **Đăng Xuất** (`/auth/logout/`)
4. **Thay Đổi Mật Khẩu** (optional)

### **Phase 3: Update Navigation/Header**
1. Thêm **Login/Register buttons** ở góc phải header (khi chưa login)
2. Hiển thị **username** và **dropdown menu** khi đã login (khi đã login)
3. Thêm link đến Profile, Settings, Logout

### **Phase 4: Update Existing Views**
1. Thêm `@login_required` decorators
2. Update recommendation logic (dùng User thay Session)
3. Migrate existing session-based users (optional)

---

## 📊 Database Changes

### **Before (Session-Based)**
```python
class UserProfile(models.Model):
    session_id = CharField(unique=True)  # ← Session tracking
    age = IntegerField(null=True)
    weight_kg = FloatField(null=True)
    # ...
```

### **After (Authentication-Based)**
```python
class UserProfile(models.Model):
    user = ForeignKey(User, on_delete=models.CASCADE)  # ← NEW!
    # Remove: session_id = CharField(unique=True)  ← DELETE!
    age = IntegerField(null=True)
    weight_kg = FloatField(null=True)
    # ...
```

---

## 📁 Các File Cần Tạo/Sửa

### **New Files to Create:**
```
products/
├── auth_views.py              # ← NEW: Login/Register/Logout views
├── auth_forms.py              # ← NEW: CustomUserCreationForm
├── signals.py                 # ← NEW: Auto-create UserProfile signal
└── migrations/
    └── 0005_userprofile_user.py  # ← NEW: Add user ForeignKey

templates/
├── auth/                       # ← NEW: Authentication templates
│   ├── register.html
│   ├── login.html
│   ├── logout_confirm.html
│   └── password_change.html
│
└── partials/
    └── user_menu.html         # ← NEW: Reusable user menu component
```

### **Files to Modify:**
```
products/
├── models.py                  # Update UserProfile model
├── urls.py                    # Add auth URLs
├── views.py                   # Update recommendation logic
├── forms.py                   # Update forms (remove session-based)
├── middleware.py              # Remove UserProfileMiddleware (no longer needed)
└── apps.py                    # Register signal

templates/
├── base.html                  # Update header with login/user menu
└── products/
    └── user_profile_view.html # Update to use user.userprofile
```

---

## 🔧 Implementation Steps

### **Step 1: Update UserProfile Model**

```python
# products/models.py
from django.contrib.auth.models import User

class UserProfile(models.Model):
    # ✅ NEW: Link to Django User
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
        verbose_name="Người dùng"
    )
    
    # ❌ REMOVE: session_id = CharField(...)
    
    age = models.IntegerField(null=True, blank=True)
    weight_kg = models.FloatField(null=True, blank=True)
    height_cm = models.FloatField(null=True, blank=True)
    gender = models.CharField(...)
    goal = models.CharField(...)
    # ... rest of fields
    
    def __str__(self):
        return f"Profile: {self.user.username}"
    
    class Meta:
        verbose_name_plural = "User Profiles"
```

---

### **Step 2: Create Signal (Auto-create UserProfile)**

```python
# products/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserProfile

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Auto-create UserProfile when User is created
    """
    if created:
        UserProfile.objects.create(
            user=instance,
            goal='general-health'  # Default goal
        )

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """
    Save UserProfile when User is saved
    """
    if hasattr(instance, 'profile'):
        instance.profile.save()

# Register signals in apps.py:
# from django.apps import AppConfig

# class ProductsConfig(AppConfig):
#     name = 'products'
#     
#     def ready(self):
#         import products.signals
```

---

### **Step 3: Create Authentication Forms**

```python
# products/auth_forms.py
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import UserProfile

class CustomUserCreationForm(UserCreationForm):
    """
    Register form - Create User with email
    """
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    first_name = forms.CharField(
        label="Tên",
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    last_name = forms.CharField(
        label="Họ",
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    password1 = forms.CharField(
        label="Mật khẩu",
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    password2 = forms.CharField(
        label="Xác nhận mật khẩu",
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
        }
    
    def clean_email(self):
        """Check if email already exists"""
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email này đã được sử dụng!")
        return email


class UserLoginForm(forms.Form):
    """
    Login form
    """
    username = forms.CharField(
        label="Tên người dùng hoặc Email",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nhập tên đăng nhập hoặc email'
        })
    )
    password = forms.CharField(
        label="Mật khẩu",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nhập mật khẩu'
        })
    )
    remember_me = forms.BooleanField(
        label="Nhớ tôi",
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
```

---

### **Step 4: Create Authentication Views**

```python
# products/auth_views.py
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from .auth_forms import CustomUserCreationForm, UserLoginForm

# ========== REGISTER VIEW ==========
@require_http_methods(["GET", "POST"])
def register(request):
    """
    User registration page
    URL: /auth/register/
    
    GET: Show registration form
    POST: Create user & profile
    """
    if request.user.is_authenticated:
        return redirect('products:user_profile_view')
    
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            # Create user
            user = form.save()
            
            # UserProfile auto-created by signal
            messages.success(request, f'✅ Đăng kí thành công! Chào mừng {user.username}')
            
            # Auto-login after registration
            login(request, user)
            return redirect('products:user_profile_view')
        else:
            messages.error(request, '❌ Đăng kí thất bại! Vui lòng kiểm tra lại thông tin.')
    else:
        form = CustomUserCreationForm()
    
    context = {
        'form': form,
        'title': 'Đăng Kí Tài Khoản',
    }
    return render(request, 'auth/register.html', context)


# ========== LOGIN VIEW ==========
@require_http_methods(["GET", "POST"])
def login_view(request):
    """
    User login page
    URL: /auth/login/
    
    GET: Show login form
    POST: Authenticate user
    """
    if request.user.is_authenticated:
        return redirect('products:user_profile_view')
    
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username_or_email = form.cleaned_data['username']
            password = form.cleaned_data['password']
            remember_me = form.cleaned_data.get('remember_me', False)
            
            # Try to authenticate with username first, then email
            user = authenticate(request, username=username_or_email, password=password)
            
            if not user:
                # Try with email
                try:
                    user_obj = User.objects.get(email=username_or_email)
                    user = authenticate(request, username=user_obj.username, password=password)
                except User.DoesNotExist:
                    user = None
            
            if user is not None:
                login(request, user)
                
                # Set session expiry if "remember me" is checked
                if remember_me:
                    request.session.set_expiry(settings.SESSION_COOKIE_AGE)
                else:
                    request.session.set_expiry(0)  # Session expires on browser close
                
                messages.success(request, f'✅ Đăng nhập thành công! Chào mừng {user.username}')
                
                # Redirect to next page or profile
                next_page = request.GET.get('next', 'products:user_profile_view')
                return redirect(next_page)
            else:
                messages.error(request, '❌ Tên đăng nhập hoặc mật khẩu không đúng!')
    else:
        form = UserLoginForm()
    
    context = {
        'form': form,
        'title': 'Đăng Nhập',
    }
    return render(request, 'auth/login.html', context)


# ========== LOGOUT VIEW ==========
@login_required(login_url='auth:login')
@require_http_methods(["GET", "POST"])
def logout_view(request):
    """
    User logout
    URL: /auth/logout/
    """
    if request.method == 'POST':
        logout(request)
        messages.success(request, '✅ Đã đăng xuất')
        return redirect('blog:home')
    
    return render(request, 'auth/logout_confirm.html', {
        'title': 'Xác Nhận Đăng Xuất'
    })
```

---

### **Step 5: Update URLs**

```python
# products/urls.py
from django.urls import path
from . import auth_views, views

app_name = 'products'

auth_patterns = [
    path('auth/register/', auth_views.register, name='register'),
    path('auth/login/', auth_views.login_view, name='login'),
    path('auth/logout/', auth_views.logout_view, name='logout'),
]

product_patterns = [
    path('products/', views.product_list, name='product_list'),
    path('products/<slug:slug>/', views.product_detail, name='product_detail'),
    path('products/setup/', views.user_profile_setup, name='user_profile_setup'),
    path('products/profile/', views.user_profile_view, name='user_profile_view'),
    # ... other urls
]

urlpatterns = auth_patterns + product_patterns
```

---

### **Step 6: Update Base Template (Header with Login/User Menu)**

```django-html
<!-- templates/base.html -->

<header>
    <div class="container">
        <!-- ... logo ... -->
        
        <!-- User Menu - TOP RIGHT CORNER -->
        <div class="user-menu">
            {% if user.is_authenticated %}
                <!-- LOGGED IN: Show user dropdown -->
                <div class="user-dropdown">
                    <button class="user-btn" id="user-dropdown-toggle">
                        <span class="user-icon">👤</span>
                        <span class="username">{{ user.username }}</span>
                        <span class="dropdown-arrow">▼</span>
                    </button>
                    
                    <ul class="dropdown-menu" id="user-dropdown-menu">
                        <li>
                            <a href="{% url 'products:user_profile_view' %}">
                                📋 Hồ Sơ Cá Nhân
                            </a>
                        </li>
                        <li>
                            <a href="{% url 'products:user_profile_setup' %}">
                                ⚙️ Cập Nhật Thông Tin
                            </a>
                        </li>
                        <li class="divider"></li>
                        <li>
                            <form method="post" action="{% url 'auth:logout' %}">
                                {% csrf_token %}
                                <button type="submit" class="logout-btn">
                                    🚪 Đăng Xuất
                                </button>
                            </form>
                        </li>
                    </ul>
                </div>
            {% else %}
                <!-- NOT LOGGED IN: Show login/register buttons -->
                <div class="auth-buttons">
                    <a href="{% url 'auth:login' %}" class="btn-login">
                        🔓 Đăng Nhập
                    </a>
                    <a href="{% url 'auth:register' %}" class="btn-register">
                        ✍️ Đăng Kí
                    </a>
                </div>
            {% endif %}
        </div>
    </div>
</header>

<style>
.user-menu {
    position: absolute;
    top: 20px;
    right: 20px;
}

.auth-buttons {
    display: flex;
    gap: 10px;
}

.btn-login, .btn-register {
    padding: 8px 16px;
    border-radius: 4px;
    text-decoration: none;
    font-weight: 600;
}

.btn-login {
    background: #f0f0f0;
    color: #333;
    border: 2px solid #999;
}

.btn-register {
    background: #4CAF50;
    color: white;
    border: 2px solid #4CAF50;
}

.user-dropdown {
    position: relative;
}

.user-btn {
    background: #f0f0f0;
    border: none;
    padding: 8px 16px;
    border-radius: 4px;
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: 8px;
}

.dropdown-menu {
    position: absolute;
    top: 100%;
    right: 0;
    background: white;
    border: 1px solid #ddd;
    border-radius: 4px;
    list-style: none;
    padding: 0;
    margin: 8px 0 0 0;
    min-width: 200px;
    display: none;
    z-index: 1000;
}

.dropdown-menu.active {
    display: block;
}

.dropdown-menu li {
    border-bottom: 1px solid #f0f0f0;
}

.dropdown-menu li:last-child {
    border-bottom: none;
}

.dropdown-menu a, .logout-btn {
    display: block;
    padding: 12px 16px;
    color: #333;
    text-decoration: none;
    width: 100%;
    text-align: left;
    background: none;
    border: none;
    cursor: pointer;
    font-size: 14px;
}

.dropdown-menu a:hover, .logout-btn:hover {
    background: #f5f5f5;
}

.divider {
    height: 8px;
    background: #f0f0f0;
}
</style>

<script>
// Toggle user dropdown
document.getElementById('user-dropdown-toggle').addEventListener('click', function() {
    const menu = document.getElementById('user-dropdown-menu');
    menu.classList.toggle('active');
});

// Close dropdown when clicking outside
document.addEventListener('click', function(event) {
    if (!event.target.closest('.user-dropdown')) {
        document.getElementById('user-dropdown-menu').classList.remove('active');
    }
});
</script>
```

---

### **Step 7: Create Registration Template**

```django-html
<!-- templates/auth/register.html -->
{% extends 'base.html' %}

{% block title %}Đăng Kí - Fitblog{% endblock %}

{% block content %}
<div class="auth-container">
    <div class="auth-card">
        <h2>✍️ Đăng Kí Tài Khoản</h2>
        <p>Tạo tài khoản mới để nhận gợi ý cá nhân hóa</p>
        
        {% if messages %}
            <div class="messages">
                {% for message in messages %}
                    <div class="alert alert-{{ message.tags }}">{{ message }}</div>
                {% endfor %}
            </div>
        {% endif %}
        
        <form method="post" class="auth-form">
            {% csrf_token %}
            
            {{ form.username }}
            {% if form.username.errors %}
                <span class="error">{{ form.username.errors }}</span>
            {% endif %}
            
            {{ form.email }}
            {% if form.email.errors %}
                <span class="error">{{ form.email.errors }}</span>
            {% endif %}
            
            {{ form.first_name }}
            {{ form.last_name }}
            
            {{ form.password1 }}
            {% if form.password1.errors %}
                <span class="error">{{ form.password1.errors }}</span>
            {% endif %}
            
            {{ form.password2 }}
            {% if form.password2.errors %}
                <span class="error">{{ form.password2.errors }}</span>
            {% endif %}
            
            <button type="submit" class="btn-submit">Đăng Kí</button>
        </form>
        
        <p class="auth-link">
            Đã có tài khoản? <a href="{% url 'auth:login' %}">Đăng nhập tại đây</a>
        </p>
    </div>
</div>
{% endblock %}

<style>
.auth-container {
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 60vh;
    margin: 40px 0;
}

.auth-card {
    background: white;
    border: 1px solid #ddd;
    border-radius: 8px;
    padding: 40px;
    max-width: 500px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.auth-card h2 {
    margin-top: 0;
    margin-bottom: 10px;
}

.auth-form {
    display: flex;
    flex-direction: column;
    gap: 16px;
}

.auth-form input {
    padding: 10px 12px;
    border: 1px solid #ccc;
    border-radius: 4px;
    font-size: 14px;
}

.btn-submit {
    background: #4CAF50;
    color: white;
    padding: 12px;
    border: none;
    border-radius: 4px;
    font-weight: 600;
    cursor: pointer;
}

.btn-submit:hover {
    background: #45a049;
}

.auth-link {
    text-align: center;
    margin-top: 20px;
}

.auth-link a {
    color: #4CAF50;
    text-decoration: none;
}
</style>
```

---

### **Step 8: Create Login Template**

```django-html
<!-- templates/auth/login.html -->
{% extends 'base.html' %}

{% block title %}Đăng Nhập - Fitblog{% endblock %}

{% block content %}
<div class="auth-container">
    <div class="auth-card">
        <h2>🔓 Đăng Nhập</h2>
        
        {% if messages %}
            <div class="messages">
                {% for message in messages %}
                    <div class="alert alert-{{ message.tags }}">{{ message }}</div>
                {% endfor %}
            </div>
        {% endif %}
        
        <form method="post" class="auth-form">
            {% csrf_token %}
            
            {{ form.username }}
            {% if form.username.errors %}
                <span class="error">{{ form.username.errors }}</span>
            {% endif %}
            
            {{ form.password }}
            {% if form.password.errors %}
                <span class="error">{{ form.password.errors }}</span>
            {% endif %}
            
            <label class="remember-me">
                {{ form.remember_me }}
                Nhớ tôi
            </label>
            
            <button type="submit" class="btn-submit">Đăng Nhập</button>
        </form>
        
        <p class="auth-link">
            Chưa có tài khoản? <a href="{% url 'auth:register' %}">Đăng kí tại đây</a>
        </p>
    </div>
</div>
{% endblock %}
```

---

## 📊 Comparison: Before vs After

| Feature | Before (Session) | After (Auth) |
|---------|-----------------|------------|
| **Header Menu** | Chỉ "Hồ Sơ" link | Login/Register buttons + User dropdown |
| **User Data** | Anonymous, session-based | Registered, database-backed |
| **Data Persistence** | Expires with session | Permanent (until deleted) |
| **Personalization** | Weak (session tracking) | Strong (user account) |
| **Security** | Low (no authentication) | High (password hashing) |
| **UserProfile Link** | session_id (CharField) | user (ForeignKey) |
| **Recommendation** | Session-based | User-based |

---

## ⚠️ Important: Migration Strategy

### **Option 1: Keep Both Systems (Recommended)**
- New users use Authentication
- Existing session users still work
- Migrate gradually

### **Option 2: Full Migration**
- Create data migration to convert session_id to user
- Requires matching session data with users

### **Option 3: Fresh Start**
- Remove session-based system
- New users must register
- Faster implementation

---

## 🚀 Implementation Order

1. **First**: Update UserProfile model (add user ForeignKey)
2. **Second**: Create signals.py
3. **Third**: Create auth_forms.py & auth_views.py
4. **Fourth**: Update products/urls.py
5. **Fifth**: Create auth templates (register, login)
6. **Sixth**: Update base.html header
7. **Seventh**: Test everything
8. **Eighth**: Run migrations

---

## ✅ Checklist

- [ ] Update UserProfile model
- [ ] Create signals.py
- [ ] Create auth forms
- [ ] Create auth views
- [ ] Update URLs
- [ ] Create templates
- [ ] Update base.html header
- [ ] Test registration
- [ ] Test login
- [ ] Test logout
- [ ] Test profile access
- [ ] Deploy

---

**Bạn muốn tôi bắt đầu triển khai? Hãy cho tôi biết!** 🚀
