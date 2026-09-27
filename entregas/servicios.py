from django.db import transaction
from .models import Pedido
from .fabrica import crear_medio
from .sugerencias import Sugerencia

@transaction.atomic
def registrar_pedido(datos, proveedor_ia):
    clave= datos.get('idempotency_key')

    if clave:
        pedido_existente = Pedido.objects.filter(idempotency_key=clave).first()
        if pedido_existente:
            return pedido_existente

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

    transaction.on_commit(lambda: enviar_aviso(pedido))

    return pedido

def obtener_seguimiento_pedido(pedido_id):
    pedido = Pedido.objects.get(pk=pedido_id)
    return {
        'folio': pedido.pk,
        'estado': pedido.estado,
        'eta': 'Por calcular',
        'origen': pedido.origen,
        'destino': pedido.destino,
        'medio': pedido.medio_asignado,
        'motivo': pedido.motivo_asignacion,
        'costo_estimado': pedido.costo_estimado,
        'tiempo_estimado_min': pedido.tiempo_estimado_min,
    }

def enviar_aviso(pedido):
    """Simulación de correo/notificación. Puede fallar sin afectar lo ya guardado."""
    print(f"[AVISO] Pedido #{pedido.pk} creado. Medio: {pedido.medio_asignado}")

def obtener_sugerencia_segura(proveedor_ia, pedido):
    """
    Facade sobre el Adapter: si la IA falla o tarda, no tumbamos el alta.
    Devolvemos una Sugerencia de reserva y seguimos.
    """
    try:
        return proveedor_ia.sugerir(pedido)
    except Exception as e:
        print(f"[IA CAÍDA] {e} — usando asignación por defecto")
        return Sugerencia(medio='camioneta', motivo='IA no disponible: asignación por defecto')
 