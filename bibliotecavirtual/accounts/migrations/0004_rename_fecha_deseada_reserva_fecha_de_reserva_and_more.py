# Generated by Django 4.2 on 2025-04-15 04:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_libro_descripcion'),
    ]

    operations = [
        migrations.RenameField(
            model_name='reserva',
            old_name='fecha_deseada',
            new_name='fecha_de_reserva',
        ),
        migrations.RenameField(
            model_name='reserva',
            old_name='fecha_entrega',
            new_name='fecha_devolucion',
        ),
    ]
