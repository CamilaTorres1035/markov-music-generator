"""
ConstructorCorpusMidi: Responsable de construir un corpus de secuencias musicales
a partir de archivos MIDI.

Adapta la lógica de sketch.py (normalización, cuantización, filtrado) para 
generar instancias de SecuenciaMusical.
"""

from music21 import converter, key, interval
from pathlib import Path
from model.NotaMusical import NotaMusical
from model.EventoMusical import EventoMusical
from model.SecuenciaMusical import SecuenciaMusical


class ConstructorCorpusMidi:
    """
    Construye un corpus de secuencias musicales a partir de archivos MIDI.
    
    Responsabilidades:
    - Cargar archivos MIDI
    - Normalizar tonalidad (Do Mayor / La Menor)
    - Cuantizar ritmo
    - Filtrar outliers
    - Convertir a estructuras de dominio (SecuenciaMusical)
    - Mantener corpus en memoria
    """
    
    # Parámetros de filtrado
    MIN_DURATION_MS = 50
    MAX_DURATION_MS = 4000
    
    def __init__(self):
        """Inicializa el corpus vacío."""
        self.corpus: list[SecuenciaMusical] = []
    
    def agregar_archivo(self, ruta: str) -> None:
        """
        Carga y procesa un archivo MIDI, agregando la secuencia al corpus.
        
        Args:
            ruta: ruta al archivo MIDI
            
        Raises:
            FileNotFoundError: si el archivo no existe
            Exception: si hay error en el procesamiento
        """
        secuencia = self._procesar_archivo(ruta)
        self.corpus.append(secuencia)
        print(f"✓ Archivo procesado: {ruta}")
        print(f"  - Eventos: {len(secuencia._lista_eventos)}")
    
    def _procesar_archivo(self, ruta: str) -> SecuenciaMusical:
        """
        Procesa un archivo MIDI individual y retorna una SecuenciaMusical.
        
        Pipeline:
        1. Cargar archivo MIDI
        2. Extraer BPM y tonalidad original
        3. Calcular transposición (sin copiar partitura)
        4. Cuantizar ritmo
        5. Extraer eventos con transposición aplicada directamente a MIDI
        
        Args:
            ruta: ruta al archivo MIDI
            
        Returns:
            SecuenciaMusical con eventos procesados
            
        Raises:
            FileNotFoundError: si el archivo no existe
            Exception: si hay error en el procesamiento
        """
        
        # Validar existencia
        path = Path(ruta)
        if not path.exists():
            raise FileNotFoundError(f"Archivo MIDI no encontrado: {ruta}")
        
        # Cargar partitura
        try:
            score = converter.parse(ruta)
        except Exception as e:
            raise Exception(f"Error al cargar MIDI {ruta}: {str(e)}")
        
        # Extraer BPM y tonalidad
        bpm = self._get_bpm(score)
        original_key = self._get_key(score)
        
        # Calcular intervalo de transposición (sin transponer la partitura)
        transposition_semitones = self._get_transposition_semitones(original_key)
        
        # Cuantizar ritmo
        try:
            score = self._quantize_rhythm(score)
        except Exception:
            # Si la cuantización falla, continuar sin ella
            pass
        
        # Extraer eventos (con transposición aplicada directamente a MIDI)
        eventos = self._extraer_eventos(score, bpm, transposition_semitones)
        
        # Crear y retornar SecuenciaMusical
        return SecuenciaMusical(eventos)
    
    def obtener_corpus(self) -> list[SecuenciaMusical]:
        """
        Retorna el corpus completo.
        
        Returns:
            list[SecuenciaMusical] con todas las secuencias procesadas
        """
        return self.corpus
    
    def limpiar_corpus(self) -> None:
        """Vacía el corpus."""
        self.corpus = []
        print("✓ Corpus limpiado")
    
    def obtener_estadisticas(self) -> dict:
        """
        Retorna estadísticas del corpus.
        
        Returns:
            dict con información de cantidad de secuencias y eventos
        """
        total_secuencias = len(self.corpus)
        total_eventos = sum(len(seq._lista_eventos) for seq in self.corpus)
        
        return {
            'total_secuencias': total_secuencias,
            'total_eventos': total_eventos,
            'promedio_eventos_por_secuencia': total_eventos / total_secuencias if total_secuencias > 0 else 0
        }
    
    # --- Métodos privados ---
    
    @staticmethod
    def _get_bpm(score) -> int:
        """
        Extrae el tempo (BPM) de la partitura.
        
        Si no encuentra tempo, retorna 120 por defecto.
        """
        tempos = score.flatten().getElementsByClass('MetronomeMark')
        if tempos:
            return int(tempos[0].number)
        return 120
    
    @staticmethod
    def _get_key(score) -> key.Key:
        """
        Analiza y retorna la tonalidad de la partitura.
        
        Si no puede detectarse, retorna Do Mayor por defecto.
        """
        try:
            return score.analyze('key')
        except:
            return key.Key('C')
    
    @staticmethod
    def _get_transposition_semitones(original_key: key.Key) -> int:
        """
        Calcula cuántos semitones se necesitan transponer.
        
        Normaliza a Do Mayor (si es mayor) o La Menor (si es menor)
        sin necesidad de copiar la partitura (mucho más eficiente).
        
        Args:
            original_key: tonalidad original detectada
            
        Returns:
            número de semitones a transponer (positivos o negativos)
        """
        # Determinar clave objetivo según modo
        if original_key.mode == 'major':
            target_tonic = 0  # Do (semitono 0)
        else:
            target_tonic = 9  # La (semitono 9)
        
        # Obtener semitono de la tónica original (0-11)
        original_semitone = original_key.tonic.pitchClass
        
        # Calcular intervalo en semitones
        transposition = target_tonic - original_semitone
        
        # Normalizar a rango [-6, 6]
        if transposition > 6:
            transposition -= 12
        elif transposition < -6:
            transposition += 12
        
        return transposition
    
    @staticmethod
    def _quantize_rhythm(score):
        """
        Cuantiza la partitura a una grilla rítmica.
        
        Reduce ruido rítmico y consolida duraciones cercanas.
        """
        return score.quantize([4, 8, 16])
    
    def _extraer_eventos(self, score, bpm: int, transposition_semitones: int = 0) -> list[EventoMusical]:
        """
        Extrae notas, acordes y silencios de la partitura.
        
        Convierte a duraciones en milisegundos, aplica filtros y crea EventoMusical.
        Aplica transposición directamente a los números MIDI (eficiente, sin deepcopy).
        
        Args:
            score: partitura cuantizada
            bpm: tempo en beats por minuto
            transposition_semitones: semitones a transponer
            
        Returns:
            list[EventoMusical] con eventos filtrados y convertidos
        """
        eventos = []
        elementos = score.flatten().notesAndRests
        
        for el in elementos:
            # Convertir quarter length a duración en milisegundos
            duration_ms = self._calculate_duration_ms(el.duration.quarterLength, bpm)
            
            # Filtrar outliers
            if not self._is_valid_duration(duration_ms):
                continue
            
            # Convertir ms a float
            duration_float = float(duration_ms)
            
            # Extraer la nota con transposición aplicada
            try:
                if el.isNote:
                    # Nota simple: aplicar transposición
                    nota_midi = el.pitch.midi + transposition_semitones
                    nota = NotaMusical(nota_midi)
                    evento = EventoMusical(nota, duration_float)
                    eventos.append(evento)
                    
                elif el.isChord:
                    # Acorde: tomar la nota más grave (bajo) con transposición
                    nota_midi = min(p.midi for p in el.pitches) + transposition_semitones
                    nota = NotaMusical(nota_midi)
                    evento = EventoMusical(nota, duration_float)
                    eventos.append(evento)
                    
                elif el.isRest:
                    # Silencio representado como nota MIDI -1
                    nota = NotaMusical(-1)
                    evento = EventoMusical(nota, duration_float)
                    eventos.append(evento)
            except Exception:
                # Saltar elementos problemáticos
                continue
        
        return eventos
    
    @staticmethod
    def _calculate_duration_ms(quarter_length: float, bpm: int) -> int:
        """
        Convierte quarter length de music21 a milisegundos.
        
        formula: (quarter_length / 4) * (60000 / bpm)
        """
        return int(quarter_length * (60000 / bpm))
    
    def _is_valid_duration(self, duration_ms: int) -> bool:
        """
        Verifica si la duración está en rango válido.
        
        Filtra outliers muy cortos (<50ms) o muy largos (>4000ms).
        """
        return self.MIN_DURATION_MS <= duration_ms <= self.MAX_DURATION_MS
