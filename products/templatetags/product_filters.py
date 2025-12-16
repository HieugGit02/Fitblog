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
