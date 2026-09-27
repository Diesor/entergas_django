from django.contrib import admin
from django.urls import path
from entregas import views 

urlpatterns = [
    path('admin/', admin.site.urls),
    path('pedidos/alta/', views.alta_pedido, name='alta_pedido'),
    path('pedidos/seguimiento/<int:pedido_id>/', views.seguimiento_pedido, name='seguimiento_pedido'),
    path('pedidos/seguimiento/<int:pedido_id>.json', views.seguimiento_pedido_json, name='seguimiento_pedido_json'),
    path('pedidos/reporte/<int:pedido_id>/', views.reporte_pedido, name='reporte_pedido'),
]
