from model.SecuenciaMusical import SecuenciaMusical
from typing import Callable
import dask.bag as db
from dto.DataTransicionAgrupada import DataTransicionAgrupada
from dask.distributed import Client
from services.TransformadorTransiciones import TransformadorTransiciones

class OrquestadorMapReduce:
    _corpus: list[SecuenciaMusical]
    _client: Client

    def __init__(self, corpus:list[SecuenciaMusical], client:Client):
        self._corpus = corpus
        self._client = client
        print(f"Dashboard: {self._client.dashboard_link}")

    def ejecutar_map_reduce(self, funcion_map:Callable, funcion_reduce:Callable, funcion_combine:Callable) -> list[DataTransicionAgrupada]:
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
        resultado_transformado = TransformadorTransiciones.a_dtos(resultado)
        return resultado_transformado
    



            

