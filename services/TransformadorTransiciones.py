from dto.DataTransicionAgrupada import DataTransicionAgrupada
from dto.EstadisticasDeTransicion import EstadisticasDeTransicion


class TransformadorTransiciones:
    @staticmethod
    def a_dtos(resultado: list[tuple[int, dict]]) -> list[DataTransicionAgrupada]:
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