# -*- coding: utf-8 -*-
"""
Authentication views for user registration, login, and logout.
Includes rate limiting for brute force protection and password reset flow.
"""

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.conf import settings
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.urls import reverse
from django.core.mail import send_mail
from datetime import timedelta
import logging

from .auth_forms import CustomUserCreationForm, UserLoginForm, PasswordResetRequestForm, PasswordResetForm
from .auth_throttle import login_throttle
from .models import PasswordResetToken

logger = logging.getLogger(__name__)



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
    User login page with rate limiting protection.
    
    URL: /auth/login/
    Template: auth/login.html
    
    GET: Show login form
    POST: Authenticate user with username or email
    
    Features:
    - Login with username OR email
    - Remember me checkbox (Session expiry control)
    - Redirect to next page or profile
    - Rate limiting (max 5 attempts in 15 minutes)
    - Account lockout after too many failures
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
            
            # ===== RATE LIMITING CHECK =====
            allowed, error_message = login_throttle.allow_attempt(request, username_or_email)
            if not allowed:
                messages.error(request, error_message)
                context = {
                    'form': form,
                    'title': '🔓 Đăng Nhập',
                    'page_title': 'Đăng Nhập Vào Tài Khoản Fitblog',
                }
                return render(request, 'auth/login.html', context)
            
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
                # ===== CLEAR THROTTLE ON SUCCESS =====
                login_throttle.clear_attempts(request, username_or_email)
                login(request, user)
                
                # Set session expiry based on remember_me
                if not remember_me:
                    # Session expires on browser close
                    request.session.set_expiry(0)
                else:
                    # Session expires after SESSION_COOKIE_AGE seconds
                    request.session.set_expiry(settings.SESSION_COOKIE_AGE)
                
                # Different messages for admin and regular users
                if user.is_staff or user.is_superuser:
                    messages.success(
                        request,
                        f'✅ Đã đăng nhập với tư cách admin - Chào mừng {user.username}'
                    )
                else:
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
                # ===== RECORD FAILURE =====
                login_throttle.record_failure(request, username_or_email)
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
        is_admin = request.user.is_staff or request.user.is_superuser
        logout(request)
        
        # Different messages for admin and regular users
        if is_admin:
            messages.success(request, f'✅ Admin đã đăng xuất. Tạm biệt!')
        else:
            messages.success(request, f'✅ Đã đăng xuất. Tạm biệt!')
        return redirect('blog:home')
    
    context = {
        'title': '🚪 Xác Nhận Đăng Xuất',
        'page_title': 'Bạn có chắc muốn đăng xuất?',
    }
    return render(request, 'auth/logout_confirm.html', context)


# ============================================================================
# PASSWORD RESET VIEWS
# ============================================================================

