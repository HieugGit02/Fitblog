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
        """
        # Tự động tạo session nếu chưa có
        if not request.session.session_key:
            request.session.create()
        
        session_id = request.session.session_key
        
        # Get UserProfile nếu tồn tại (không tạo mới)
        try:
            user_profile = UserProfile.objects.get(session_id=session_id)
            # Update last_activity nếu profile tồn tại
            user_profile.save(update_fields=['last_activity'])
        except UserProfile.DoesNotExist:
            # Không tạo profile ở đây
            # Chỉ tạo khi user submit form
            user_profile = None
        
        # Thêm vào request (có thể None)
        request.user_profile = user_profile
        
        return None
