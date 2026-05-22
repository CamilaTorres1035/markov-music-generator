from .TransicionMarkov import TransicionMarkov

"""
Módulo con la estructura de datos que representa una matriz de Markov musical.

Define la matriz que contiene todas las transiciones probabilísticas entre notas
y los estados posibles del modelo. Se utiliza para generar secuencias musicales
siguiendo un proceso estocástico basado en el corpus MIDI procesado.
"""


class MatrizMarkov:
    """
    Matriz de Markov que almacena transiciones probabilísticas entre notas musicales.
    
    Encapsula la cadena de Markov generada a partir del análisis del corpus MIDI.
    Proporciona acceso rápido a las transiciones posibles desde cualquier estado
    (nota) y permite verificar si un estado existe en el modelo. Se utiliza en
    main.py en el paso 5 para generar secuencias musicales procedurales.
    
    Attributes:
        _matriz: Diccionario que mapea cada nota origen (número MIDI) a una lista
                de objetos TransicionMarkov que representan todas las transiciones
                posibles desde esa nota, incluyendo probabilidades y duraciones.
        _estados: Conjunto (set) con todos los números MIDI que aparecen como
                 notas origen en la matriz. Representa todos los estados posibles
                 en el modelo de Markov.
    """
    _matriz: dict[int, list[TransicionMarkov]]
    _estados: set[int]

    def __init__(self, matriz: dict[int, list[TransicionMarkov]], estados: set[int]):
        """
        Inicializa una matriz de Markov.
        
        Args:
            matriz: Diccionario {nota_origen: [TransicionMarkov, ...]} con todas
                   las transiciones de la cadena de Markov.
            estados: Conjunto de números MIDI que son estados válidos en el modelo.
        """
        self._matriz = matriz
        self._estados = estados

    def obtener_transiciones(self, estado: int) -> list[TransicionMarkov]:
        """
        Obtiene todas las transiciones posibles desde un estado (nota) específico.
        
        Retorna la lista de objetos TransicionMarkov que representan todos los
        cambios posibles desde la nota indicada. Se utiliza en GeneradorProceduralSuavizado
        para seleccionar la siguiente nota en la secuencia.
        
        Args:
            estado: Número MIDI de la nota origen (0-127).
        
        Returns:
            Lista de TransicionMarkov con todas las transiciones desde ese estado,
            o None si el estado no existe en la matriz.
        """
        return self._matriz.get(estado)
    
    def existe_estado(self, estado: int) -> bool:
        """
        Verifica si un estado (nota) existe en la matriz de Markov.
        
        Args:
            estado: Número MIDI de la nota a verificar (0-127).
        
        Returns:
            True si el estado está presente en los estados del modelo, False en caso contrario.
        """
        return estado in self._estados
        