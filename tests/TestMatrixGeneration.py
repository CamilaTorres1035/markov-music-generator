from services.GeneradorMatrizMarkov import GeneradorMatrizMarkov
from dto.DataTransicionAgrupada import DataTransicionAgrupada
from dto.EstadisticasDeTransicion import EstadisticasDeTransicion
from services.GeneradorProcedural import GeneradorProcedural

datos_mock = [
    DataTransicionAgrupada(
        _nota_origen=60,  # Do
        _transiciones={
            62: EstadisticasDeTransicion(_conteo=3, _tiempos=[100, 200, 300]),  # Do → Re (3 veces)
            64: EstadisticasDeTransicion(_conteo=1, _tiempos=[400]),            # Do → Mi (1 vez)
        }
    ),
    DataTransicionAgrupada(
        _nota_origen=62,  # Re
        _transiciones={
            64: EstadisticasDeTransicion(_conteo=2, _tiempos=[150, 250]),       # Re → Mi (2 veces)
            60: EstadisticasDeTransicion(_conteo=2, _tiempos=[350, 450]),       # Re → Do (2 veces)
        }
    ),
    DataTransicionAgrupada(
        _nota_origen=64,  # Mi
        _transiciones={
            60: EstadisticasDeTransicion(_conteo=1, _tiempos=[500]),            # Mi → Do (1 vez)
        }
    ),
]

generador = GeneradorMatrizMarkov(datos_mock)
matriz = generador.generar_matriz()

for estado in [60, 62, 64]:
    transiciones = matriz.obtener_transiciones(estado)
    total = sum(t._probabilidad_transicion for t in transiciones)
    print(f"Estado {estado}: suma = {total}")
    for t in transiciones:
        print(f"  → {t._nota_destino._nota_midi}: {t._probabilidad_transicion}")

generador_procedural = GeneradorProcedural(matriz)
generador_procedural.generar_secuencia(duracion_secuencia_ms=2000)