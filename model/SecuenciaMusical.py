from dataclasses import dataclass
from model.EventoMusical import EventoMusical

@dataclass
class SecuenciaMusical:
    _lista_notas: list[EventoMusical]