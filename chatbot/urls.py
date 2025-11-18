from django.urls import path
from . import views

app_name = 'chatbot'

urlpatterns = [
    path('api/chat/', views.chat_api, name='chat_api'),
    path('health/', views.health_check, name='health_check'),
    path('update-ngrok/', views.update_ngrok_url, name='update_ngrok'),
]
