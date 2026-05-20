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
        print(f"  - Eventos: {len(secuencia._lista_notas)}")
    
    def _procesar_archivo(self, ruta: str) -> SecuenciaMusical:
        """
        Procesa un archivo MIDI individual y retorna una SecuenciaMusical.
        
        Pipeline:
        1. Cargar archivo MIDI
        2. Extraer BPM y tonalidad original
        3. Normalizar tonalidad
        4. Cuantizar ritmo
        5. Filtrar y convertir a EventoMusical
        
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
        
        # Normalizar tonalidad
        score = self._normalize_key(score, original_key)
        
        # Cuantizar ritmo
        score = self._quantize_rhythm(score)
        
        # Extraer eventos
        eventos = self._extraer_eventos(score, bpm)
        
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
        total_eventos = sum(len(seq._lista_notas) for seq in self.corpus)
        
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
    def _normalize_key(score, original_key: key.Key):
        """
        Transpone la partitura a Do Mayor (si es mayor) o La Menor (si es menor).
        
        Esto normaliza todas las canciones al mismo "idioma tonal".
        """
        # Determinar clave objetivo según modo
        if original_key.mode == 'major':
            target_key = key.Key('C')
        else:
            target_key = key.Key('a')
        
        # Calcular intervalo de transposición
        transposition_interval = interval.Interval(
            original_key.tonic,
            target_key.tonic
        )
        
        # Transponer
        return score.transpose(transposition_interval)
    
    @staticmethod
    def _quantize_rhythm(score):
        """
        Cuantiza la partitura a una grilla rítmica.
        
        Reduce ruido rítmico y consolida duraciones cercanas.
        """
        return score.quantize([4, 8, 16])
    
    def _extraer_eventos(self, score, bpm: int) -> list[EventoMusical]:
        """
        Extrae notas, acordes y silencios de la partitura.
        
        Convierte a duraciones en milisegundos, aplica filtros y crea EventoMusical.
        
        Args:
            score: partitura normalizada y cuantizada
            bpm: tempo en beats por minuto
            
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
            
            # Convertir ms a float (suponiendo que EventoMusical._duracion es en milisegundos)
            duration_float = float(duration_ms)
            
            # Extraer la nota (resolviendo acordes y silencios)
            if el.isNote:
                # Nota simple
                nota = NotaMusical(el.pitch.midi)
                evento = EventoMusical(nota, duration_float)
                eventos.append(evento)
                
            elif el.isChord:
                # Acorde: tomar la nota más aguda (soprano)
                nota = NotaMusical(el[-1].pitch.midi)
                evento = EventoMusical(nota, duration_float)
                eventos.append(evento)
                
            elif el.isRest:
                # Silencio representado como nota MIDI -1
                nota = NotaMusical(-1)
                evento = EventoMusical(nota, duration_float)
                eventos.append(evento)
        
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
