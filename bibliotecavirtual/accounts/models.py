from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    pass

class Libro(models.Model):
    titulo = models.CharField(max_length=200)
    autor = models.CharField(max_length=100)
    categoria = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    isbn = models.CharField(max_length=13)
    stock = models.PositiveIntegerField()
    imagen = models.ImageField(upload_to='libros/', blank=True, null=True)
      # <- campo nuevo

    def __str__(self):
        return self.titulo

from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Reserva(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    libro = models.ForeignKey('Libro', on_delete=models.CASCADE)
    fecha_deseada = models.DateField()
    fecha_entrega = models.DateField(blank=True, null=True)

    def __str__(self):
        return f"{self.usuario.username} - {self.libro.titulo}"
