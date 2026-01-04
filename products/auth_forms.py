# -*- coding: utf-8 -*-
"""
Authentication forms for user registration and login.
"""

from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError


class CustomUserCreationForm(UserCreationForm):
    """
    Custom registration form with email field.
    
    Fields:
    - username: Unique username
    - email: Email address (must be unique)
    - first_name: Optional
    - last_name: Optional
    - password1: Password
    - password2: Confirm password
    """
    email = forms.EmailField(
        label="Email",
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nhập email của bạn',
        })
    )
    first_name = forms.CharField(
        label="Tên (Họ)",
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ví dụ: John'
        })
    )
    last_name = forms.CharField(
        label="Tên (Đệm + Tên)",
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ví dụ: Doe'
        })
    )
    
    password1 = forms.CharField(
        label="Mật khẩu",
        required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nhập mật khẩu (ít nhất 8 ký tự)',
            'autocomplete': 'new-password',
        })
    )
    password2 = forms.CharField(
        label="Xác nhận mật khẩu",
        required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nhập lại mật khẩu',
            'autocomplete': 'new-password',
        })
    )
    
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Chọn tên đăng nhập (không dấu, không khoảng trắng)'
            }),
        }
    
    def clean_email(self):
        """Validate that email is unique"""
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email=email).exists():
            raise ValidationError("❌ Email này đã được sử dụng! Hãy chọn email khác.")
        return email
    
    def clean_username(self):
        """Validate username"""
        username = self.cleaned_data.get('username')
        if username and User.objects.filter(username=username).exists():
            raise ValidationError("❌ Tên đăng nhập này đã được sử dụng! Hãy chọn tên khác.")
        if username and len(username) < 3:
            raise ValidationError("❌ Tên đăng nhập phải có ít nhất 3 ký tự.")
        return username
    
    def clean_password1(self):
        """Validate password strength"""
        password = self.cleaned_data.get('password1')
        if password and len(password) < 8:
            raise ValidationError("❌ Mật khẩu phải có ít nhất 8 ký tự.")
        return password
    
    def clean_password2(self):
        """Validate password confirmation"""
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2:
            if password1 != password2:
                raise ValidationError("❌ Hai mật khẩu không khớp!")
        return password2


class UserLoginForm(forms.Form):
    """
    Custom login form that allows login with username or email.
    
    Fields:
    - username: Username or email
    - password: Password
    - remember_me: Keep login session
    """
    username = forms.CharField(
        label="Tên đăng nhập hoặc Email",
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nhập tên đăng nhập hoặc email',
            'autocomplete': 'username',
        })
    )
    password = forms.CharField(
        label="Mật khẩu",
        required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nhập mật khẩu',
            'autocomplete': 'current-password',
        })
    )
    remember_me = forms.BooleanField(
        label="Nhớ tôi trên máy này",
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
        })
    )
