from django.contrib.auth.forms import UserCreationForm
from .models import User

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'password1', 'password2')

from django import forms
from datetime import date

class ReservaForm(forms.Form):
    fecha_reserva = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        label='Fecha de reserva'
    )

    def clean_fecha_reserva(self):
        fecha = self.cleaned_data['fecha_reserva']
        if fecha < date.today():
            raise forms.ValidationError("La fecha de reserva no puede ser anterior a hoy.")
        return fecha
