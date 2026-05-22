from typing import Callable
import dask.bag as db
from dask.distributed import Client
"""
Módulo que implementa el patrón Map-Reduce distribuido sobre una colección
de ítems arbitrarios usando Dask como motor de cómputo paralelo.

Está diseñado para ser usado por orquestadores de alto nivel (como
OrquestadorMapReduceCorpus) que necesitan aplicar transformaciones y
agregaciones sobre grandes volúmenes de datos de forma eficiente.
"""


class MapReduceCorpus:
    """
    Motor genérico de Map-Reduce distribuido sobre una colección de ítems.

    Encapsula la lógica de paralelización con Dask, permitiendo aplicar
    una función de mapeo y, opcionalmente, una de reducción sobre cualquier
    lista de ítems (rutas de archivos, objetos, cadenas de texto, etc.).

    Esta clase no conoce el dominio de los datos: es responsabilidad del
    llamador proveer las funciones ``fn_map``, ``fn_reduce`` y ``fn_combine``
    adecuadas al problema (p. ej. extracción de n-gramas MIDI, conteo de
    palabras, cálculo de estadísticas, etc.).

    Attributes:
        _items (list): Colección de ítems sobre la que se ejecutará el map-reduce.
        _client (Client): Cliente Dask que gestiona el clúster de workers.
    """
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
        Ejecuta el pipeline Map-Reduce en paralelo sobre ``_items``.

        El pipeline tiene tres fases opcionales:

        1. **Map**: aplica ``fn_map`` a cada ítem de forma paralela.
           Se espera que retorne una lista de tuplas ``(clave, valor)``.
        2. **Flatten** *(opcional)*: aplana los resultados individuales
           en una única secuencia de tuplas.
        3. **Reduce** *(opcional)*: agrupa y combina las tuplas por clave
           usando ``foldby`` de Dask.

        El comportamiento varía según los parámetros:

        +------------+---------------------+-------------------------------------------+
        | flatten    | fn_reduce/fn_combine | Resultado                                 |
        +============+=====================+===========================================+
        | ``False``  | cualquiera          | ``list[Any]`` — resultados por ítem       |
        +------------+---------------------+-------------------------------------------+
        | ``True``   | ``None``            | ``list[tuple]`` — tuplas aplanadas        |
        +------------+---------------------+-------------------------------------------+
        | ``True``   | provistos           | ``list[tuple]`` — tuplas reducidas        |
        +------------+---------------------+-------------------------------------------+

        Args:
            fn_map (Callable): Función aplicada a cada ítem. Debe retornar
                una lista de tuplas (clave, valor) cuando se usa con
                flatten=True y reduce, o cualquier valor si solo se mapea.
            fn_reduce (Callable | None): Función binaria (acumulador, tupla) → acumulador
                que reduce las tuplas agrupadas por clave. Requiere fn_combine.
                Si es None, se omite la fase de reducción.
            fn_combine (Callable | None): Función binaria (acumulador, acumulador) → acumulador
                que fusiona dos acumuladores parciales generados en distintos workers.
                Necesaria para garantizar la correctitud en entornos distribuidos.
                Si es None, se omite la fase de reducción.
            flatten (bool): Si True, aplana los resultados del map antes
                de continuar el pipeline. Necesario para la fase de reducción.
                Por defecto False.

        Returns:
            list: El tipo concreto depende de los parámetros (ver tabla superior).
                En el caso de reducción, cada elemento es una tupla
                (clave, acumulador_final).

        Note:
            fn_reduce y fn_combine deben proveerse juntas: si una es
            None y la otra no, se omite la reducción y se retornan las
            tuplas aplanadas sin agrupar.
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
