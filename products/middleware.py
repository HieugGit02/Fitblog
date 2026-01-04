# -*- coding: utf-8 -*-
"""
Middleware để xử lý session setup cho UserProfile
"""

from django.utils.deprecation import MiddlewareMixin
from products.models import UserProfile


class UserProfileMiddleware(MiddlewareMixin):
    """
    Middleware để xử lý UserProfile (KHÔNG tự động tạo)
    
    Changes:
    - Chỉ tạo session, không tạo UserProfile tự động
    - UserProfile chỉ tạo khi user submit form setup
    - Cập nhật last_activity nếu profile tồn tại
    
    Lợi ích:
    - Admin chỉ show profile có data (user đã setup)
    - Không đầy lên profile trống
    - Cleaner data
    """
    
    def process_request(self, request):
        """
        Called for each request - before view is processed
        
        NOTE: Deprecated in favor of authentication-based approach
        """
        # DEPRECATED: No longer creating UserProfile from session_id
        # UserProfile is now linked to User model via OneToOneField
        # This middleware remains for backward compatibility only
        
        return None
