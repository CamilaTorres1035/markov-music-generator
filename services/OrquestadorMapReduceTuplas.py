import dask.bag as db
from dask.distributed import Client
from dto.DataTransicionAgrupada import DataTransicionAgrupada


class OrquestadorMapReduceTuplas:
    """Orquestador que aplica map-reduce a tuplas crudas de transiciones.

    Recibe tuplas (nota_origen, nota_destino, duracion) y aplica reduce
    para agruparlas y generar estructura de matriz de Markov."""

    def __init__(self, tuplas: list[tuple[int, int, float]], client: Client):
        self._tuplas = tuplas
        self._client = client
        print(f"Dashboard: {self._client.dashboard_link}")

    def ejecutar_map_reduce(
        self,
        funcion_reduce,
        funcion_combine
    ) -> list[DataTransicionAgrupada]:
        """Aplica map-reduce a tuplas crudas.

        Args:
            funcion_reduce: Función que agrupa tuplas (ej: MarkovReducer.funcion_reduce)
            funcion_combine: Función que combina acumuladores (ej: MarkovReducer.funcion_combine)

        Returns:
            Lista de DataTransicionAgrupada con transiciones agrupadas
        """
        bag_inicial = db.from_sequence(self._tuplas)

        agrupado = bag_inicial.foldby(
            key=lambda tupla: tupla[0],
            initial=dict,
            binop=funcion_reduce,
            combine=funcion_combine
        )

        resultado = agrupado.compute()
        resultado_transformado = self._transformar_datos_agrupados(resultado)
        return resultado_transformado

    @staticmethod
    def _transformar_datos_agrupados(resultado: list[tuple[int, dict]]) -> list[DataTransicionAgrupada]:
        """Transforma resultado de foldby a DTOs DataTransicionAgrupada."""
        from dto.EstadisticasDeTransicion import EstadisticasDeTransicion

        resultado_transformado = []
        for tupla in resultado:
            nota_origen, transiciones = tupla
            aux = {}
            for clave_destino, informacion in transiciones.items():
                dto = EstadisticasDeTransicion(informacion["frecuencia"], informacion["tiempos"])
                aux[clave_destino] = dto

            resultado_transformado.append(DataTransicionAgrupada(nota_origen, aux))

        return resultado_transformado
