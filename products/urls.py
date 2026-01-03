# -*- coding: utf-8 -*-
"""
URL routes for products app - REST API endpoints + Frontend pages
"""

from django.urls import path, include, re_path
from rest_framework.routers import DefaultRouter
from . import views

# Create router and register viewsets
router = DefaultRouter()
router.register(r'products', views.ProductViewSet, basename='product')
router.register(r'categories', views.ProductCategoryViewSet, basename='category')
router.register(r'reviews', views.ProductReviewViewSet, basename='review')

app_name = 'products'

# URL patterns
urlpatterns = [
    # API endpoints with router - prefix with /api/
    path('api/', include(router.urls)),
    
    # UserProfile setup pages - with products prefix
    path('products/setup/', views.user_profile_setup, name='user_profile_setup'),
    path('products/quick-setup/', views.user_profile_quick_setup, name='user_profile_quick_setup'),
    path('products/profile/', views.user_profile_view, name='user_profile_view'),
    path('products/profile/delete/', views.user_profile_delete, name='user_profile_delete'),
    path('products/profile/reset/', views.user_profile_reset, name='user_profile_reset'),
    
    # Frontend HTML pages - no /api/ prefix
    path('products/', views.product_list, name='product_list'),
    re_path(r'^products/(?P<slug>[\w\-\:\.%]+)/$', views.product_detail, name='product_detail'),
    
    # Tracking endpoint
    path('api/track-click/', views.track_product_click, name='track_product_click'),
]

# Example URLs:
# GET  /api/products/                    - API: List all products
# GET  /api/products/{id}/               - API: Product detail
# GET  /api/products/{id}/recommendations/ - API: Recommendations
# GET  /api/categories/                  - API: List categories
# GET  /api/reviews/                     - API: List reviews
#
# GET  /products/                        - HTML: Product listing page
# GET  /products/{slug}/                 - HTML: Product detail page
