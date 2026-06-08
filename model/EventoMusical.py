from dataclasses import dataclass
from .NotaMusical import NotaMusical
"""
Módulo que define la clase EventoMusical, representando un evento musical
compuesto por una nota y su duración en una secuencia.
"""
@dataclass
class EventoMusical:
    """
    Representa un evento musical dentro de una secuencia.

    Un evento musical asocia una nota MIDI con una duración específica,
    siendo la unidad básica de composición en una SecuenciaMusical.

    Attributes:
        _nota (NotaMusical): La nota musical asociada al evento.
        _duracion (int): Duración del evento en unidades de tiempo (e.g. ticks MIDI).
    """
    _nota: NotaMusical
    _duracion: int
    _velocidad: int = 60         # Añadido: Volumen (0-127)