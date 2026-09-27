# Plataforma de entregas — Proyecto de patrones de software

## Cómo correrlo

    python manage.py migrate
    python manage.py runserver

- Alta de pedido: http://127.0.0.1:8000/pedidos/alta/ (POST)
- Seguimiento (panel web): http://127.0.0.1:8000/pedidos/seguimiento/<id>
- Reporte gerencial: http://127.0.0.1:8000/pedidos/reporte/<id>
- Contrato para la app (JSON mínimo): http://127.0.0.1:8000/api/pedidos/<id>

## Qué patrón ya traía Django (no se reescribió)

- **Front Controller**: `urls.py` despacha toda petición; no se escribió un dispatcher propio.
- **ORM**: `Pedido.objects.create(...)` / `filter(...)`; no se escribió SQL a mano.
- **Middleware de sesión/autenticación**: reutilizado de Django, no reimplementado.

## Qué patrón cubre cada conflicto

| Archivo | Patrón | Conflicto que resuelve |
|---|---|---|
| `views.py` | Page Controller (delgado) | Cada trámite es una vista chica que delega en el servicio |
| `servicios.py` | Service Layer | Reglas de negocio y orquestación fuera de la vista y la plantilla |
| `servicios.py` (`registrar_pedido`) | PRG + transacción atómica | Evita doble alta al recargar; agrupa la escritura |
| `servicios.py` (`idempotency_key`) | Idempotencia | Evita doble alta por doble clic (distinto del PRG) |
| `medios.py` | Strategy | Un medio de entrega = una clase; agregar uno nuevo no toca los demás |
| `proveedores_ia.py` | Adapter | Traduce JSON/XML de cada proveedor de IA a `Sugerencia(medio, motivo)` |
| `fabrica.py` | Fábrica simple (no Factory Method) | Un solo punto de creación (`crear_medio`) a partir de un string ya resuelto |
| `servicios.py` (`obtener_sugerencia_segura`) | Facade + manejo de fallos | Si la IA se cae, se asigna un medio por defecto y el alta no se detiene |
| `servicios.py` (`enviar_aviso` + `transaction.on_commit`) | Separación transacción/aviso | El aviso se dispara solo si el pedido ya quedó confirmado |
| `templates/seguimiento.html` | Template View | Solo pinta variables ya resueltas; no consulta la base |
| `views.py` (`reporte_pedido`) | Reutilización del Service Layer | El reporte no duplica el `SELECT` del seguimiento |

## Qué se rechazó a propósito

No se implementó Event Sourcing, CQRS ni Redux para generar el PDF de guía (punto 7 del enunciado). El trámite real es autenticar, consultar un pedido existente y generar un archivo — eso no requiere replay de eventos ni un store separado de lectura/escritura. Agregar esa maquinaria sería ceremonia sin necesidad real para el alcance de este proyecto.