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