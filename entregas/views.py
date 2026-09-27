from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from decimal import Decimal
from .servicios import registrar_pedido, obtener_seguimiento_pedido
from .proveedores_ia import ProveedorIAFalsoJSON, AdaptadorProveedorIAFalsoJSON, ProveedorIAFalsoXML, AdaptadorProveedorXML


@require_http_methods(["GET","POST"])
def alta_pedido(request):
    if request.method == "POST":
        datos = {
            'origen': request.POST['origen'],
            'destino': request.POST['destino'],
            'peso': Decimal(request.POST['peso']),
            'largo': Decimal(request.POST['largo']),
            'ancho': Decimal(request.POST['ancho']),
            'alto': Decimal(request.POST['alto']),
            'urgente': request.POST.get('urgente') == 'on',
            'fecha_limite': request.POST['fecha_limite'],
            'idempotency_key': request.POST.get('idempotency_key'),
        }
        import uuid
        proveedor_ia = AdaptadorProveedorIAFalsoJSON(ProveedorIAFalsoJSON())
        pedido = registrar_pedido(datos, proveedor_ia)
        return redirect('seguimiento_pedido', pedido_id=pedido.pk)
    return render(request, 'entregas/alta.html', {'idempotency_key': uuid.uuid4()})


def seguimiento_pedido(request, pedido_id):
    contexto = obtener_seguimiento_pedido(pedido_id)
    return render(request, 'entregas/seguimiento.html', contexto)

def seguimiento_pedido_json(request, pedido_id):
    contexto = obtener_seguimiento_pedido(pedido_id)
    return JsonResponse(contexto)

def reporte_pedido(request, pedido_id):
    contexto = obtener_seguimiento_pedido(pedido_id)
    html = f"""
    <html><body>
        <h1>Reporte gerencial #{contexto['folio']}</h1>
        <table border="1">
            <tr><td>Estado</td><td>{contexto['estado']}</td></tr>
            <tr><td>Medio</td><td>{contexto['medio']}</td></tr>
            <tr><td>Costo</td><td>${contexto['costo_estimado']}</td></tr>
            <tr><td>Tiempo</td><td>{contexto['tiempo_estimado_min']} min</td></tr>
        </table>
    </body></html>
    """
    return HttpResponse(html)