"""
test.py: Archivo de prueba para ConstructorCorpusMidi y ExportadorMidi

Demuestra el flujo completo:
1. Cargar un archivo MIDI
2. Procesar y construir corpus
3. Exportar resultado
"""

from services import ConstructorCorpusMidi, ExportadorMidi
from pathlib import Path


def main():
    print("=== Test: Markov Music Generator ===\n")
    
    # Crear instancias de los servicios
    constructor = ConstructorCorpusMidi()
    exportador = ExportadorMidi()
    
    # Ruta del archivo MIDI de prueba
    archivo_midi = "ViridianForest.mid"
    
    if not Path(archivo_midi).exists():
        print(f"❌ Error: Archivo '{archivo_midi}' no encontrado")
        return
    
    print("1️⃣  Procesando archivo MIDI...")
    try:
        constructor.agregar_archivo(archivo_midi)
        print(f"✓ Archivo cargado exitosamente\n")
    except Exception as e:
        print(f"❌ Error al procesar: {e}\n")
        return
    
    # Obtener estadísticas
    print("2️⃣  Estadísticas del corpus:")
    stats = constructor.obtener_estadisticas()
    print(f"   - Secuencias: {stats['total_secuencias']}")
    print(f"   - Eventos totales: {stats['total_eventos']}")
    print(f"   - Promedio eventos/secuencia: {stats['promedio_eventos_por_secuencia']:.2f}\n")
    
    # Obtener la secuencia procesada
    print("3️⃣  Exportando secuencia procesada...")
    corpus = constructor.obtener_corpus()
    
    if corpus:
        secuencia = corpus[0]
        try:
            ruta_exportada = exportador.exportar_secuencia(
                secuencia,
                "output",
                "ViridianForest_procesado"
            )
            print(f"✓ Archivo exportado: {ruta_exportada}\n")
        except Exception as e:
            print(f"❌ Error al exportar: {e}\n")
            return
    
    print("=" * 40)
    print("✅ Prueba completada exitosamente")
    print("=" * 40)


if __name__ == "__main__":
    main()
