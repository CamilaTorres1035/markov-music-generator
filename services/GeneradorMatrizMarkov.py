from model.MatrizMarkov import MatrizMarkov
from dto.DataTransicionAgrupada import DataTransicionAgrupada
from model.TransicionMarkov import TransicionMarkov
from collections import defaultdict
from model.NotaMusical import NotaMusical
class GeneradorMatrizMarkov:

    _datos:list[DataTransicionAgrupada]

    def __init__(self, data:list[DataTransicionAgrupada]):
        self._datos = data

    def generar_matriz(self) -> MatrizMarkov:
        matriz = defaultdict(list) #Aquí se acumula la matriz
        estados = set() #Aquí se guardan los estados
        for dto in self._datos:
            nota_origen = dto._nota_origen ##Esta es la nota clave
            estados.add(nota_origen) # Añadimos la nota de origen al conjunto de estados Markov
            frecuencia_nota_origen = sum(e._conteo for e in dto._transiciones.values()) #Cantidad de veces que aparece esa nota, sin importar su transición
            #Se recorre el diccionario de Transiciones de esa nota de origen
            for nota_destino, estadisticas in dto._transiciones.items():
                matriz[nota_origen].append(TransicionMarkov(
                    NotaMusical(nota_origen),
                    NotaMusical(nota_destino),
                    self.calcular_probabilidad(estadisticas._conteo, frecuencia_nota_origen),
                    estadisticas._tiempos
                ))

        return MatrizMarkov(matriz=matriz, estados=estados)
    
    
    def calcular_probabilidad(self, ocurrencias_transicion:int, frecuencia_nota_origen:int) -> float:
        return ocurrencias_transicion / frecuencia_nota_origen