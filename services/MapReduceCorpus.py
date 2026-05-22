from typing import Callable
import dask.bag as db
from dask.distributed import Client


class MapReduceCorpus:
    def __init__(self, items: list, client: Client):
        self._items = items
        self._client = client
        print(f"Dashboard: {self._client.dashboard_link}")

    def ejecutar(
        self,
        fn_map: Callable,
        fn_reduce: Callable | None = None,
        fn_combine: Callable | None = None,
        flatten: bool = False
    ):
        """
        Ejecuta map-reduce en paralelo con Dask.

        Args:
            fn_map: Función que transforma cada item en lista de tuplas (clave, valor)
            fn_reduce: Función que agrupa tuplas. Si None, retorna tuplas planas.
            fn_combine: Función que combina dos acumuladores en paralelo.
            flatten: Si False, mantiene resultados separados por item.

        Returns:
            Si flatten=False: Lista de listas (resultados por item)
            Si flatten=True y sin reduce: Lista de tuplas combinadas
            Si flatten=True y con reduce: Tuplas agrupadas
        """
        bag_inicial = db.from_sequence(self._items, npartitions=len(self._items))
        bag_mapeado = bag_inicial.map(fn_map)

        if flatten:
            bag_mapeado = bag_mapeado.flatten()

            if fn_reduce is None or fn_combine is None:
                return bag_mapeado.compute()

            agrupado = bag_mapeado.foldby(
                key=lambda tupla: tupla[0],
                initial=dict,
                binop=fn_reduce,
                combine=fn_combine
            )
            return agrupado.compute()
        else:
            return bag_mapeado.compute()
