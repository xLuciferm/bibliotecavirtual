from django.contrib.auth.forms import UserCreationForm
from .models import User

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'password1', 'password2')

from django import forms
from django.utils import timezone
class ReservaForm(forms.Form):
    libro_id = forms.IntegerField(widget=forms.HiddenInput())
    titulo = forms.CharField(max_length=200, disabled=True)
    autor = forms.CharField(max_length=200, disabled=True)
    fecha_reserva = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        label='Fecha de reserva'
    )

    def clean_fecha_reserva(self):
        fecha = self.cleaned_data.get('fecha_reserva')
        if fecha < timezone.now().date():
            raise forms.ValidationError("La fecha de reserva no puede ser en el pasado.")
        return fecha
