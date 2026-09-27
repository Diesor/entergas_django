from .medios import Camioneta, Motocicleta, Bicicleta, Dron

_MEDIOS = {
    'camioneta': Camioneta,
    'motocicleta': Motocicleta,
    'bicicleta': Bicicleta,
    'dron': Dron,
}

def crear_medio(nombre):
    clase = _MEDIOS.get(nombre.lower())
    if clase is None:
        raise ValueError(f"Medio de transporte desconocido: {nombre}")
    return clase()