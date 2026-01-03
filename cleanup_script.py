# -*- coding: utf-8 -*-
"""
Script để chạy cleanup định kỳ (dùng cho crontab hoặc Railway scheduler)
Thêm vào crontab: 0 0 * * * cd /path/to/project && python manage.py cleanup_expired_sessions
(Chạy hàng ngày lúc 0 giờ sáng)

Hoặc dùng Railway scheduler (thêm vào Procfile):
cleanup: python manage.py cleanup_expired_sessions
"""

import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fitblog_config.settings')
django.setup()

from django.contrib.sessions.models import Session
from django.utils import timezone
from products.models import UserProfile, RecommendationLog

def cleanup_expired_sessions():
    """Xóa expired sessions và UserProfiles liên quan"""
    
    # Xóa expired sessions
    expired_sessions = Session.objects.filter(expire_date__lt=timezone.now())
    sessions_count = expired_sessions.count()
    expired_sessions.delete()
    
    # Xóa UserProfiles mồ côi (orphan)
    all_profiles = UserProfile.objects.all()
    orphan_profiles = []
    
    for profile in all_profiles:
        try:
            Session.objects.get(session_key=profile.session_id)
        except Session.DoesNotExist:
            orphan_profiles.append(profile.id)
    
    orphan_count = len(orphan_profiles)
    if orphan_count > 0:
        RecommendationLog.objects.filter(user_profile_id__in=orphan_profiles).delete()
        UserProfile.objects.filter(id__in=orphan_profiles).delete()
    
    total = sessions_count + orphan_count
    print(f"✓ Đã xóa {sessions_count} expired sessions + {orphan_count} orphan profiles = {total} items")
    return total

if __name__ == '__main__':
    cleanup_expired_sessions()

