# Día 1 — Estudiar el caso web (sin código de dominio) #

#|Inconveniente del enunciado|Qué ya trae Django|Qué tendremos que escribir nosotros|Qué no vamos a copiar del libro|
|-|-|-|-|-|
|1| Cada tramite repite "¿hay sesión?", bitácora y encabezado.| Middleware de autenticación, @login required, sistema de LOGGING | Middleware/decorator propio de auditoría de negocio (que se registra en cada pedido)| Un dispatcher casero urls.py + middleware ya cumplen el rol de Front Controller |
|2| Switch de 200 lineas para elegir medio + cada proveedor de IA devuelve JSON/XML/objeto distinto | Nada de negocio; solo el mecanismo de vistas para invocar servicios | Strategy (una clase por medio: camioneta, moto, dron, bici) + Adapter por proveedor de IA que traduzca a Sugerencia{medio,motivo}| El diagrama GoF de Strategy/Adapter sin instanciarlo con las reglas reales |
|3| La plantilla ejecuta SQL, el reporte duplica consultas, la vista conoce la bodega| ORM (QuerySets), vistas basadas en clase que separan lógica de presentación | Service Layer único que resuelva mapa/ETA/bodega, usado tanto por plantilla como por reporte | Copiar el ejemplo de Service Layer línea por línea sin adaptarlo a nuestras entidades |
|4| Cobro + alta de envío + correo + aviso mezclados; doble click genera doble cargo | transaction.atomic, señales (signals) para desacoplar efectos secundarios | Patrón PGR tras confirmar el pago, y observer/signals para avisar a cliente, repartidor, stats e IA una vez comprometida la transacción | Meter el envío del correo dentro de la misma transacción síncrona del cobro |
|5| App cliente, app repartidor y panel piden el mismo pedido en formatos distintos (12 peticiones) | Serialización a JSON (JsonResponse), un mismo modelo/queryset como fuente de verdad| Un endpoint GET que devuelca el JSON mínimo (folio, estado, eta) además de la vista HTML del panel, ambos alimentados por el mismo Service Layer | Construir una API tipo CQRS/Event Sourcing solo para esto |
|6| Mapa e IA se caen y tumban hasta la consulta de un pedido ya guardado | Mecanismo de vistas para aislar llamadas externas | Adapter/Facade con manejo de fallos (try/except, timeout, valor por defecto) para que el dominio no dependa de que el mapa o la IA respondan | Copiar un circuit breaker sofisticado que no corresponde a la escala del proyecto |
|7| Proponen Event Sourcing, CQRS y Redux para generar un pdf de guía | Auntenticación, ORM para consultar el pedido, libería para generar el archivo | Una vista simple: autenticar, consultar el pedido, generar el PDF | Event Sourcing/CQRS/Redux: es ceremonia, no una necesidad real|

- **¿=urls.py= es Front Controller, Page Controller, o el camino hacia los dos?** R= Es el camino hacia los dos. Funciona como Front Controller (punto único de entrada que despacha toda la petición) pero delega en cada vista, que actúa como Page Controller de su propio trámite (alta de pedido, cobro, seguimiento).


- **¿La plantilla Jinja/Django puede hacer SELECT?** R= Técnicamente sí —Django permite pasar un QuerySet sin evaluar y la plantilla lo dispara al iterarlo—, pero no debe. La plantilla es la capa de presentación; decidir qué datos traer es responsabilidad de la vista o del Service Layer. Meter el SELECT ahí es justo el problema descrito arriba (mapa/ETA/reporte duplicados) y rompe la separación entre presentación y acceso a datos.

# Día 2 — Pensar el primer corte y arrancar Django #

1. Front Controller (Django, ya instanciado): toda petición entra por plataforma/urls.py. No escribimos un dispatcher propio — el framework ya lo trae. Esta línea no es GoF nuestro, es el marco.
2. Page Controller: urls.py resuelve la ruta pedidos y llama a la vista alta_pedido. Esa vista es el Page Controller del trámite "alta de pedido" — sabe leer el request.POST, nada más.
3. Servicio (Service Layer): la vista delega en registrar_pedido(datos), que vive en servicios.py y no sabe qué es HTTP. Ahí está la regla de negocio y la transacción.
4. Modelo / ORM: servicios.py usa Pedido.objects.create(...), que es el ORM de Django — no escribimos SQL a mano.
5. PRG: tras crear el pedido, la vista hace redirect(...) hacia seguimiento_pedido, nunca renderiza directamente el resultado del POST. Así, si el usuario recarga la página de seguimiento, dispara un GET (idempotente), no un segundo POST que duplicaría el pedido.
6. Template View: el GET de seguimiento arma el contexto en el servicio y lo pasa a seguimiento.html, que solo pinta variables.

# Día 3 — Strategy, Adapter y quién hace el new #

* **Strategy:** cada medio de entrega es una clase intercambiable con el mismo método planear, así el conjunto de medios crece sin tocar código existente.
* **Adapter:** cada proveedor de IA habla su propio idioma (JSON con route_hint, XML con <vehicle>); el Adapter lo traduce a Sugerencia(medio, motivo) para que el dominio nunca conozca el formato externo.
* **Fábrica simple (no Factory Method):** un solo punto (crear_medio) instancia el medio a partir del string ya resuelto por la Sugerencia; no hay familias de trámite que necesiten redefinir el gancho de creación, así que Factory Method sería sobre-ingeniería aquí.

# Día 4 — Plantilla limpia, transacción e IA caída #

Si el cliente pulsa "crear" dos veces seguidas (dos peticiones POST casi simultáneas a /pedidos/alta/), el PRG por sí solo no lo evita: PRG protege contra el recargar la página de resultado, no contra dos envíos del mismo formulario antes de que llegue la primera respuesta. Con el código actual, esas dos peticiones crearían dos pedidos distintos, cada uno con su transaction.atomic propio, y ambas pasarían.

Si hubiera cobro real de por medio, el riesgo sería doble cargo. La solución no es Event Sourcing ni nada parecido: es idempotencia — el cliente envía un identificador único generado en el navegador (un idempotency_key, por ejemplo un UUID puesto en un campo oculto del formulario al cargar la página). En registrar_pedido, antes de crear, se verifica si ya existe un pedido con esa clave.

# Día 5 — El mismo pedido en JSON y la defensa #

**Si mañana hay triciclo, ¿cuántos archivos abrimos?**
Si mañana la empresa decide agregar un medio de transporte nuevo, como un triciclo, la respuesta correcta es: un archivo, y una línea en un segundo.

Abrimos medios.py y agregamos una clase nueva, Triciclo, que hereda de MedioDeEntrega e implementa un único método: planear(pedido, contexto). Ahí definimos su costo, su tiempo estimado y las restricciones propias de ese medio (por ejemplo, un peso máximo). Nada más. Después vamos a fabrica.py y agregamos una línea al diccionario de medios disponibles, asociando el string "triciclo" con la clase recién creada.

Con eso, el triciclo ya existe en el sistema. No abrimos views.py, porque la vista nunca supo qué medios existen: solo recibe una sugerencia y pide que se cree el medio correspondiente. No abrimos servicios.py, porque el Service Layer orquesta el flujo —Adapter, fábrica, Strategy— sin conocer los nombres concretos de los medios. No tocamos las plantillas, porque solo pintan lo que el contexto ya les entrega resuelto. Y no tocamos proveedores_ia.py, porque el formato en que la IA recomienda un medio (JSON, XML, o lo que sea) es independiente de cuántos medios existan en el dominio.


