# -*- coding: utf-8 -*-
"""
Custom template filters for products app
"""

from django import template

register = template.Library()


@register.filter
def format_price(value):
    """
    Format price with thousand separator using dot (.)
    
    Examples:
        5000000 -> 5.000.000
        1500 -> 1.500
        100 -> 100
    """
    if value is None:
        return "0"
    
    try:
        # Convert to int if needed
        value = int(float(value))
        # Format with thousand separator
        return f"{value:,}".replace(",", ".")
    except (ValueError, TypeError):
        return str(value)


@register.filter
def event_type_label(value):
    """
    Convert event_type code to Vietnamese label
    
    Examples:
        'product_view' -> 'Xem sản phẩm'
        'review_submit' -> 'Gửi đánh giá'
        'rec_clicked' -> 'Nhấp gợi ý'
    """
    EVENT_LABELS = {
        'product_view': 'Xem sản phẩm',
        'product_click': 'Nhấp sản phẩm',
        'review_submit': 'Gửi đánh giá',
        'review_helpful': 'Đánh giá hữu ích',
        'rec_shown': 'Gợi ý hiển thị',
        'rec_clicked': 'Nhấp gợi ý',
        'rec_purchased': 'Mua gợi ý',
        'search': 'Tìm kiếm',
        'filter_apply': 'Áp dụng lọc',
        'sort_applied': 'Sắp xếp',
        'login': 'Đăng nhập',
        'logout': 'Đăng xuất',
        'register': 'Đăng ký',
        'profile_setup': 'Thiết lập hồ sơ',
        'profile_update': 'Cập nhật hồ sơ',
        'page_load': 'Tải trang',
        'api_call': 'Gọi API',
    }
    return EVENT_LABELS.get(value, value)
