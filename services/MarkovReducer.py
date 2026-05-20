class MarkovReducer:
    @staticmethod
    def funcion_reduce(acumulador: dict[int, dict[str, int | list]], transicion:tuple[int, int, float]) -> dict[int, dict[str, int | list]]:
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