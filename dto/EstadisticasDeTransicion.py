from dataclasses import dataclass

"""
Módulo con estructura de datos para estadísticas de transiciones musicales.

Define la clase que encapsula las estadísticas agregadas de una transición
de una nota a otra.
"""


@dataclass
class EstadisticasDeTransicion:
    """
    Estadísticas agregadas de una transición entre dos notas musicales.
    
    Almacena la frecuencia con la que ocurre una transición de una nota origen
    a una nota destino específica, junto con todas las duraciones registradas
    para la nota destino en esas transiciones. Se utiliza para construir
    probabilidades en modelos de Markov musicales.
    
    Attributes:
        _conteo: Número de veces que ocurrió esta transición en el corpus MIDI.
        _tiempos: Lista de duraciones (en milisegundos) registradas para la nota
                 destino cada vez que esta transición ocurrió. Se utiliza para
                 calcular estadísticas de duración (media, desviación, etc.).
    """
    _conteo: int
    _tiempos: list[int]