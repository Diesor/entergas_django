from django.db import models

class Pedido(models.Model):
    ESTADOS = [
        ('registrado', 'Registrado'),
        ('en_camino', 'En camino'),
        ('entregado', 'Entregado'),
    ]

    origen = models.CharField(max_length=255)
    destino = models.CharField(max_length=255)
    peso = models.DecimalField(max_digits=6, decimal_places=2)
    largo = models.DecimalField(max_digits=6, decimal_places=2)
    ancho = models.DecimalField(max_digits=6, decimal_places=2)
    alto = models.DecimalField(max_digits=6, decimal_places=2)
    urgente = models.BooleanField(default=False)
    fecha_limite = models.DateTimeField()
    estado = models.CharField(max_length=20, choices=ESTADOS, default='registrado')
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Pedido #{self.pk} ({self.estado})"
    