from django.shortcuts import redirect
from django_otp.util import random_hex
from .forms import CustomUserCreationForm
import qrcode
from io import BytesIO
import base64
from django.shortcuts import render
from django_otp.plugins.otp_totp.models import TOTPDevice
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.contrib.auth import login

@login_required
def home(request):
    if not request.session.get('mfa_verified'):
        return redirect('verify_token')
    return render(request, 'accounts/home.html')

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            device = TOTPDevice.objects.create(
                user=user,
                name='default',
                confirmed=True,
                key=random_hex()
            )
            return redirect('setup_mfa', device.id)
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})

@login_required
def setup_mfa(request, device_id):
    device = TOTPDevice.objects.get(id=device_id)
    qr_url = device.config_url

    img = qrcode.make(qr_url)
    qr_image = BytesIO()
    img.save(qr_image, format='PNG')
    qr_image.seek(0)
    qr_base64 = base64.b64encode(qr_image.getvalue()).decode('utf-8')

    return render(request, 'accounts/setup_mfa.html', {
        'device': device,
        'qr_base64': qr_base64
    })

@login_required
def verify_token(request):
    if request.session.get('mfa_verified'):
        return redirect('home')

    if request.method == 'POST':
        token = request.POST.get('token')
        device = TOTPDevice.objects.filter(user=request.user, confirmed=True).first()

        if device and device.verify_token(token):
            request.session['mfa_verified'] = True
            next_url = request.GET.get('next')
            return redirect(next_url if next_url else 'home')
        else:
            return render(request, 'accounts/verify_token.html', {'error': 'Token inválido'})

    return render(request, 'accounts/verify_token.html')


from django.contrib.auth import login
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib.auth.views import LoginView

class CustomLoginView(LoginView):
    template_name = 'accounts/log.html'

    def form_valid(self, form):
        """Siempre redirige a verify_token después del login."""
        login(self.request, form.get_user())  # inicia sesión
        return redirect(reverse('verify_token'))  # ignora ?next=

# logout personalizado
from django.contrib.auth import logout

@login_required
def custom_logout(request):
    logout(request)
    return redirect('log')

from django.contrib.auth.decorators import login_required

@login_required
def catalogo_view(request):
    titulo = request.GET.get('titulo', '')
    autor = request.GET.get('autor', '')

    libros = Libro.objects.all()

    hay_busqueda = False

    if titulo or autor:
        hay_busqueda = True
        if titulo:
            libros = libros.filter(titulo__icontains=titulo)
        if autor:
            libros = libros.filter(autor__icontains=autor)

    return render(request, 'accounts/catalogo.html', {
        'libros': libros,
        'hay_busqueda': hay_busqueda
    })

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from django.core.exceptions import ValidationError
from .models import Libro, Reserva, Resena
from .forms import ResenaForm

@login_required
def detalle_libro_view(request, libro_id):
    libro = get_object_or_404(Libro, id=libro_id)
    resenas = libro.resenas.select_related('usuario').order_by('-fecha')
    form_resena = None

    # Recomendaciones completamente aleatorias, excluyendo el libro actual
    recomendaciones = Libro.objects.exclude(id=libro.id).order_by('?')[:4]

    if request.method == 'POST':
        form_resena = ResenaForm(request.POST)
        if form_resena.is_valid():
            resena = form_resena.save(commit=False)
            resena.usuario = request.user
            resena.libro = libro
            try:
                resena.full_clean()
                resena.save()
                messages.success(request, "Gracias por tu reseña.")
                return redirect('detalle_libro', libro_id=libro.id)
            except ValidationError:
                messages.error(request, "Ya has dejado una reseña para este libro.")
    else:
        if not Resena.objects.filter(usuario=request.user, libro=libro).exists():
            form_resena = ResenaForm()

    return render(request, 'accounts/detalle_libro.html', {
        'libro': libro,
        'resenas': resenas,
        'form_resena': form_resena,
        'recomendaciones': recomendaciones,
    })

