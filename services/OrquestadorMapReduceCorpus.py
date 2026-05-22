from dask.distributed import Client
from services.MapReduceCorpus import MapReduceCorpus


class OrquestadorMapReduceCorpus:
    """Orquestador que procesa archivos MIDI en paralelo y aplica map-reduce completo.

    Responsabilidad única: archivos MIDI → tuplas reducidas/agrupadas
    Sin construir SecuenciaMusical (eso es responsabilidad del cliente).
    """

    def __init__(self, rutas: list[str], client: Client):
        self._rutas = rutas
        self._client = client

    def procesar_y_reducir(self, funcion_extractor, fn_reduce, fn_combine):
        """Procesa archivos MIDI aplicando map-reduce completo.

        Args:
            fn_reduce: Función que reduce tuplas (ej: MarkovReducer.funcion_reduce)
            fn_combine: Función que combina acumuladores (ej: MarkovReducer.funcion_combine)

        Returns:
            list[tuple]: Tuplas reducidas/agrupadas (nota_origen, dict_transiciones)
        """
        orquestador = MapReduceCorpus(self._rutas, self._client)

        # Map: archivo → tuplas, Reduce: agrupa tuplas por nota
        tuplas_reducidas = orquestador.ejecutar(
            fn_map=funcion_extractor,
            fn_reduce=fn_reduce,
            fn_combine=fn_combine,
            flatten=True
        )

        return tuplas_reducidas



