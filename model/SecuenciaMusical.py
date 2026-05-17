from dataclasses import dataclass
from EventoMusical import EventoMusical

@dataclass
class SecuenciaMusical:
    _lista_notas: list[EventoMusical]