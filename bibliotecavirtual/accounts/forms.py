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

from .models import Resena

class ResenaForm(forms.ModelForm):
    class Meta:
        model = Resena
        fields = ['calificacion', 'comentario']
        widgets = {
            'calificacion': forms.RadioSelect,
            'comentario': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }

from django.shortcuts import render, get_object_or_404, redirect
from .models import Resena
from .forms import ResenaForm

def editar_resena(request, resena_id):
    # Obtén la reseña que se va a editar
    resena = get_object_or_404(Resena, id=resena_id)

    # Si la solicitud es POST, es porque el usuario está enviando el formulario
    if request.method == 'POST':
        form = ResenaForm(request.POST, instance=resena)  # Le pasas la instancia de la reseña
        if form.is_valid():
            form.save()  # Guarda los cambios
            return redirect('detalle_libro', libro_id=resena.libro.id)  # Redirige a la página del libro
    else:
        form = ResenaForm(instance=resena)  # Si es un GET, se muestra el formulario con los datos actuales

    return render(request, 'editar_resena.html', {'form': form, 'resena': resena})
