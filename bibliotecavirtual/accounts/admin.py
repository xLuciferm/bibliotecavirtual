from django.contrib import admin
from .models import Libro, Reserva
from django.utils.html import format_html

@admin.register(Libro)
class LibroAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'autor', 'categoria', 'isbn', 'stock', 'mostrar_imagen')
    readonly_fields = ('mostrar_imagen',)

    def mostrar_imagen(self, obj):
        if obj.imagen:
            return format_html('<img src="{}" width="150" />', obj.imagen.url)
        return "No hay imagen"
    mostrar_imagen.short_description = "Vista previa"

@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'libro', 'fecha_deseada', 'fecha_entrega')
    list_filter = ('fecha_deseada', 'fecha_entrega', 'usuario')
    search_fields = ('libro__titulo', 'usuario__username')
