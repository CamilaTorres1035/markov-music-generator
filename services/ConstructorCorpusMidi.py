from music21 import converter, key
from pathlib import Path


"""
Módulo para extraer transiciones musicales de archivos MIDI.

Proporciona utilidades para procesar archivos MIDI y extraer tuplas de transiciones
en formato (nota_origen, nota_destino, duracion_destino) para usar en cadenas de Markov.
"""


class ConstructorCorpusMidi:
    """
    Clase de utilidad para extraer transiciones musicales de archivos MIDI.
    
    Proporciona métodos estáticos para procesar archivos MIDI, normalizar tonalidades,
    extraer eventos musicales y convertirlos en transiciones para modelos de Markov.
    """
    
    MIN_DURATION_MS = 50
    MAX_DURATION_MS = 4000

    @staticmethod
    def _extraer_tuplas_archivo(ruta: str) -> list[tuple[int, int, float]]:
        """
        Extrae tuplas de transiciones desde un archivo MIDI.
        
        Carga un archivo MIDI, normaliza su tonalidad, extrae eventos musicales
        y los convierte en tuplas de transiciones (nota_origen, nota_destino, duracion_destino).
        
        Args:
            ruta: Ruta al archivo MIDI a procesar.
            
        Returns:
            Lista de tuplas (nota_origen, nota_destino, duracion_destino) donde
            nota_origen y nota_destino son valores MIDI y duracion_destino es milisegundos.
            
        Raises:
            FileNotFoundError: Si el archivo MIDI no existe.
            Exception: Si hay error al procesar el archivo MIDI.
        """
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
    def _get_bpm(score) -> int:
        """
        Extrae el tempo (BPM) de una partitura MIDI.
        
        Busca marcas de metrónomo en la partitura. Si no las encuentra,
        retorna 120 BPM como valor por defecto.
        
        Args:
            score: Partitura music21 a procesar.
            
        Returns:
            Tempo en BPM.
        """
        tempos = score.flatten().getElementsByClass('MetronomeMark')
        if tempos:
            return int(tempos[0].number)
        return 120

    @staticmethod
    def _get_key(score):
        """
        Analiza la tonalidad de una partitura MIDI.
        
        Intenta detectar la tonalidad automáticamente. Si falla,
        retorna Do Mayor como tonalidad por defecto.
        
        Args:
            score: Partitura music21 a procesar.
            
        Returns:
            Objeto Key de music21 representando la tonalidad.
        """
        try:
            return score.analyze('key')
        except:
            return key.Key('C')

    @staticmethod
    def _get_transposition_semitones(original_key) -> int:
        """
        Calcula los semitonos necesarios para transponer a Do Mayor o La Menor.
        
        Normaliza la tonalidad al rango Do Mayor (0) o La Menor (9) para
        estandarizar los valores MIDI entre archivos con diferentes tonalidades.
        
        Args:
            original_key: Tonalidad original de la partitura.
            
        Returns:
            Número de semitonos para transponer (positivo o negativo).
        """
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
    def _extraer_tuplas_eventos_static(score, bpm: int, transposition_semitones: int = 0) -> list[tuple[int, float]]:
        """
        Extrae eventos musicales de una partitura.
        
        Convierte notas, acordes y silencios de una partitura en tuplas
        (nota_midi, duracion_ms), aplicando transposición y cuantización
        de duraciones a una resolución de 50ms.
        
        Args:
            score: Partitura music21 a procesar.
            bpm: Tempo de la partitura en BPM.
            transposition_semitones: Semitonos a transponer (por defecto 0).
            
        Returns:
            Lista de tuplas (nota_midi, duracion_ms) donde nota_midi es el
            número MIDI (rango 0-127) o -1 para silencios, y duracion_ms
            está cuantizada en pasos de 50ms entre MIN_DURATION_MS y MAX_DURATION_MS.
        """
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
        """
        Convierte una secuencia de eventos en transiciones entre eventos consecutivos.
        
        Cada transición contiene la nota de origen, la nota de destino y la duración
        de la nota de destino, en el formato esperado por modelos de Markov.
        
        Args:
            eventos: Lista de tuplas (nota_midi, duracion_ms).
            
        Returns:
            Lista de tuplas (nota_origen, nota_destino, duracion_destino).
        """
        transiciones = []
        for i in range(len(eventos) - 1):
            nota_origen, _ = eventos[i]
            nota_destino, duracion_destino = eventos[i + 1]
            transiciones.append((nota_origen, nota_destino, duracion_destino))
        return transiciones