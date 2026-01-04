# -*- coding: utf-8 -*-
"""
Authentication views for user registration, login, and logout.
"""

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.conf import settings
from .auth_forms import CustomUserCreationForm, UserLoginForm


# ========== REGISTER VIEW ==========
@require_http_methods(["GET", "POST"])
def register(request):
    """
    User registration page
    
    URL: /auth/register/
    Template: auth/register.html
    
    GET: Show registration form
    POST: Create user & auto-create UserProfile via signal
    
    Features:
    - Email validation (must be unique)
    - Username validation
    - Password strength check
    - Auto-create UserProfile with signal
    - Auto-login after registration
    """
    # If already logged in, redirect to profile
    if request.user.is_authenticated:
        return redirect('products:user_profile_view')
    
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            # Create user (this triggers signal to auto-create UserProfile)
            user = form.save()
            
            messages.success(
                request,
                f'✅ Chào mừng {user.username}! Đăng kí thành công. Vui lòng hoàn thành hồ sơ của bạn.'
            )
            
            # Auto-login after registration
            login(request, user)
            
            # Redirect to profile setup
            return redirect('products:user_profile_setup')
        else:
            # Show form errors
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"❌ {field}: {error}")
    else:
        form = CustomUserCreationForm()
    
    context = {
        'form': form,
        'title': '✍️ Đăng Kí Tài Khoản',
        'page_title': 'Tạo Tài Khoản Fitblog Của Bạn',
    }
    return render(request, 'auth/register.html', context)


# ========== LOGIN VIEW ==========
@require_http_methods(["GET", "POST"])
def login_view(request):
    """
    User login page
    
    URL: /auth/login/
    Template: auth/login.html
    
    GET: Show login form
    POST: Authenticate user with username or email
    
    Features:
    - Login with username OR email
    - Remember me checkbox (Session expiry control)
    - Redirect to next page or profile
    - Error handling
    """
    # If already logged in, redirect to profile
    if request.user.is_authenticated:
        return redirect('products:user_profile_view')
    
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username_or_email = form.cleaned_data['username']
            password = form.cleaned_data['password']
            remember_me = form.cleaned_data.get('remember_me', False)
            
            # Try to authenticate with username
            user = authenticate(request, username=username_or_email, password=password)
            
            # If username fails, try with email
            if not user:
                try:
                    user_obj = User.objects.get(email=username_or_email)
                    user = authenticate(
                        request,
                        username=user_obj.username,
                        password=password
                    )
                except User.DoesNotExist:
                    user = None
            
            if user is not None:
                login(request, user)
                
                # Set session expiry based on remember_me
                if not remember_me:
                    # Session expires on browser close
                    request.session.set_expiry(0)
                else:
                    # Session expires after SESSION_COOKIE_AGE seconds
                    request.session.set_expiry(settings.SESSION_COOKIE_AGE)
                
                messages.success(
                    request,
                    f'✅ Đăng nhập thành công! Chào mừng {user.username}'
                )
                
                # Redirect to next page or profile
                next_page = request.GET.get('next')
                if next_page:
                    return redirect(next_page)
                return redirect('products:user_profile_view')
            else:
                messages.error(
                    request,
                    '❌ Tên đăng nhập/email hoặc mật khẩu không đúng!'
                )
    else:
        form = UserLoginForm()
    
    context = {
        'form': form,
        'title': '🔓 Đăng Nhập',
        'page_title': 'Đăng Nhập Vào Tài Khoản Fitblog',
    }
    return render(request, 'auth/login.html', context)


# ========== LOGOUT VIEW ==========
@login_required(login_url='auth:login')
@require_http_methods(["GET", "POST"])
def logout_view(request):
    """
    User logout page
    
    URL: /auth/logout/
    Template: auth/logout_confirm.html
    
    GET: Show logout confirmation page
    POST: Confirm logout and destroy session
    
    Features:
    - Confirmation before logout
    - Session cleanup
    - Redirect to home
    """
    if request.method == 'POST':
        username = request.user.username
        logout(request)
        messages.success(request, f'✅ Đã đăng xuất. Tạm biệt!')
        return redirect('blog:home')
    
    context = {
        'title': '🚪 Xác Nhận Đăng Xuất',
        'page_title': 'Bạn có chắc muốn đăng xuất?',
    }
    return render(request, 'auth/logout_confirm.html', context)
