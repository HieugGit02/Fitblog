# -*- coding: utf-8 -*-
"""
Django signals for products app.
Auto-create UserProfile when User is created.
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserProfile


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Signal handler: Auto-create UserProfile when User is created
    
    This signal fires when:
    1. User is created via Django admin
    2. User is created via signup form
    3. User is created via manage.py createsuperuser
    
    The new UserProfile will have:
    - user: ForeignKey to the new User
    - goal: 'general-health' (default)
    - age, weight_kg, height_cm: None (to be filled in setup page)
    """
    if created:
        UserProfile.objects.create(
            user=instance,
            goal='general-health'  # Default goal
        )
        print(f"✅ Created UserProfile for user: {instance.username}")


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """
    Signal handler: Save UserProfile when User is saved
    
    This ensures UserProfile is always saved along with User.
    """
    if hasattr(instance, 'profile'):
        instance.profile.save()
