from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .servicios import registrar_pedido, obtener_seguimiento_pedido
from .models import Pedido

@require_http_methods(["GET","POST"])
def alta_pedido(request):
    if request.method == "POST":
        datos = {
            'origen': request.POST.get('origen'),
            'destino': request.POST.get('destino'),
            'peso': request.POST.get('peso'),
            'largo': request.POST.get('largo'),
            'ancho': request.POST.get('ancho'),
            'alto': request.POST.get('alto'),
            'urgente': request.POST.get('urgente') == 'on',
            'fecha_limite': request.POST.get('fecha_limite'),
        }
        pedido = registrar_pedido(datos)
        return redirect('seguimiento_pedido', pedido_id=pedido.pk)
    return render(request, 'entregas/alta.html')


def seguimiento_pedido(request, pedido_id):
    contexto = obtener_seguimiento_pedido(pedido_id)
    return render(request, 'entregas/seguimiento.html', contexto)

def seguimiento_pedido_json(request, pedido_id):
    contexto = obtener_seguimiento_pedido(pedido_id)
    return JsonResponse(contexto)