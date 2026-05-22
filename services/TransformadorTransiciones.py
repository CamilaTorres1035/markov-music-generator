from dto.DataTransicionAgrupada import DataTransicionAgrupada
from dto.EstadisticasDeTransicion import EstadisticasDeTransicion


"""
Módulo para transformar tuplas reducidas en estructuras de datos de transiciones.

Convierte el resultado del pipeline map-reduce (tuplas primitivas con estadísticas
agrupadas) en objetos DTOs (DataTransicionAgrupada y EstadisticasDeTransicion)
que facilitan el acceso y manipulación de datos para la generación de matrices de Markov.
"""


class TransformadorTransiciones:
    """
    Clase de utilidad que transforma tuplas reducidas en objetos de transferencia de datos.
    
    Convierte el resultado del pipeline map-reduce en una estructura de DTOs más
    accesible y tipada. Actúa como adaptador entre el resultado crudo del map-reduce
    (tuplas con diccionarios) y las estructuras de datos especializadas del dominio.
    
    Se utiliza en main.py en el paso 3 de la cadena de procesamiento:
    tuplas_reducidas → DTOs → matriz de Markov.
    """
    
    @staticmethod
    def a_dtos(resultado: list[tuple[int, dict]]) -> list[DataTransicionAgrupada]:
        """
        Transforma tuplas reducidas en una lista de objetos DataTransicionAgrupada.
        
        Recibe el resultado del pipeline map-reduce (lista de tuplas donde cada tupla
        contiene una nota origen y un diccionario de transiciones con estadísticas).
        Convierte cada tupla en un objeto DataTransicionAgrupada, creando objetos
        EstadisticasDeTransicion para cada transición destino.
        
        Args:
            resultado: Lista de tuplas (nota_origen, transiciones_dict) donde:
                      - nota_origen: número MIDI
                      - transiciones_dict: diccionario con estructura
                        {nota_destino: {"frecuencia": int, "tiempos": list[float]}}
                      Típicamente el resultado de OrquestadorMapReduceCorpus.procesar_y_reducir()
        
        Returns:
            Lista de objetos DataTransicionAgrupada, uno por cada nota origen,
            conteniendo todas las transiciones posibles desde esa nota con sus
            estadísticas encapsuladas en objetos EstadisticasDeTransicion.
        """
        resultado_transformado = []

        for nota_origen, transiciones in resultado:
            aux = {}

            for clave_destino, informacion in transiciones.items():
                dto = EstadisticasDeTransicion(
                    informacion["frecuencia"],
                    informacion["tiempos"]
                )
                aux[clave_destino] = dto

            resultado_transformado.append(
                DataTransicionAgrupada(nota_origen, aux)
            )

        return resultado_transformado