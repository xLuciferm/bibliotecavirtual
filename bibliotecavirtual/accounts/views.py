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
    template_name = 'accounts/login.html'

    def form_valid(self, form):
        """Siempre redirige a verify_token después del login."""
        login(self.request, form.get_user())  # inicia sesión
        return redirect(reverse('verify_token'))  # ignora ?next=

# logout personalizado
from django.contrib.auth import logout

@login_required
def custom_logout(request):
    logout(request)
    return redirect('login')

from django.shortcuts import render
from .models import Libro
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

from django.shortcuts import render, get_object_or_404
from .models import Libro

@login_required
def detalle_libro_view(request, libro_id):
    libro = get_object_or_404(Libro, id=libro_id)
    return render(request, 'accounts/detalle_libro.html', {'libro': libro})

