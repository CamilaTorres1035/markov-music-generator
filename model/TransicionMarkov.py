from dataclasses import dataclass
from .NotaMusical import NotaMusical

"""
Módulo con la estructura de datos para una transición en una cadena de Markov.

Define una transición individual que representa la probabilidad y características
de cambio de una nota musical a otra dentro de un modelo de Markov.
"""


@dataclass
class TransicionMarkov:
    """
    Representa una transición probabilística en una cadena de Markov musical.
    
    Encapsula la información completa de una transición de una nota origen a una
    nota destino, incluyendo la probabilidad de ocurrencia y todas las duraciones
    registradas en el corpus MIDI. Se utiliza dentro de la MatrizMarkov para
    almacenar las transiciones posibles desde cada estado (nota).
    
    Attributes:
        _nota_origen: NotaMusical que representa la nota desde la cual ocurre
                     la transición.
        _nota_destino: NotaMusical que representa la nota hacia la cual ocurre
                      la transición.
        _probabilidad_transicion: Valor entre 0 y 1 que representa la probabilidad
                                 de que esta transición ocurra desde la nota origen.
                                 Se calcula como: ocurrencias_esta_transicion /
                                 total_ocurrencias_nota_origen.
        _lista_tiempos: Lista de duraciones (en milisegundos) registradas para la
                       nota destino cada vez que esta transición ocurrió en el
                       corpus. Se utiliza para análisis y síntesis de ritmo.
    """
    _nota_origen: NotaMusical
    _nota_destino: NotaMusical
    _probabilidad_transicion: float
    _lista_tiempos: list[int]