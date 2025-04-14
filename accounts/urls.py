from django.urls import path
from . import views
from .views import CustomLoginView

urlpatterns = [
    path('register/', views.register, name='register'),
    path('setup-mfa/<int:device_id>/', views.setup_mfa, name='setup_mfa'),
    path('verify-token/', views.verify_token, name='verify_token'),
    path('home/', views.home, name='home'),  # Asegúrate de que esta línea esté presente
    path('login/', CustomLoginView.as_view(), name='login'),  # <-- esta línea
    path('logout/', views.custom_logout, name='logout'),
]
