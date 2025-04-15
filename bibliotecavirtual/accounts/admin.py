from django.contrib import admin
from .models import Libro, Reserva
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone

@admin.register(Libro)
class LibroAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'autor', 'categoria', 'isbn', 'stock', 'mostrar_imagen', 'disponibilidad')
    readonly_fields = ('mostrar_imagen', 'disponibilidad')
    list_editable = ('stock',)  # Permite editar el stock directamente desde la lista
    list_filter = ('categoria',)
    search_fields = ('titulo', 'autor', 'isbn')
    fields = ('titulo', 'autor', 'categoria', 'isbn', 'stock', 'imagen', 'mostrar_imagen', 'descripcion')

    def mostrar_imagen(self, obj):
        if obj.imagen:
            return format_html('<img src="{}" width="150" />', obj.imagen.url)
        return "No hay imagen"

    mostrar_imagen.short_description = "Vista previa"

    def disponibilidad(self, obj):
        if obj.stock > 0:
            return format_html('<span style="color: green;">Disponible ({})</span>', obj.stock)
        return format_html('<span style="color: red;">Agotado</span>')

    disponibilidad.short_description = "Estado"

@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'enlace_libro', 'fecha_de_reserva', 'fecha_devolucion', 'estado_reserva')
    list_filter = ('fecha_de_reserva', 'fecha_devolucion', 'usuario', 'libro__categoria')
    search_fields = ('libro__titulo', 'usuario__username')
    list_select_related = ('libro', 'usuario')
    actions = ['marcar_como_entregado']

    def enlace_libro(self, obj):
        url = reverse('admin:accounts_libro_change', args=[obj.libro.id])
        return format_html('<a href="{}">{}</a>', url, obj.libro.titulo)

    enlace_libro.short_description = "Libro"
    enlace_libro.admin_order_field = 'libro__titulo'

    def estado_reserva(self, obj):
        if obj.fecha_devolucion:
            return "Entregado"
        if obj.fecha_de_reserva < timezone.now().date():
            return "Vencido"
        return "Pendiente"

    estado_reserva.short_description = "Estado"

    def marcar_como_entregado(self, request, queryset):
        updated = queryset.update(fecha_devolucion=timezone.now().date())
        self.message_user(request, f"{updated} reservas marcadas como entregadas")

    marcar_como_entregado.short_description = "Marcar como entregado"