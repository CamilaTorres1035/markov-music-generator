from dataclasses import dataclass
from .EstadisticasDeTransicion import EstadisticasDeTransicion
@dataclass
class DataTransicionAgrupada:
    _nota_origen: int
    _transiciones: dict[int, EstadisticasDeTransicion]
