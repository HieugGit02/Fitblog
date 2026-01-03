# -*- coding: utf-8 -*-
"""
Management command: Xóa expired sessions và UserProfiles liên quan
Dùng: python manage.py cleanup_expired_sessions
"""

from django.core.management.base import BaseCommand
from django.contrib.sessions.models import Session
from django.utils import timezone
from products.models import UserProfile, RecommendationLog
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Xóa expired sessions và UserProfiles để tiết kiệm dữ liệu trên Railway'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Chỉ hiển thị số lượng sẽ xóa mà không xóa thực tế'
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        # Bước 1: Xóa expired sessions từ Django
        expired_sessions = Session.objects.filter(expire_date__lt=timezone.now())
        sessions_count = expired_sessions.count()

        if sessions_count == 0:
            self.stdout.write(
                self.style.SUCCESS('✓ Không có expired sessions')
            )
        else:
            if dry_run:
                self.stdout.write(
                    self.style.WARNING(f'⚠️  [DRY RUN] Sẽ xóa {sessions_count} expired sessions')
                )
            else:
                expired_sessions.delete()
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Đã xóa {sessions_count} expired sessions')
                )

        # Bước 2: Xóa UserProfiles không có session tương ứng
        all_profiles = UserProfile.objects.all()
        orphan_profiles = []
        
        for profile in all_profiles:
            try:
                # Kiểm tra session có tồn tại không
                Session.objects.get(session_key=profile.session_id)
            except Session.DoesNotExist:
                orphan_profiles.append(profile.id)
        
        orphan_count = len(orphan_profiles)

        if orphan_count == 0:
            self.stdout.write(
                self.style.SUCCESS('✓ Không có UserProfiles mồ côi (orphan)')
            )
        else:
            if dry_run:
                self.stdout.write(
                    self.style.WARNING(
                        f'⚠️  [DRY RUN] Sẽ xóa {orphan_count} UserProfiles mồ côi\n'
                        f'     (vì sessions liên quan đã hết hạn)'
                    )
                )
            else:
                # Xóa associated logs trước
                logs_count = RecommendationLog.objects.filter(
                    user_profile_id__in=orphan_profiles
                ).delete()[0]
                
                # Xóa orphan profiles
                UserProfile.objects.filter(id__in=orphan_profiles).delete()
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✓ Đã xóa {orphan_count} UserProfiles mồ côi\n'
                        f'  - {orphan_count} profiles\n'
                        f'  - {logs_count} recommendation logs'
                    )
                )

        # Tóm tắt
        total_deleted = sessions_count + orphan_count
        if total_deleted == 0 and not dry_run:
            self.stdout.write(
                self.style.SUCCESS('\n✓ Database sạch sẽ, không có dữ liệu cũ')
            )
        elif dry_run and total_deleted > 0:
            self.stdout.write(
                self.style.WARNING(f'\nℹ️  Tổng cộng sẽ xóa: {total_deleted} items')
            )
        elif not dry_run and total_deleted > 0:
            self.stdout.write(
                self.style.SUCCESS(f'\n✓ Tổng cộng đã xóa: {total_deleted} items')
            )
