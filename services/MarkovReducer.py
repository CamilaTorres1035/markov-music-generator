"""
Módulo para reducir y combinar transiciones musicales en pipelines map-reduce.

Proporciona funciones de reduce y combine para Dask que agrupan transiciones MIDI
por nota de destino, calculando frecuencias y recopilando duraciones de cada transición.
"""


class MarkovReducer:
    """
    Clase de utilidad para operaciones de reducción en pipelines map-reduce de Dask.
    
    Agrupa transiciones musicales (nota_origen, nota_destino, duracion) por nota de destino,
    acumulando estadísticas de frecuencia y duraciones para construir matrices de Markov.
    
    Se utiliza en el flujo: extracción MIDI → map (transiciones) → reduce → combine → matriz Markov.
    """
    
    @staticmethod
    def funcion_reduce(acumulador: dict[int, dict[str, int | list]], transicion:tuple[int, int, int]) -> dict[int, dict[str, int | list]]:
        """
        Reduce transiciones individuales en un acumulador de estadísticas.
        
        Para cada transición procesada, agrupa por nota de destino e incrementa
        la frecuencia de esa transición, además de registrar la duración de la
        nota destino para análisis estadístico posterior.
        
        Args:
            acumulador: Diccionario que acumula estadísticas con estructura
                       {nota_destino: {"frecuencia": int, "tiempos": list[float]}}.
                       Se modifica in-place.
            transicion: Tupla (nota_origen, nota_destino, duracion_ms) extraída de archivos MIDI.
        
        Returns:
            El acumulador actualizado con las estadísticas de la nueva transición.
        """
        nota_origen, nota_destino, tiempo = transicion

        if nota_destino not in acumulador:
            acumulador[nota_destino] = {
                "frecuencia": 0,
                "tiempos" : []
            }
        
        acumulador[nota_destino]["frecuencia"] += 1
        acumulador[nota_destino]["tiempos"].append(tiempo)

        return acumulador
    
    @staticmethod
    def funcion_combine(
        acumulador1: dict[int, dict[str, int | list]],
        acumulador2: dict[int, dict[str, int | list]]
        ) -> dict[int, dict[str, int | list]]:
        """
        Combina dos acumuladores de transiciones en un resultado unificado.
        
        Fusiona dos diccionarios de estadísticas por nota de destino, sumando
        frecuencias y concatenando listas de duraciones. Utilizado en Dask para
        combinar resultados parciales de diferentes particiones.
        
        Args:
            acumulador1: Primer diccionario con estadísticas acumuladas
                        {nota_destino: {"frecuencia": int, "tiempos": list[float]}}.
            acumulador2: Segundo diccionario con estadísticas acumuladas
                        {nota_destino: {"frecuencia": int, "tiempos": list[float]}}.
        
        Returns:
            Diccionario fusionado con frecuencias sumadas y duraciones concatenadas.
            Para notas destino presentes en ambos acumuladores, se suman frecuencias
            y se extienden las listas de tiempos.
        """

        resultado = dict(acumulador1)

        for nota_destino, datos in acumulador2.items():

            # Si la transición aún no existe
            if nota_destino not in resultado:

                resultado[nota_destino] = {
                    "frecuencia": datos["frecuencia"],
                    "tiempos": list(datos["tiempos"])
                }

            # Si ya existe, combinar estadísticas
            else:

                resultado[nota_destino]["frecuencia"] += datos["frecuencia"]

                resultado[nota_destino]["tiempos"].extend(
                    datos["tiempos"]
                )

        return resultado