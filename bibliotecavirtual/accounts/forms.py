from django.contrib.auth.forms import UserCreationForm
from .models import User

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'password1', 'password2')

from django import forms

class FiltroLibroForm(forms.Form):
    titulo = forms.CharField(required=False, label='Título')
    autor = forms.CharField(required=False, label='Autor')
    categoria = forms.CharField(required=False, label='Categoría')

