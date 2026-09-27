from django.db import transaction
from .models import Pedido
from .fabrica import crear_medio

@transaction.atomic
def registrar_pedido(datos, proveedor_ia):
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

    sugerencia = proveedor_ia.sugerir(pedido)
    medio = crear_medio(sugerencia.medio)
    plan = medio.planear(pedido, contexto={})

    pedido.medio_asignado = sugerencia.medio
    pedido.motivo_asignacion = sugerencia.motivo
    pedido.costo_estimado = plan['costo']
    pedido.tiempo_estimado_min = plan['tiempo_estimado_min']
    pedido.save()

    return pedido

def obtener_seguimiento_pedido(pedido_id):
    pedido = Pedido.objects.get(pk=pedido_id)
    return {
        'folio': pedido.pk,
        'estado': pedido.estado,
        'eta': 'Por calcular (sin medios de transporte aún)',
        'origen': pedido.origen,
        'destino': pedido.destino,
        'medio': pedido.medio_asignado,
        'motivo': pedido.motivo_asignacion,
        'costo_estimado': pedido.costo_estimado,
        'tiempo_estimado_min': pedido.tiempo_estimado_min,
    }