from dataclasses import dataclass
from NotaMusical import NotaMusical

@dataclass
class EventoMusical:
    _nota: NotaMusical
    _duracion: float