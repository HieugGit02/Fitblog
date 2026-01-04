# -*- coding: utf-8 -*-
"""
Admin customization để tách Admin Users và Customer Users
"""

from django.contrib import admin
from django.contrib.auth.models import User
from django.db.models import Q


class AdminUserFilter(admin.SimpleListFilter):
    """Filter users by group (Admin vs Customer)"""
    title = 'User Type'
    parameter_name = 'user_type'

    def lookups(self, request, model_admin):
        return (
            ('admin', 'Admin Users'),
            ('customer', 'Customer Users'),
            ('all', 'All Users'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'admin':
            return queryset.filter(groups__name='Admin')
        elif self.value() == 'customer':
            return queryset.filter(groups__name='Customer')
        elif self.value() == 'all':
            return queryset
        return queryset


class UserAdmin(admin.ModelAdmin):
    """
    Custom User Admin - hiển thị Admin & Customer tách riêng
    """
    list_display = [
        'username',
        'email',
        'user_type_display',
        'is_staff',
        'is_superuser',
        'date_joined',
        'last_login'
    ]
    list_filter = [AdminUserFilter, 'is_staff', 'is_superuser', 'is_active', 'date_joined']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    readonly_fields = ['date_joined', 'last_login']
    
    fieldsets = (
        ('Account Info', {
            'fields': ('username', 'email', 'password')
        }),
        ('Personal Info', {
            'fields': ('first_name', 'last_name')
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
            'classes': ('collapse',)
        }),
        ('Important Dates', {
            'fields': ('last_login', 'date_joined'),
            'classes': ('collapse',)
        }),
    )
    
    def user_type_display(self, obj):
        """Show user type based on group"""
        if obj.groups.filter(name='Admin').exists():
            return '👨‍💼 Admin'
        elif obj.groups.filter(name='Customer').exists():
            return '👤 Customer'
        else:
            return '❓ Unknown'
    user_type_display.short_description = 'User Type'
    
    def save_model(self, request, obj, form, change):
        """Auto-assign group when user is saved"""
        super().save_model(request, obj, form, change)
        
        # Remove from all groups first
        obj.groups.clear()
        
        # Assign group based on staff status
        from django.contrib.auth.models import Group
        
        if obj.is_staff or obj.is_superuser:
            admin_group = Group.objects.get_or_create(name='Admin')[0]
            obj.groups.add(admin_group)
        else:
            customer_group = Group.objects.get_or_create(name='Customer')[0]
            obj.groups.add(customer_group)


# Unregister default admin.UserAdmin và register custom
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
