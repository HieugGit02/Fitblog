# -*- coding: utf-8 -*-
"""
Rate Limiting (Throttling) for login attempts
Prevent brute force attacks by tracking failed login attempts
"""

from django.core.cache import cache
from django.utils import timezone
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)

# ============================================================================
# LOGIN THROTTLE CLASS
# ============================================================================

class LoginThrottle:
    """
    Tracks login attempts and locks account after too many failures.
    
    Rules:
    - Max 5 failed attempts within 15 minutes
    - After 5 failures: Lock for 15 minutes
    - Attempts tracked by IP + username/email combo
    - Clean attempts on successful login
    
    Usage:
        throttle = LoginThrottle()
        if not throttle.allow_attempt(request, username):
            return error_response("Too many attempts. Try again in 15 minutes")
        
        if login_failed:
            throttle.record_failure(request, username)
        else:
            throttle.clear_attempts(request, username)
    """
    
    MAX_ATTEMPTS = 5                    # Max failed attempts
    LOCKOUT_TIME = 15 * 60              # 15 minutes in seconds
    ATTEMPT_WINDOW = 15 * 60            # 15 minutes to track attempts
    
    def _get_client_ip(self, request):
        """Get client IP address from request"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def _get_cache_key(self, ip, username_or_email, key_type='attempts'):
        """Generate cache key for throttle tracking"""
        # key_type: 'attempts' or 'lockout'
        return f'login_throttle:{key_type}:{ip}:{username_or_email}'
    
    def allow_attempt(self, request, username_or_email):
        """
        Check if user is allowed to attempt login
        
        Returns:
            (bool, str): (allowed, error_message)
        """
        ip = self._get_client_ip(request)
        lockout_key = self._get_cache_key(ip, username_or_email, 'lockout')
        attempts_key = self._get_cache_key(ip, username_or_email, 'attempts')
        
        # Check if account is locked
        lockout_time = cache.get(lockout_key)
        if lockout_time:
            remaining = int(lockout_time - timezone.now().timestamp())
            if remaining > 0:
                return False, f'❌ Quá nhiều lần đăng nhập thất bại. Vui lòng thử lại sau {remaining} giây.'
            else:
                # Lockout expired, remove it
                cache.delete(lockout_key)
        
        # Check attempt count
        attempts = cache.get(attempts_key, 0)
        if attempts >= self.MAX_ATTEMPTS:
            # Lock the account
            lockout_timestamp = (timezone.now() + timedelta(seconds=self.LOCKOUT_TIME)).timestamp()
            cache.set(lockout_key, lockout_timestamp, self.LOCKOUT_TIME)
            return False, f'❌ Tài khoản bị khóa do quá nhiều lần thất bại. Vui lòng thử lại sau {self.LOCKOUT_TIME // 60} phút.'
        
        return True, ''
    
    def record_failure(self, request, username_or_email):
        """Record a failed login attempt"""
        ip = self._get_client_ip(request)
        attempts_key = self._get_cache_key(ip, username_or_email, 'attempts')
        
        # Increment attempt counter
        attempts = cache.get(attempts_key, 0)
        attempts += 1
        cache.set(attempts_key, attempts, self.ATTEMPT_WINDOW)
        
        logger.warning(
            f'Failed login attempt: {ip} - {username_or_email} (Attempt {attempts}/{self.MAX_ATTEMPTS})'
        )
        
        return attempts
    
    def clear_attempts(self, request, username_or_email):
        """Clear failed attempts on successful login"""
        ip = self._get_client_ip(request)
        attempts_key = self._get_cache_key(ip, username_or_email, 'attempts')
        lockout_key = self._get_cache_key(ip, username_or_email, 'lockout')
        
        cache.delete(attempts_key)
        cache.delete(lockout_key)
        
        logger.info(f'Login successful: {ip} - {username_or_email}')


# ============================================================================
# GLOBAL THROTTLE INSTANCE
# ============================================================================

login_throttle = LoginThrottle()


# ============================================================================
# THROTTLE DECORATOR (for views)
# ============================================================================

def throttle_login_attempts(view_func):
    """
    Decorator to add throttling to login views.
    
    Usage:
        @throttle_login_attempts
        def login_view(request):
            ...
    """
    def wrapped_view(request, *args, **kwargs):
        if request.method == 'POST':
            username_or_email = request.POST.get('username', '')
            allowed, error_message = login_throttle.allow_attempt(request, username_or_email)
            
            if not allowed:
                from django.contrib import messages
                messages.error(request, error_message)
                return view_func(request, *args, **kwargs)  # Re-render form with error
        
        return view_func(request, *args, **kwargs)
    
    return wrapped_view
