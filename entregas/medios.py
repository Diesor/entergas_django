from abc import ABC, abstractmethod

class MedioTransporte(ABC):
    @abstractmethod
    def planear(self, pedido, contexto):
        raise NotImplementedError

class Camioneta(MedioTransporte):
    def planear(self, pedido, contexto):
        return {
            'medio': 'Camioneta',
            'costo': 150,
            'tiempo_estimado_min': '60',
        }

class Motocicleta(MedioTransporte):
    def planear(self, pedido, contexto):
        return {
            'medio': 'Motocicleta',
            'costo': 80,
            'tiempo_estimado_min': '30',
        }
    
class Bicicleta(MedioTransporte):
    def planear(self, pedido, contexto):
        if pedido.peso > 5:
            raise ValueError("El pedido es demasiado pesado para ser transportado en bicicleta.")
        return {
            'medio': 'Bicicleta',
            'costo': 40,
            'tiempo_estimado_min': '45',
        }

class Dron(MedioTransporte):
    def planear(self, pedido, contexto):
        if pedido.peso > 3:
            raise ValueError("El pedido es demasiado pesado para ser transportado en dron.")
        return {
            'medio': 'Dron',
            'costo': 200,
            'tiempo_estimado_min': '15',
        }