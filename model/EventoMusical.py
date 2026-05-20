from dataclasses import dataclass
from model.NotaMusical import NotaMusical

@dataclass
class EventoMusical:
    _nota: NotaMusical
    _duracion: float