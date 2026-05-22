import os
from pathlib import Path

from services.ConstructorCorpusMidi import ConstructorCorpusMidi
from services.MarkovReducer import MarkovReducer
from services.OrquestadorMapReduceCorpus import OrquestadorMapReduceCorpus
from services.GeneradorMatrizMarkov import GeneradorMatrizMarkov
from services.GeneradorProceduralSuavizado import GeneradorProceduralSuavizado
from services.ExportadorMidi import ExportadorMidi
from services.TransformadorTransiciones import TransformadorTransiciones
from dask.distributed import Client


def main():
    # 1. Cargar archivos MIDI del directorio /data
    data_dir = Path("data")

    # Creamos un cluster (Client) local con dask
    client = Client(n_workers=os.cpu_count(), threads_per_worker=1, dashboard_address=':5847')
    print(client.dashboard_link)

    # Creamos una lista con los archivos .midi o .mid
    midi_files = sorted(list(data_dir.rglob("*.midi")) + list(data_dir.rglob("*.mid")))
    print(f"Encontrados {len(midi_files)} archivos MIDI")

    rutas = [str(f) for f in midi_files] #La misma lista se reconvierte a cadenas de texto

    # 2. Procesar archivos con map-reduce completo
    print("\nProcesando archivos MIDI con map-reduce...")

    """
        Instanciamos un objeto de la clase orquestadora del corpus.
        En este punto, se realizan las trasnformaciones en el orden:
        Map: archivo MIDI → lista de tuplas (nota_origen, nota_destino, duracion) 
        Reduce: agrupa tuplas por frecuencia
    """
    orquestador_corpus = OrquestadorMapReduceCorpus(rutas=rutas, client=client)
    tuplas_reducidas = orquestador_corpus.procesar_y_reducir(
        funcion_extractor=ConstructorCorpusMidi._extraer_tuplas_archivo,
        fn_reduce=MarkovReducer.funcion_reduce,
        fn_combine=MarkovReducer.funcion_combine
    )

    print(f"Procesamiento completado: {len(midi_files)} archivos procesados")
    print(f"Tuplas reducidas: {len(tuplas_reducidas)}")

    # 3. Transformar tuplas reducidas a DataTransicionAgrupada
    print("\nTransformando tuplas a estructura de matriz...")
    resultado_transformado = TransformadorTransiciones.a_dtos(tuplas_reducidas)

    print(f"Transiciones agrupadas: {len(resultado_transformado)} estados encontrados")

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
