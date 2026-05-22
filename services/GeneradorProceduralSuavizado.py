from model.MatrizMarkov import MatrizMarkov
from model.SecuenciaMusical import SecuenciaMusical
from model.EventoMusical import EventoMusical
from model.NotaMusical import NotaMusical
from model.TransicionMarkov import TransicionMarkov
import random

"""
Módulo con generador procedural mejorado para síntesis musical de cadenas de Markov.

Genera secuencias musicales aplicando filtros y suavización para mejorar la
calidad musical. Es una versión mejorada de GeneradorProcedural que aplica
restricciones musicales como limitar saltos melódicos y filtrar silencios
encadenados.

Se utiliza en main.py en el paso 5 del pipeline para generar la secuencia
musical final a partir de la matriz de Markov.
"""


class GeneradorProceduralSuavizado:
    """
    Generador procedural mejorado de secuencias musicales con filtros musicales.
    
    Implementa síntesis musical estocástica con aplicación de reglas musicales:
    - Limita saltos melódicos a un máximo de 12 semitonos (una octava)
    - Evita cadenas infinitas de silencios
    - Permite silencios musicales normales
    
    Esto resulta en secuencias más fluidas y musicales en comparación con
    GeneradorProcedural (versión sin filtros). Se utiliza en main.py para
    producir la secuencia musical final.
    
    Attributes:
        _matriz_markov: MatrizMarkov que contiene las transiciones probabilísticas
                       y los estados válidos del modelo.
    """
    _matriz_markov: MatrizMarkov

    def __init__(self, matriz: MatrizMarkov):
        """
        Inicializa el constructor con una matriz de Markov.
        
        Args:
            matriz: Objeto MatrizMarkov con transiciones y estados válidos,
                   típicamente generado por GeneradorMatrizMarkov.
        """
        self._matriz_markov = matriz

    def generar_secuencia(
        self,
        nota_inicial: int = None,
        duracion_secuencia_ms=30000
    ) -> SecuenciaMusical:
        """
        Genera una secuencia musical procedural con suavización y filtros musicales.
        
        Comienza desde una nota inicial y sigue la cadena de Markov seleccionando
        transiciones según sus probabilidades, aplicando filtros para mejorar la
        musicalidad. Se utiliza en main.py paso 5 para generar la secuencia final.
        
        Args:
            nota_inicial: Número MIDI de la nota inicial. Si es None o no
                         existe en la matriz, se selecciona aleatoriamente.
            duracion_secuencia_ms: Duración total de la secuencia en milisegundos.
                                  Por defecto 30000 (30 segundos).
        
        Returns:
            SecuenciaMusical con los eventos musicales generados y filtrados.
        """

        melodia = []

        # Validar nota inicial
        if (
            nota_inicial is None
            or not self._matriz_markov.existe_estado(nota_inicial)
        ):
            nota_inicial = random.choice(
                list(self._matriz_markov._estados)
            )

        duracion = 0

        while duracion < duracion_secuencia_ms:

            transiciones = self._matriz_markov.obtener_transiciones(
                nota_inicial
            )

            # Seguridad por si un estado no tiene transiciones
            if not transiciones:
                break

            # Seleccionar transición con filtros musicales
            transicion_escogida = self.seleccionar_transicion(
                transiciones,
                nota_inicial
            )

            # Elegir duración
            tiempo_escogido = self.seleccionar_duracion(
                transicion_escogida._lista_tiempos
            )

            # Caso especial: primera nota
            if duracion == 0:

                duracion_nota_inicial = self.seleccionar_duracion(
                    transicion_escogida._lista_tiempos
                )

                melodia.append(
                    EventoMusical(
                        NotaMusical(nota_inicial),
                        duracion_nota_inicial
                    )
                )

                duracion += duracion_nota_inicial

            # Crear nuevo evento musical
            melodia.append(
                EventoMusical(
                    NotaMusical(
                        transicion_escogida._nota_destino._nota_midi
                    ),
                    tiempo_escogido
                )
            )

            # Actualizar duración total
            duracion += tiempo_escogido

            # Actualizar estado actual
            nota_inicial = (
                transicion_escogida._nota_destino._nota_midi
            )

        return SecuenciaMusical(melodia)

    def seleccionar_transicion(
        self,
        transiciones: list[TransicionMarkov],
        nota_actual: int
    ) -> TransicionMarkov:
        """
        Selecciona una transición aplicando filtros musicales de suavización.
        
        Filtra las transiciones disponibles según reglas musicales:
        1. Evita cadenas infinitas de silencios (-1 → -1)
        2. Permite silencios normales (-1 como destino desde notas)
        3. Limita saltos melódicos a máximo 12 semitonos (una octava)
        
        Si todos los filtros eliminan transiciones, utiliza las originales.
        La selección final se realiza mediante muestreo de recta numérica
        proporcional a las probabilidades.
        
        Args:
            transiciones: Lista de TransicionMarkov disponibles desde el estado actual.
            nota_actual: Número MIDI de la nota origen actual (0-127 o -1 para silencio).
        
        Returns:
            TransicionMarkov seleccionada según probabilidades y filtros musicales.
        """

        transiciones_filtradas = []

        for t in transiciones:

            nota_destino = t._nota_destino._nota_midi

            # Evitar cadenas infinitas de silencios
            if nota_actual == -1 and nota_destino == -1:
                continue

            # Permitir silencios normales
            if nota_destino == -1:
                transiciones_filtradas.append(t)
                continue

            # Limitar saltos melódicos a una octava (12 semitonos)
            if abs(nota_destino - nota_actual) <= 12:
                transiciones_filtradas.append(t)

        # Si todo fue filtrado, usar originales
        if not transiciones_filtradas:
            transiciones_filtradas = transiciones

        # Muestreo de recta numérica según probabilidades
        recta_numerica = {}
        suma_probabilidad = 0

        for transicion in transiciones_filtradas:

            inicio_intervalo = suma_probabilidad

            suma_probabilidad += (
                transicion._probabilidad_transicion
            )

            fin_intervalo = suma_probabilidad

            recta_numerica[
                (inicio_intervalo, fin_intervalo)
            ] = transicion

        decision = random.random() * suma_probabilidad # Esto escala el número aleatorio [0, 1) al rango real de la recta numérica [0, suma_probabilidad).

        for intervalo, transicion in recta_numerica.items():

            if intervalo[0] <= decision <= intervalo[1]:
                return transicion

        return random.choice(transiciones_filtradas)

    def seleccionar_duracion(self, tiempos: list[int]) -> int:
        """
        Selecciona aleatoriamente una duración del corpus.
        
        Args:
            tiempos: Lista de duraciones (ms) registradas en el corpus para esta transición.
        
        Returns:
            Duración seleccionada en milisegundos.
        """
        return random.choice(tiempos)