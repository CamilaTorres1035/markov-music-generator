from dataclasses import dataclass
from .EstadisticasDeTransicion import EstadisticasDeTransicion

"""
Módulo con estructura de datos para transiciones agrupadas de un corpus MIDI.

Define la clase que encapsula todas las posibles transiciones desde una nota
origen hacia otras notas destino, junto con sus estadísticas asociadas.
"""


@dataclass
class DataTransicionAgrupada:
    """
    Agrupa todas las transiciones posibles desde una nota origen específica.
    
    Representa todas las transiciones que pueden ocurrir desde una nota MIDI
    particular, indicando a qué notas destino puede ir y con qué frecuencia
    e información de duraciones. Esta estructura es el resultado de transformar
    tuplas reducidas de un pipeline map-reduce en estructuras de datos más
    accesibles para construir matrices de Markov.
    
    Se genera en main.py al transformar tuplas_reducidas usando
    TransformadorTransiciones.a_dtos() y se utiliza para generar la matriz
    de Markov en GeneradorMatrizMarkov.
    
    Attributes:
        _nota_origen: Número MIDI de la nota origen. Define desde qué
                     nota musical se originan todas las transiciones agrupadas
                     en este objeto.
        _transiciones: Diccionario que mapea cada nota destino (número MIDI)
                      a sus EstadisticasDeTransicion asociadas. Permite acceso
                      rápido a la frecuencia y duraciones de cada transición
                      posible desde la nota origen.
    """
    _nota_origen: int
    _transiciones: dict[int, EstadisticasDeTransicion]
