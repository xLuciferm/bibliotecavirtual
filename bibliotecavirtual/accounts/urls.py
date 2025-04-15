from django.urls import path
from . import views
from .views import CustomLoginView, reserva_exitosa

urlpatterns = [
    path('register/', views.register, name='register'),
    path('setup-mfa/<int:device_id>/', views.setup_mfa, name='setup_mfa'),
    path('verify-token/', views.verify_token, name='verify_token'),
    path('home/', views.home, name='home'),
    path('login/', CustomLoginView.as_view(), name='login'),  # Cambié esta ruta
    path('logout/', views.custom_logout, name='logout'),
    path('catalogo/', views.catalogo_view, name='catalogo'),
    path('libro/<int:libro_id>/', views.detalle_libro_view, name='detalle_libro'),
    path('libro/reservar/<int:libro_id>/', views.reservar_libro, name='reservar_libro'),
    path('reserva-exitosa/<int:reserva_id>/', reserva_exitosa, name='reserva_exitosa'),
]