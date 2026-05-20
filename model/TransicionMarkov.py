from dataclasses import dataclass
from .NotaMusical import NotaMusical

@dataclass
class TransicionMarkov:
    _nota_origen: NotaMusical
    _nota_destino: NotaMusical
    _probabilidad_transicion: float
    _lista_tiempos: list[float]