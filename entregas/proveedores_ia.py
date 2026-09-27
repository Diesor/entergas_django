import xml.etree.ElementTree as ET
from abc import ABC, abstractmethod
from .sugerencias import Sugerencia

class ProveedorSugerencia(ABC):
    @abstractmethod
    def sugerir(self, pedido) -> Sugerencia:
        raise NotImplementedError
    

class ProveedorIAFalsoJSON:
    def responder(self, pedido):
        import random 
        if random.random() < 0.5:
            raise ConnectionError("Timeout del servicio de IA")
        if pedido.peso <= 5:
            return {'route_hint': 'trafico_alto', 'score': 0.82, 'medio_sugerido': 'motocicleta'}
        return {'route_hint': 'distancia_larga', 'score': 0.65, 'medio_sugerido': 'camioneta'}

class AdaptadorProveedorIAFalsoJSON(ProveedorSugerencia):
    def __init__(self, proveedor):
        self.proveedor = proveedor

    def sugerir(self, pedido) -> Sugerencia:
        respuesta = self.proveedor.responder(pedido)
        return Sugerencia(
            medio=respuesta['medio_sugerido'],
            motivo=f"{respuesta['route_hint']} (score {respuesta['score']})",
        )


class ProveedorIAFalsoXML:
    def responder(self, pedido):
        vehiculo = 'bicicleta' if pedido.peso <= 3 else 'camioneta'
        return f"<recomendacion><vehicle>{vehiculo}</vehicle><razon>zona_peatonal</razon></recomendacion>"


class AdaptadorProveedorXML(ProveedorSugerencia):
    def __init__(self, proveedor):
        self.proveedor = proveedor

    def sugerir(self, pedido) -> Sugerencia:
        raiz = ET.fromstring(self.proveedor.responder(pedido))
        return Sugerencia(
            medio=raiz.find('vehicle').text,
            motivo=raiz.find('razon').text,
        )