from model.SecuenciaMusical import SecuenciaMusical
class MarkovMapper:
    @staticmethod
    def map_secuencia(secuencia_musical: SecuenciaMusical) -> list[tuple[int, int, float]]:
        """
        Convierte una MusicalSequence en una lista de transiciones.

        Parámetro:
            secuencia_musical (SecuenciaMusical)

        Retorna:
            list[tuple[int, int, int]]
            Formato:
            (nota_origen, nota_destino, duración)
        """
        transiciones = []
        eventos = secuencia_musical._lista_eventos

        for i in range(len(eventos) - 1):
            evento_actual = eventos[i]
            evento_siguiente = eventos[i + 1]
            transiciones.append((evento_actual._nota._nota_midi, evento_siguiente._nota._nota_midi, evento_siguiente._duracion))
        
        return transiciones