from django.core.exceptions import ValidationError
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Libro, Reserva
from .forms import ReservaForm


@login_required
def reservar_libro(request, libro_id):
    libro = get_object_or_404(Libro, id=libro_id)

    # Verificar si el libro tiene stock disponible
    if libro.stock <= 0:
        messages.error(request, "Este libro no tiene stock disponible.")
        return redirect('catalogo')

    # Creamos una variable para saber si ya existe una reserva
    reserva_existente = Reserva.objects.filter(usuario=request.user, libro=libro,
                                               fecha_devolucion__isnull=True).exists()

    if request.method == 'POST':
        # Si ya tiene una reserva activa y está intentando hacer POST, mostramos error
        if reserva_existente:
            messages.error(request,
                           "Ya tienes este libro reservado. No puedes reservarlo nuevamente hasta que lo devuelvas.")
            form = ReservaForm()  # Inicializamos un formulario vacío para mostrar
        else:
            form = ReservaForm(request.POST)
            if form.is_valid():
                fecha_reserva = form.cleaned_data['fecha_reserva']
                reserva = Reserva(
                    usuario=request.user,
                    libro=libro,
                    fecha_de_reserva=fecha_reserva
                )
                try:
                    reserva.full_clean()
                    reserva.save()

                    # Reducir stock solo si se guardó correctamente
                    libro.stock -= 1
                    libro.save()

                    # Agregar mensaje de éxito
                    messages.success(request, f"Reserva exitosa del libro: {libro.titulo}")

                    return redirect('reserva_exitosa', reserva_id=reserva.id)

                except ValidationError as e:
                    mensaje = e.message_dict.get('__all__', ["Ocurrió un error al guardar la reserva."])[0]
                    messages.error(request, mensaje)
            else:
                messages.error(request, "Por favor corrige los errores en el formulario.")
    else:
        # Si ya tiene una reserva activa y está accediendo por GET, mostramos error
        if reserva_existente:
            messages.error(request,
                           "Ya tienes este libro reservado. No puedes reservarlo nuevamente hasta que lo devuelvas.")
        form = ReservaForm()

    return render(request, 'accounts/formulario_reserva.html', {
        'libro': libro,
        'form': form,
        'reserva_existente': reserva_existente  # Pasamos esta variable al template
    })


@login_required
def reserva_exitosa(request, reserva_id):
    reserva = get_object_or_404(Reserva, id=reserva_id, usuario=request.user)
    return render(request, 'accounts/reserva_exitosa.html', {
        'reserva': reserva,
        'libro': reserva.libro
    })

@login_required
def editar_resena(request, comentario_id):
    comentario = get_object_or_404(Resena, id=comentario_id)

    # Verificamos si el usuario es el propietario del comentario
    if comentario.usuario != request.user:
        messages.error(request, "No tienes permiso para editar esta reseña.")
        return redirect('detalle_libro', libro_id=comentario.libro.id)

    if request.method == 'POST':
        form = ResenaForm(request.POST, instance=comentario)
        if form.is_valid():
            form.save()
            messages.success(request, "Reseña actualizada exitosamente.")
            return redirect('detalle_libro', libro_id=comentario.libro.id)  # Mantenerse en la misma página
    else:
        form = ResenaForm(instance=comentario)

    return render(request, 'accounts/editar_resena.html', {
        'form': form,
        'comentario': comentario
    })

@login_required
def eliminar_comentario(request, comentario_id):
    comentario = get_object_or_404(Resena, id=comentario_id)

    # Verificamos si el usuario es el propietario del comentario
    if comentario.usuario != request.user:
        messages.error(request, "No tienes permiso para eliminar este comentario.")
        return redirect('detalle_libro', libro_id=comentario.libro.id)

    comentario.delete()
    messages.success(request, "Comentario eliminado exitosamente.")
    return redirect('detalle_libro', libro_id=comentario.libro.id)  # Redirigir a la misma página

