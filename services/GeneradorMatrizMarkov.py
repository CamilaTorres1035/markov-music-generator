from model.MatrizMarkov import MatrizMarkov
from dto.DataTransicionAgrupada import DataTransicionAgrupada
from model.TransicionMarkov import TransicionMarkov
from collections import defaultdict
from model.NotaMusical import NotaMusical

"""
Módulo que genera una matriz de Markov a partir de datos de transiciones agrupadas.

Transforma objetos DTOs (DataTransicionAgrupada) en una estructura de matriz de Markov
funcional, calculando probabilidades de transición y construyendo la cadena de Markov
que será utilizada para síntesis musical procedural.
"""


class GeneradorMatrizMarkov:
    """
    Generador de matrices de Markov a partir de transiciones musicales agrupadas.
    
    Recibe una lista de DataTransicionAgrupada (resultado del transformador) y
    construye una matriz de Markov completa con probabilidades calculadas.
    Se utiliza en main.py en el paso 4 del flujo de procesamiento para convertir
    datos procesados en una cadena de Markov usable para síntesis.
    
    Attributes:
        _datos: Lista de objetos DataTransicionAgrupada que contienen todas las
               transiciones agrupadas por nota origen, obtenidas del transformador.
    """

    _datos: list[DataTransicionAgrupada]

    def __init__(self, data: list[DataTransicionAgrupada]):
        """
        Inicializa el generador con datos de transiciones agrupadas.
        
        Args:
            data: Lista de DataTransicionAgrupada obtenida de
                 TransformadorTransiciones.a_dtos().
        """
        self._datos = data

    def generar_matriz(self) -> MatrizMarkov:
        """
        Genera una matriz de Markov completa a partir de los datos de transiciones.
        
        Procesa cada DataTransicionAgrupada para:
        1. Registrar todas las notas origen como estados válidos
        2. Calcular la frecuencia total de cada nota origen
        3. Crear objetos TransicionMarkov con probabilidades normalizadas
        4. Mapear cada nota origen a su lista de transiciones posibles
        
        El resultado es una matriz completa lista para síntesis musical mediante
        procesos estocásticos. Se pasa a GeneradorProceduralSuavizado en main.py
        para generar secuencias musicales.
        
        Returns:
            Objeto MatrizMarkov con la estructura completa de transiciones
            probabilísticas y conjunto de estados válidos.
        """
        matriz = defaultdict(list)  # Acumula transiciones por nota origen
        estados = set()  # Registra todas las notas origen (estados válidos)
        
        for dto in self._datos:
            nota_origen = dto._nota_origen
            estados.add(nota_origen)
            
            # Calcula cuántas veces aparece esta nota como origen en el corpus
            frecuencia_nota_origen = sum(e._conteo for e in dto._transiciones.values())
            
            # Crea una TransicionMarkov para cada nota destino posible
            for nota_destino, estadisticas in dto._transiciones.items():
                matriz[nota_origen].append(TransicionMarkov(
                    NotaMusical(nota_origen),
                    NotaMusical(nota_destino),
                    self.calcular_probabilidad(estadisticas._conteo, frecuencia_nota_origen),
                    estadisticas._tiempos
                ))

        return MatrizMarkov(matriz=matriz, estados=estados)
    
    def calcular_probabilidad(self, ocurrencias_transicion: int, frecuencia_nota_origen: int) -> float:
        """
        Calcula la probabilidad de una transición específica.
        
        Normaliza la frecuencia de ocurrencia de una transición dividiendo por el
        total de veces que la nota origen aparece en el corpus, resultando en una
        probabilidad entre 0 y 1.
        
        Args:
            ocurrencias_transicion: Número de veces que ocurrió esta transición
                                   específica en el corpus.
            frecuencia_nota_origen: Número total de veces que apareció la nota
                                   origen en el corpus.
        
        Returns:
            Probabilidad normalizada (float entre 0 y 1) de esta transición.
        """
        return ocurrencias_transicion / frecuencia_nota_origen