import os
from pathlib import Path

from services.ConstructorCorpusMidi import ConstructorCorpusMidi
from services.MarkovMapper import MarkovMapper
from services.MarkovReducer import MarkovReducer
from services.OrquestadorMapReduce import OrquestadorMapReduce
from services.GeneradorMatrizMarkov import GeneradorMatrizMarkov
from services.GeneradorProceduralSuavizado import GeneradorProceduralSuavizado
from services.ExportadorMidi import ExportadorMidi
from dask.distributed import Client


def main():
    # 1. Cargar archivos MIDI del directorio /data
    constructor = ConstructorCorpusMidi()
    data_dir = Path("data")
    client = Client(n_workers=os.cpu_count(), threads_per_worker= 1 , dashboard_address=':5847')
    print(client.dashboard_link)

    midi_files = sorted(list(data_dir.rglob("*.midi")) + list(data_dir.rglob("*.mid")))
    print(f"Encontrados {len(midi_files)} archivos MIDI")

    rutas = [str(f) for f in midi_files]
    constructor.agregar_archivos(rutas)

    print(f"\nProcesamiento completado: {len(midi_files)} archivos procesados")

    # 2. Obtener corpus procesado
    corpus = constructor.obtener_corpus()
    stats = constructor.obtener_estadisticas()
    
    print(f"\nEstadísticas del corpus:")
    print(f"  - Secuencias: {stats['total_secuencias']}")
    print(f"  - Total eventos: {stats['total_eventos']}")
    print(f"  - Promedio por secuencia: {stats['promedio_eventos_por_secuencia']:.2f}")
    
    if stats['total_secuencias'] == 0:
        print("No hay secuencias en el corpus. Finalizando.")
        return
    
    

    # 3. MapReduce
    print("\nIniciando MapReduce...")
    orquestador = OrquestadorMapReduce(corpus=corpus, client=client)
    resultado_transformado = orquestador.ejecutar_map_reduce(
        MarkovMapper.map_secuencia,
        MarkovReducer.funcion_reduce,
        MarkovReducer.funcion_combine
    )

    print(f"MapReduce completado: {len(resultado_transformado)} estados encontrados")

    # 4. Generar matriz de Markov
    print("\nGenerando matriz de Markov...")
    generador_matriz = GeneradorMatrizMarkov(resultado_transformado)
    matriz = generador_matriz.generar_matriz()
    print(f"Matriz generada con {len(matriz._estados)} estados")

    # 5. Generar secuencia procedural
    print("\nGenerando secuencia musical...")
    generador_procedural = GeneradorProceduralSuavizado(matriz)
    secuencia = generador_procedural.generar_secuencia(duracion_secuencia_ms=30000)
    
    print(f"Secuencia generada: {len(secuencia._lista_eventos)} eventos")
    for evento in secuencia._lista_eventos:
        print(f"  Nota: {evento._nota._nota_midi}, Duración: {evento._duracion}ms")

    # 6. Exportar secuencia a MIDI
    print("\nExportando secuencia a MIDI...")
    exportador = ExportadorMidi()
    ruta = exportador.exportar_secuencia(
        secuencia=secuencia,
        ruta_archivo="output",
        nombre_archivo="secuencia_generada"
    )
    print(f"Archivo guardado en: {ruta}")
    client.close()


if __name__ == "__main__":
    main()