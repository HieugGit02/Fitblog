from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('blog/', views.PostListView.as_view(), name='post_list'),
    path('blog/<slug:slug>/', views.PostDetailView.as_view(), name='post_detail'),
    path('category/<slug:slug>/', views.CategoryDetailView.as_view(), name='category_detail'),
    path('categories/', views.CategoriesView.as_view(), name='categories'),
    path('subscribe/', views.SubscribeView.as_view(), name='subscribe'),
]
