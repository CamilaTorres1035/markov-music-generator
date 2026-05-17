from model.SecuenciaMusical import SecuenciaMusical
from typing import Callable
import dask.bag as db
from dto.DataTransicionAgrupada import DataTransicionAgrupada
from dto.EstadisticasDeTransicion import EstadisticasDeTransicion
from dask.distributed import Client

class OrquestadorMapReduce:
    _corpus: list[SecuenciaMusical]
    _client: Client

    def __init__(self, corpus:list[SecuenciaMusical]):
        self._corpus = corpus
        self._client = Client(n_workers=4,dashboard_address=':5847')
        print(f"Dashboard: {self._client.dashboard_link}")

    def ejecutar_map_reduce(self, funcion_map:Callable, funcion_reduce:Callable, funcion_combine:Callable):
        ##Paso 1: crear el bag de dask
        bag_inicial = db.from_sequence(self._corpus)
        ##Paso 2: Aplicar Map
        bag_mapeado = bag_inicial.map(funcion_map)
        bag_mapeado = bag_mapeado.flatten() ##Elimina la lista de listas en una sola lista global
        ##Paso 3: Shuffle y Reduce
        agrupado = bag_mapeado.foldby(
            key= lambda tupla: tupla[0],
            initial=dict,
            binop=funcion_reduce,
            combine=funcion_combine
        )

        ##Paso 4: ejecutar MapReduce
        resultado = agrupado.compute()
        resultado_transformado = self.transformar_datos_agrupados(resultado)
        return resultado_transformado
    
    def transformar_datos_agrupados(self, resultado:list[tuple[int, dict]]) -> list[DataTransicionAgrupada]:
        ##Recorre el resultado y crea la lista con dto's trasnformada
        resultado_transformado = []
        for tupla in resultado:
            nota_origen, transiciones = tupla
            aux = {}
            for clave_destino, informacion in transiciones.items():
                dto = EstadisticasDeTransicion(informacion["frecuencia"], informacion["tiempos"])
                aux[clave_destino] = dto
            
            resultado_transformado.append(DataTransicionAgrupada(nota_origen, aux))
        
        return resultado_transformado
    
    def cerrar(self):
        self._client.close()



            

