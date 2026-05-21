from model.MatrizMarkov import MatrizMarkov
from model.SecuenciaMusical import SecuenciaMusical
from model.EventoMusical import EventoMusical
from model.NotaMusical import NotaMusical
from model.TransicionMarkov import TransicionMarkov
import random

class GeneradorProcedural:
    _matriz_markov: MatrizMarkov

    def __init__(self, matriz:MatrizMarkov):
        self._matriz_markov = matriz
    
    def generar_secuencia(self, nota_inicial:int = None, duracion_secuencia_ms = 30000) -> SecuenciaMusical:
        melodia = [] ##Aquí se almacena la secuencia de eventos

        #Para validar si no hay nota inicial
        if nota_inicial is None or not self._matriz_markov.existe_estado(nota_inicial):
            nota_inicial = random.choice(list(self._matriz_markov._estados))


        duracion = 0 #Controlador de duración, por defecto se deja para audios de 30 segundos
        while duracion < duracion_secuencia_ms:
            #Paso 1: elegir una transición para ese estado
            transicion_escogida = self.seleccionar_transicion(self._matriz_markov.obtener_transiciones(nota_inicial))
            #Paso 2: elegir un tiempo de la mochila de tiempos
            tiempo_escogido = self.seleccionar_duracion(transicion_escogida._lista_tiempos)

            #Caso especial, solo válido para la primera nota de la melodía
            if duracion == 0:
                duracion_nota_inicial = self.seleccionar_duracion(transicion_escogida._lista_tiempos)
                melodia.append(EventoMusical(
                    NotaMusical(nota_inicial),
                    duracion_nota_inicial
                ))
                duracion += duracion_nota_inicial


            #Paso 3: crear el evento musical de la transición
            melodia.append(EventoMusical(
                NotaMusical(transicion_escogida._nota_destino._nota_midi),
                tiempo_escogido 
                ))
            
            #Paso 4: actualizar la duración y la nota
            duracion += tiempo_escogido
            nota_inicial = transicion_escogida._nota_destino._nota_midi
        
        #Al finalizar:
        return SecuenciaMusical(melodia)


        
    def seleccionar_transicion(self, transiciones: list[TransicionMarkov]) -> TransicionMarkov:
        #Se emula la forma de elegir un estado en un bigrama, por medio de una recta
        #numérica separada por intervalos proporcionales a las probabilidades
        #de transición de otros estados y eligiendo un número seudoaleatorio
        #para decidir el próximo estado, dependiendo de en qué intervalo caiga
        recta_numerica = {}
        suma_probabilidad = 0

        inicio_intervalo = float
        fin_intervalo = float
        for transicion in transiciones:
            inicio_intervalo = suma_probabilidad
            suma_probabilidad += transicion._probabilidad_transicion
            fin_intervalo = suma_probabilidad
            recta_numerica[(inicio_intervalo, fin_intervalo)] = transicion._nota_destino._nota_midi
        
        decision = random.random() #Un número entre [0, 1)
        nota_elegida = None

        for intervalo, nota in recta_numerica.items():
            if intervalo[0] <= decision <= intervalo[1]:
                nota_elegida = nota
                break

        transicion_elegida = next(
            (t for t in transiciones if t._nota_destino._nota_midi == nota_elegida), None
        )

        return transicion_elegida

    def seleccionar_duracion(self, tiempos:list[int]) -> int:
        return random.choice(tiempos)




        
        