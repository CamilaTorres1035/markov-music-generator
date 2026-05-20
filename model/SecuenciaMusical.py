from dataclasses import dataclass
from .EventoMusical import EventoMusical

@dataclass
class SecuenciaMusical:
    _lista_eventos: list[EventoMusical]