@require_http_methods(["GET", "POST"])
def password_reset_request(request):
    """
    Request password reset via email.
    
    URL: /auth/password-reset/
    Template: auth/password_reset_request.html
    
    GET: Show email form
    POST: Generate reset token and send email
    
    Features:
    - User enters email
    - System generates unique token
    - Email sent with reset link
    - Token expires in 1 hour
    """
    # If already logged in, redirect to profile
    if request.user.is_authenticated:
        return redirect('products:user_profile_view')
    
    if request.method == 'POST':
        form = PasswordResetRequestForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            
            try:
                user = User.objects.get(email=email)
                
                # Generate unique token
                token = get_random_string(length=64)
                expires_at = timezone.now() + timedelta(hours=1)
                
                # Create reset token
                reset_token = PasswordResetToken.objects.create(
                    user=user,
                    token=token,
                    expires_at=expires_at
                )
                
                # Build reset link
                reset_link = request.build_absolute_uri(
                    reverse('products:password_reset_confirm', args=[token])
                )
                
                # Send email
                try:
                    send_mail(
                        subject='🔐 Yêu cầu Reset Mật Khẩu Fitblog',
                        message=f'''
Xin chào {user.username},

Bạn đã yêu cầu reset mật khẩu cho tài khoản Fitblog của mình.

Nhấp vào link dưới đây để reset mật khẩu (link hết hạn sau 1 giờ):
{reset_link}

Nếu bạn không yêu cầu reset mật khẩu, hãy bỏ qua email này.

---
Fitblog Team
                        ''',
                        html_message=f'''
<html>
    <body>
        <h2>🔐 Yêu cầu Reset Mật Khẩu</h2>
        <p>Xin chào <strong>{user.username}</strong>,</p>
        <p>Bạn đã yêu cầu reset mật khẩu cho tài khoản Fitblog của mình.</p>
        <p>
            <a href="{reset_link}" style="background-color: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">
                Nhấp để Reset Mật Khẩu
            </a>
        </p>
        <p><small>Link hết hạn sau 1 giờ</small></p>
        <hr>
        <p>Nếu bạn không yêu cầu reset mật khẩu, hãy bỏ qua email này.</p>
        <p>Fitblog Team</p>
    </body>
</html>
                        ''',
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[email],
                        fail_silently=False,
                    )
                    
                    logger.info(f'Password reset email sent to {email}')
                    messages.success(
                        request,
                        f'✅ Email reset mật khẩu đã được gửi tới {email}. Vui lòng kiểm tra hộp thư của bạn (kiểm tra cả spam).'
                    )
                    
                    # Redirect to login with message
                    return redirect('products:login')
                
                except Exception as e:
                    logger.error(f'Failed to send password reset email: {e}')
                    messages.error(
                        request,
                        '❌ Lỗi gửi email. Vui lòng thử lại sau.'
                    )
            
            except User.DoesNotExist:
                # Don't reveal if email exists for security
                messages.success(
                    request,
                    '✅ Nếu email này tồn tại trong hệ thống, link reset sẽ được gửi. Vui lòng kiểm tra email của bạn.'
                )
                return redirect('products:login')
    
    else:
        form = PasswordResetRequestForm()
    
    context = {
        'form': form,
        'title': '🔐 Reset Mật Khẩu',
        'page_title': 'Yêu Cầu Reset Mật Khẩu',
    }
    return render(request, 'auth/password_reset_request.html', context)


@require_http_methods(["GET", "POST"])
def password_reset_confirm(request, token):
    """
    Confirm password reset with new password.
    
    URL: /auth/password-reset/<token>/
    Template: auth/password_reset_confirm.html
    
    GET: Show password form
    POST: Update password and mark token as used
    
    Features:
    - Validate token exists and not expired
    - Accept new password
    - Update user password
    - Mark token as used
    - Redirect to login
    """
    # If already logged in, redirect to profile
    if request.user.is_authenticated:
        return redirect('products:user_profile_view')
    
    try:
        reset_token = PasswordResetToken.objects.get(token=token)
    except PasswordResetToken.DoesNotExist:
        messages.error(
            request,
            '❌ Link reset mật khẩu không hợp lệ hoặc đã hết hạn.'
        )
        return redirect('products:password_reset_request')
    
    # Check if token is valid
    if not reset_token.is_valid:
        messages.error(
            request,
            '❌ Link reset mật khẩu đã hết hạn. Vui lòng yêu cầu link mới.'
        )
        return redirect('products:password_reset_request')
    
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            password = form.cleaned_data['password1']
            
            # Update user password
            user = reset_token.user
            user.set_password(password)
            user.save()
            
            # Mark token as used
            reset_token.mark_as_used()
            
            logger.info(f'Password reset successful for user {user.username}')
            messages.success(
                request,
                '✅ Mật khẩu đã được reset thành công! Bây giờ bạn có thể đăng nhập với mật khẩu mới.'
            )
            return redirect('products:login')
    else:
        form = PasswordResetForm()
    
    context = {
        'form': form,
        'title': '🔐 Đặt Mật Khẩu Mới',
        'page_title': 'Nhập Mật Khẩu Mới',
        'token': token,
    }
    return render(request, 'auth/password_reset_confirm.html', context)
