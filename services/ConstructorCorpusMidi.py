from music21 import converter, key
from pathlib import Path
from model.NotaMusical import NotaMusical
from model.EventoMusical import EventoMusical
from model.SecuenciaMusical import SecuenciaMusical
import dask.bag as db


class ConstructorCorpusMidi:
    MIN_DURATION_MS = 50
    MAX_DURATION_MS = 4000

    def __init__(self):
        self.corpus: list[SecuenciaMusical] = []

    def agregar_archivo(self, ruta: str) -> None:
        secuencia = self._procesar_archivo(ruta)
        self.corpus.append(secuencia)
        print(f"✓ Archivo procesado: {ruta}")
        print(f"  - Eventos: {len(secuencia._lista_eventos)}")

    def agregar_archivos(self, rutas: list[str]) -> None:
        bag = db.from_sequence(rutas, npartitions=64)
        secuencias = bag.map(ConstructorCorpusMidi._procesar_archivo_static).compute()
        self.corpus.extend(secuencias)
        print(f"✓ {len(secuencias)} archivos procesados")

    def _procesar_archivo(self, ruta: str) -> SecuenciaMusical:
        tuplas = ConstructorCorpusMidi._extraer_tuplas_archivo(ruta)
        return ConstructorCorpusMidi._ensamblar_secuencia(tuplas)

    @staticmethod
    def _procesar_archivo_static(ruta: str) -> SecuenciaMusical:
        tuplas = ConstructorCorpusMidi._extraer_tuplas_archivo(ruta)
        return ConstructorCorpusMidi._ensamblar_secuencia(tuplas)

    @staticmethod
    def _extraer_tuplas_archivo(ruta: str) -> list[tuple[int, int, float]]:
        """Extrae tuplas de transiciones (nota_origen, nota_destino, duracion_destino) desde un archivo MIDI.
        Pensado para usarse en pipelines de Dask con datos primitivos para Markov."""
        from music21 import converter
        from pathlib import Path

        path = Path(ruta)
        if not path.exists():
            raise FileNotFoundError(f"Archivo MIDI no encontrado: {ruta}")

        try:
            score = converter.parse(ruta)
        except Exception as e:
            raise Exception(f"Error al cargar MIDI {ruta}: {str(e)}")

        bpm = ConstructorCorpusMidi._get_bpm(score)
        original_key = ConstructorCorpusMidi._get_key(score)
        transposition_semitones = ConstructorCorpusMidi._get_transposition_semitones(original_key)

        eventos = ConstructorCorpusMidi._extraer_tuplas_eventos_static(score, bpm, transposition_semitones)
        return ConstructorCorpusMidi._convertir_eventos_a_transiciones(eventos)

    @staticmethod
    def _ensamblar_secuencia(tuplas: list[tuple[int, float]]) -> SecuenciaMusical:
        """Ensambla una SecuenciaMusical a partir de tuplas crudas.
        Se ejecuta fuera del contexto de Dask."""
        eventos = [EventoMusical(NotaMusical(nota_midi), duracion) for nota_midi, duracion in tuplas]
        return SecuenciaMusical(eventos)

    def obtener_corpus(self) -> list[SecuenciaMusical]:
        return self.corpus

    def limpiar_corpus(self) -> None:
        self.corpus = []
        print("✓ Corpus limpiado")

    def obtener_estadisticas(self) -> dict:
        total_secuencias = len(self.corpus)
        total_eventos = sum(len(seq._lista_eventos) for seq in self.corpus)

        return {
            'total_secuencias': total_secuencias,
            'total_eventos': total_eventos,
            'promedio_eventos_por_secuencia': total_eventos / total_secuencias if total_secuencias > 0 else 0
        }

    @staticmethod
    def _get_bpm(score) -> int:
        tempos = score.flatten().getElementsByClass('MetronomeMark')
        if tempos:
            return int(tempos[0].number)
        return 120

    @staticmethod
    def _get_key(score):
        try:
            return score.analyze('key')
        except:
            return key.Key('C')

    @staticmethod
    def _get_transposition_semitones(original_key) -> int:
        if original_key.mode == 'major':
            target_tonic = 0
        else:
            target_tonic = 9

        original_semitone = original_key.tonic.pitchClass
        transposition = target_tonic - original_semitone

        if transposition > 6:
            transposition -= 12
        elif transposition < -6:
            transposition += 12

        return transposition

    @staticmethod
    def _quantize_rhythm(score):
        return score.quantize([4, 8, 16])

    @staticmethod
    def _extraer_tuplas_eventos_static(score, bpm: int, transposition_semitones: int = 0) -> list[tuple[int, float]]:
        tuplas = []
        elementos = score.flatten().notesAndRests
        resolucion_ms = 50
        
        for el in elementos:
            duration_ms_raw = el.duration.quarterLength * (60000 / bpm)
            # Divide, redondea al entero más cercano, y vuelve a multiplicar
            # Ej: 123ms -> round(2.46) * 50 -> 2 * 50 -> 100ms
            duration_ms = int(round(duration_ms_raw / resolucion_ms) * resolucion_ms)
            # Prevenir que notas muy rápidas ("grace notes") queden con duración 0
            if duration_ms == 0 and duration_ms_raw > 0:
                duration_ms = resolucion_ms
            if not (ConstructorCorpusMidi.MIN_DURATION_MS <= duration_ms <= ConstructorCorpusMidi.MAX_DURATION_MS):
                continue
            duration_float = float(duration_ms)
            try:
                if el.isNote:
                    tuplas.append((el.pitch.midi + transposition_semitones, duration_float))
                elif el.isChord:
                    tuplas.append((min(p.midi for p in el.pitches) + transposition_semitones, duration_float))
                elif el.isRest:
                    tuplas.append((-1, duration_float))
            except Exception:
                continue

        return tuplas

    @staticmethod
    def _convertir_eventos_a_transiciones(eventos: list[tuple[int, float]]) -> list[tuple[int, int, float]]:
        """Convierte lista de eventos en transiciones (nota_origen, nota_destino, duracion_destino)."""
        transiciones = []
        for i in range(len(eventos) - 1):
            nota_origen, _ = eventos[i]
            nota_destino, duracion_destino = eventos[i + 1]
            transiciones.append((nota_origen, nota_destino, duracion_destino))
        return transiciones

    @staticmethod
    def _calculate_duration_ms(quarter_length: float, bpm: int) -> int:
        return int(quarter_length * (60000 / bpm))