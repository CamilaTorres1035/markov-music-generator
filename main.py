import os
from pathlib import Path

from services.ConstructorCorpusMidi import ConstructorCorpusMidi
from services.MarkovMapper import MarkovMapper
from services.MarkovReducer import MarkovReducer
from services.OrquestadorMapReduce import OrquestadorMapReduce


def main():
    # 1. Cargar archivos MIDI del directorio /data
    constructor = ConstructorCorpusMidi()
    data_dir = Path("data")
    
    # Cargar todos los archivos MIDI
    midi_files = sorted(list(data_dir.rglob("*.midi")) + list(data_dir.rglob("*.mid")))
    
    print(f"Encontrados {len(midi_files)} archivos MIDI")
    print()
    
    # Procesar todos los archivos MIDI
    errores = 0
    for i, midi_file in enumerate(midi_files, 1):
        try:
            constructor.agregar_archivo(str(midi_file))
        except Exception as e:
            errores += 1
            print(f"✗ Error en {midi_file}: {str(e)[:80]}")
    
    print(f"\nProcesamiento completado: {len(midi_files) - errores}/{len(midi_files)} archivos exitosos")
    
    print()
    
    # 2. Obtener corpus procesado
    corpus = constructor.obtener_corpus()
    stats = constructor.obtener_estadisticas()
    
    print(f"Estadísticas del corpus:")
    print(f"  - Secuencias: {stats['total_secuencias']}")
    print(f"  - Total eventos: {stats['total_eventos']}")
    print(f"  - Promedio por secuencia: {stats['promedio_eventos_por_secuencia']:.2f}")
    print()
    
    if stats['total_secuencias'] == 0:
        print("No hay secuencias en el corpus. Finalizando.")
        return
    
    # 3. Procesar con MapReduce
    print("Iniciando MapReduce...")
    orquestador = OrquestadorMapReduce(corpus=corpus)
    resultado = orquestador.ejecutar_map_reduce(
        MarkovMapper.map_secuencia,
        MarkovReducer.funcion_reduce,
        MarkovReducer.funcion_combine
    )
    
    print("Procesamiento completado. Presiona ENTER para cerrar...")
    input()
    orquestador.cerrar()
    
    print("\nMatriz de Transiciones Markov:")
    print("=" * 60)
    for data in resultado:
        print(f"Nota origen: {data._nota_origen}")
        for nota_destino, estadisticas in data._transiciones.items():
            print(
                f"  -> {nota_destino} | "
                f"conteo={estadisticas._conteo} | "
                f"tiempos={estadisticas._tiempos}"
            )
        print()


if __name__ == "__main__":
    main()