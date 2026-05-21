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
        return ConstructorCorpusMidi._procesar_archivo_static(ruta)

    @staticmethod
    def _procesar_archivo_static(ruta: str) -> SecuenciaMusical:
        from music21 import converter, key
        from model.NotaMusical import NotaMusical
        from model.EventoMusical import EventoMusical
        from model.SecuenciaMusical import SecuenciaMusical
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

        try:
            score = ConstructorCorpusMidi._quantize_rhythm(score)
        except Exception:
            pass

        eventos = ConstructorCorpusMidi._extraer_eventos_static(score, bpm, transposition_semitones)
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
    def _get_key(score) -> key.Key:
        try:
            return score.analyze('key')
        except:
            return key.Key('C')
    
    @staticmethod
    def _get_transposition_semitones(original_key: key.Key) -> int:
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
    def _extraer_eventos_static(score, bpm: int, transposition_semitones: int = 0) -> list[EventoMusical]:
        from model.NotaMusical import NotaMusical
        from model.EventoMusical import EventoMusical

        eventos = []
        elementos = score.flatten().notesAndRests
        
        for el in elementos:
            duration_ms = int(el.duration.quarterLength * (60000 / bpm))
            if not (ConstructorCorpusMidi.MIN_DURATION_MS <= duration_ms <= ConstructorCorpusMidi.MAX_DURATION_MS):
                continue
            duration_float = float(duration_ms)
            try:
                if el.isNote:
                    eventos.append(EventoMusical(NotaMusical(el.pitch.midi + transposition_semitones), duration_float))
                elif el.isChord:
                    eventos.append(EventoMusical(NotaMusical(min(p.midi for p in el.pitches) + transposition_semitones), duration_float))
                elif el.isRest:
                    eventos.append(EventoMusical(NotaMusical(-1), duration_float))
            except Exception:
                continue
        
        return eventos

    def _extraer_eventos(self, score, bpm: int, transposition_semitones: int = 0) -> list[EventoMusical]:
        return ConstructorCorpusMidi._extraer_eventos_static(score, bpm, transposition_semitones)

    @staticmethod
    def _calculate_duration_ms(quarter_length: float, bpm: int) -> int:
        return int(quarter_length * (60000 / bpm))
    
    def _is_valid_duration(self, duration_ms: int) -> bool:
        return self.MIN_DURATION_MS <= duration_ms <= self.MAX_DURATION_MS