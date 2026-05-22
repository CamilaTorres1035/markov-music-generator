from model.MatrizMarkov import MatrizMarkov
from model.SecuenciaMusical import SecuenciaMusical
from model.EventoMusical import EventoMusical
from model.NotaMusical import NotaMusical
from model.TransicionMarkov import TransicionMarkov
import random

"""
Módulo con generador procedural básico de secuencias musicales.

Genera secuencias musicales siguiendo una cadena de Markov de forma estocástica.
Esta es la versión original/base del generador. La versión mejorada con filtros
musicales se encuentra en GeneradorProceduralSuavizado.

NOTA: Este generador NO se utiliza en main.py. Se mantiene como referencia
del algoritmo base. El flujo actual utiliza GeneradorProceduralSuavizado.
"""


class GeneradorProcedural:
    """
    Generador procedural básico de secuencias musicales usando cadenas de Markov.
    
    Implementa la síntesis musical estocástica fundamental: selecciona transiciones
    de forma aleatoria según sus probabilidades y elige duraciones del corpus.
    No aplica filtros musicales, lo que puede resultar en saltos melódicos grandes
    o secuencias menos musicales.
    
    Este es el algoritmo base. Para una versión mejorada con filtros musicales,
    ver GeneradorProceduralSuavizado.
    
    Attributes:
        _matriz_markov: MatrizMarkov que contiene las transiciones probabilísticas
                       y los estados válidos del modelo.
    """
    _matriz_markov: MatrizMarkov

    def __init__(self, matriz: MatrizMarkov):
        """
        Inicializa el generador con una matriz de Markov.
        
        Args:
            matriz: Objeto MatrizMarkov con transiciones y estados válidos.
        """
        self._matriz_markov = matriz
    
    def generar_secuencia(self, nota_inicial: int = None, duracion_secuencia_ms=30000) -> SecuenciaMusical:
        """
        Genera una secuencia musical procedural usando muestreo estocástico.
        
        Comienza desde una nota inicial (aleatoria si no se especifica) y sigue
        la cadena de Markov seleccionando transiciones según sus probabilidades
        hasta alcanzar la duración especificada. Sin aplicación de filtros musicales.
        
        Args:
            nota_inicial: Número MIDI de la nota inicial. Si es None o no
                         existe en la matriz, se selecciona aleatoriamente.
            duracion_secuencia_ms: Duración total de la secuencia en milisegundos.
                                  Por defecto 30000 (30 segundos).
        
        Returns:
            SecuenciaMusical con los eventos musicales generados.
        """
        melodia = []

        # Validar nota inicial
        if nota_inicial is None or not self._matriz_markov.existe_estado(nota_inicial):
            nota_inicial = random.choice(list(self._matriz_markov._estados))

        duracion = 0
        while duracion < duracion_secuencia_ms:
            # Paso 1: elegir una transición para ese estado
            transicion_escogida = self.seleccionar_transicion(self._matriz_markov.obtener_transiciones(nota_inicial))
            # Paso 2: elegir un tiempo de la mochila de tiempos
            tiempo_escogido = self.seleccionar_duracion(transicion_escogida._lista_tiempos)

            # Caso especial: primera nota de la melodía
            if duracion == 0:
                duracion_nota_inicial = self.seleccionar_duracion(transicion_escogida._lista_tiempos)
                melodia.append(EventoMusical(
                    NotaMusical(nota_inicial),
                    duracion_nota_inicial
                ))
                duracion += duracion_nota_inicial

            # Paso 3: crear el evento musical de la transición
            melodia.append(EventoMusical(
                NotaMusical(transicion_escogida._nota_destino._nota_midi),
                tiempo_escogido 
            ))
            
            # Paso 4: actualizar la duración y la nota
            duracion += tiempo_escogido
            nota_inicial = transicion_escogida._nota_destino._nota_midi
        
        return SecuenciaMusical(melodia)

    def seleccionar_transicion(self, transiciones: list[TransicionMarkov]) -> TransicionMarkov:
        """
        Selecciona una transición aleatoria según sus probabilidades.
        
        Utiliza muestreo de recta numérica: crea intervalos proporcionales a las
        probabilidades de cada transición y selecciona la que contiene el número
        aleatorio generado.
        
        Args:
            transiciones: Lista de TransicionMarkov disponibles desde el estado actual.
        
        Returns:
            TransicionMarkov seleccionada según sus probabilidades.
        """
        recta_numerica = {}
        suma_probabilidad = 0

        inicio_intervalo = float
        fin_intervalo = float
        for transicion in transiciones:
            inicio_intervalo = suma_probabilidad
            suma_probabilidad += transicion._probabilidad_transicion
            fin_intervalo = suma_probabilidad
            recta_numerica[(inicio_intervalo, fin_intervalo)] = transicion._nota_destino._nota_midi
        
        decision = random.random()  # Número entre [0, 1)
        nota_elegida = None

        for intervalo, nota in recta_numerica.items():
            if intervalo[0] <= decision <= intervalo[1]:
                nota_elegida = nota
                break

        transicion_elegida = next(
            (t for t in transiciones if t._nota_destino._nota_midi == nota_elegida), None
        )

        return transicion_elegida

    def seleccionar_duracion(self, tiempos: list[int]) -> int:
        """
        Selecciona aleatoriamente una duración del corpus.
        
        Args:
            tiempos: Lista de duraciones (ms) registradas en el corpus para esta transición.
        
        Returns:
            Duración seleccionada en milisegundos.
        """
        return random.choice(tiempos)




        
        