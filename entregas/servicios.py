from django.db import transaction
from .models import Pedido

@transaction.atomic
def registrar_pedido(datos):
    pedido= Pedido.objects.create(
        origen=datos['origen'],
        destino=datos['destino'],
        peso=datos['peso'],
        largo=datos['largo'],
        ancho=datos['ancho'],
        alto=datos['alto'],
        urgente=datos.get('urgente', False),
        fecha_limite=datos['fecha_limite'],
    )
    return pedido

def obtener_seguimiento_pedido(pedido_id):
    pedido = Pedido.objects.get(pk=pedido_id)
    return {
        'folio': pedido.pk,
        'estado': pedido.estado,
        'eta': 'Por calcular (sin medios de transporte aún)',
        'origen': pedido.origen,
        'destino': pedido.destino,
    }