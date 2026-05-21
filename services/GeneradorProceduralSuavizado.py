from model.MatrizMarkov import MatrizMarkov
from model.SecuenciaMusical import SecuenciaMusical
from model.EventoMusical import EventoMusical
from model.NotaMusical import NotaMusical
from model.TransicionMarkov import TransicionMarkov
import random


class GeneradorProceduralSuavizado:
    _matriz_markov: MatrizMarkov

    def __init__(self, matriz: MatrizMarkov):
        self._matriz_markov = matriz

    def generar_secuencia(
        self,
        nota_inicial: int = None,
        duracion_secuencia_ms=30000
    ) -> SecuenciaMusical:

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

            # Seleccionar transición suavizada
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

            # Limitar saltos melódicos
            if abs(nota_destino - nota_actual) <= 12:
                transiciones_filtradas.append(t)

        # Si todo fue filtrado, usar originales
        if not transiciones_filtradas:
            transiciones_filtradas = transiciones

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

        decision = random.random() * suma_probabilidad

        for intervalo, transicion in recta_numerica.items():

            if intervalo[0] <= decision <= intervalo[1]:
                return transicion

        return random.choice(transiciones_filtradas)

    def seleccionar_duracion(self, tiempos: list[int]) -> int:
        return random.choice(tiempos)