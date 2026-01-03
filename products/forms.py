# -*- coding: utf-8 -*-
"""
Forms để người dùng điền UserProfile (không cần đăng nhập)
"""

from django import forms
from django.core.exceptions import ValidationError
from .models import UserProfile


class UserProfileForm(forms.ModelForm):
    """
    Form để người dùng điền thông tin cá nhân (tuổi, cân, cao, mục tiêu, v.v.)
    
    Ví dụ:
        form = UserProfileForm(data=request.POST, instance=user_profile)
        if form.is_valid():
            form.save()
    """
    
    class Meta:
        model = UserProfile
        fields = [
            'age',
            'weight_kg',
            'height_cm',
            'goal',
            'activity_level',
            'preferred_supplement_types',
            'dietary_restrictions',
        ]
        widgets = {
            'age': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ví dụ: 30',
                'min': '16',
                'max': '120',
                'required': True,
            }),
            'weight_kg': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ví dụ: 75',
                'min': '30',
                'max': '200',
                'step': '0.1',
                'required': True,
            }),
            'height_cm': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ví dụ: 175',
                'min': '100',
                'max': '250',
                'step': '0.1',
                'required': True,
            }),
            'goal': forms.Select(attrs={
                'class': 'form-control',
                'required': True,
            }),
            'activity_level': forms.Select(attrs={
                'class': 'form-control',
                'required': True,
            }),
            'preferred_supplement_types': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Ví dụ: whey, creatine, vitamins (phân tách bằng dấu phẩy)',
                'rows': 2,
            }),
            'dietary_restrictions': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Ví dụ: vegan, gluten-free, dairy-free (phân tách bằng dấu phẩy)',
                'rows': 2,
            }),
        }

    def clean_age(self):
        """Validate tuổi"""
        age = self.cleaned_data.get('age')
        if age:
            if age < 16:
                raise ValidationError("Tuổi phải từ 16 trở lên")
            if age > 120:
                raise ValidationError("Tuổi không hợp lệ")
        return age

    def clean_weight_kg(self):
        """Validate cân nặng"""
        weight = self.cleaned_data.get('weight_kg')
        if weight:
            if weight < 30:
                raise ValidationError("Cân nặng phải từ 30kg trở lên")
            if weight > 200:
                raise ValidationError("Cân nặng không hợp lệ")
        return weight

    def clean_height_cm(self):
        """Validate chiều cao"""
        height = self.cleaned_data.get('height_cm')
        if height:
            if height < 100:
                raise ValidationError("Chiều cao phải từ 100cm trở lên")
            if height > 250:
                raise ValidationError("Chiều cao không hợp lệ")
        return height

    def save(self, commit=True):
        """
        Override save để tính BMI & TDEE tự động
        """
        instance = super().save(commit=False)
        
        # Tính BMI
        instance.calculate_bmi()
        
        # Tính TDEE
        instance.calculate_tdee()
        
        if commit:
            instance.save()
        
        return instance


class QuickProfileForm(forms.ModelForm):
    """
    Form rút gọn - chỉ hỏi các field thiết yếu
    Dùng cho setup lần đầu/quick setup
    """
    
    class Meta:
        model = UserProfile
        fields = [
            'age',
            'weight_kg',
            'height_cm',
            'goal',
            'activity_level',
        ]
        widgets = {
            'age': forms.NumberInput(attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'Tuổi của bạn',
                'min': '16',
                'max': '120',
                'required': True,
            }),
            'weight_kg': forms.NumberInput(attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'Cân nặng (kg)',
                'min': '30',
                'max': '200',
                'step': '0.1',
                'required': True,
            }),
            'height_cm': forms.NumberInput(attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'Chiều cao (cm)',
                'min': '100',
                'max': '250',
                'step': '0.1',
                'required': True,
            }),
            'goal': forms.Select(attrs={
                'class': 'form-control form-control-lg',
                'required': True,
            }),
            'activity_level': forms.Select(attrs={
                'class': 'form-control form-control-lg',
                'required': True,
            }),
        }

    def save(self, commit=True):
        """Tính BMI & TDEE tự động"""
        instance = super().save(commit=False)
        instance.calculate_bmi()
        instance.calculate_tdee()
        
        if commit:
            instance.save()
        
        return instance
