from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError

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

    def __str__(self):
        return f"{self.titulo} (Stock: {self.stock})"

class Reserva(models.Model):
    usuario = models.ForeignKey('User', on_delete=models.CASCADE)
    libro = models.ForeignKey('Libro', on_delete=models.CASCADE)
    fecha_de_reserva = models.DateField()
    fecha_devolucion = models.DateField(blank=True, null=True)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def clean(self):
        if not self.pk:
            existe = Reserva.objects.filter(
                usuario=self.usuario,
                libro=self.libro,
                fecha_devolucion__isnull=True
            ).exists()
            if existe:
                raise ValidationError(
                    "Ya tienes este libro reservado. No puedes reservarlo nuevamente hasta que lo devuelvas.")

    def __str__(self):
        return f"{self.usuario.username} - {self.libro.titulo} ({self.fecha_de_reserva})"

# 👇 Esta clase debe ir fuera de Reserva y sin ñ
class Resena(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    libro = models.ForeignKey(Libro, on_delete=models.CASCADE, related_name='resenas')
    calificacion = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)])
    comentario = models.TextField()
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('usuario', 'libro')

    def __str__(self):
        return f"{self.usuario.username} - {self.libro.titulo} ({self.calificacion} estrellas)"
