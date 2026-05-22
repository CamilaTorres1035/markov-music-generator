from dataclasses import dataclass
from .EventoMusical import EventoMusical

"""
Módulo que define la clase SecuenciaMusical, representando una secuencia
ordenada de eventos musicales que conforman una pieza o fragmento musical.
"""

@dataclass
class SecuenciaMusical:
    """
    Representa una secuencia ordenada de eventos musicales.

    Agrupa una lista de EventoMusical en orden cronológico, permitiendo
    modelar fragmentos o piezas musicales completas listas para
    ser procesadas o exportadas (e.g. a formato MIDI).

    Attributes:
        _lista_eventos (list[EventoMusical]): Lista ordenada de eventos
            que componen la secuencia musical.
    """
    _lista_eventos: list[EventoMusical]