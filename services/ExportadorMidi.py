"""
ExportadorMidi: Responsable de exportar SecuenciaMusical de vuelta a archivos MIDI.

Reconstruye una partitura music21 a partir de eventos y la guarda en formato MIDI.
"""

from pathlib import Path
import random
from music21 import stream, note, tempo, meter
from model.SecuenciaMusical import SecuenciaMusical


class ExportadorMidi:
    """
    Exporta SecuenciaMusical a archivos MIDI.
    
    Responsabilidades:
    - Convertir SecuenciaMusical a music21 Score
    - Guardar archivo MIDI
    - Validar rutas y manejo de errores
    """
    
    # Tempo y métrica por defecto
    TEMPO_DEFECTO = 120  # BPM
    FIRMA_DEFECTO = (4, 4)  # 4/4
    
    def exportar_secuencia(
        self,
        secuencia: SecuenciaMusical,
        ruta_archivo: str,
        nombre_archivo: str
    ) -> Path:
        """
        Exporta una SecuenciaMusical a un archivo MIDI.
        
        Args:
            secuencia: SecuenciaMusical a exportar
            ruta_archivo: ruta del directorio donde guardar
            nombre_archivo: nombre del archivo (sin extensión .mid)
            
        Returns:
            Path: ruta completa del archivo creado
            
        Raises:
            ValueError: si la secuencia está vacía
            OSError: si hay error al crear el archivo
        """
        
        # Validar entrada
        if not secuencia._lista_eventos:
            raise ValueError("No se puede exportar una secuencia vacía")
        
        # Validar y crear directorio
        path_dir = Path(ruta_archivo)
        try:
            path_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            raise OSError(f"Error al crear directorio {ruta_archivo}: {str(e)}")
        
        # Construir ruta completa
        nombre_base = nombre_archivo.replace('.mid', '')  # Remover .mid si lo tiene
        ruta_completa = path_dir / f"{nombre_base}.mid"
        
        # Crear partitura
        try:
            score = self._construir_partitura(secuencia)
            
            # Guardar archivo
            score.write('midi', fp=str(ruta_completa))
            
            print(f"✓ Archivo MIDI exportado: {ruta_completa}")
            return ruta_completa
            
        except Exception as e:
            raise OSError(f"Error al exportar MIDI: {str(e)}")
    
    @staticmethod
    def _construir_partitura(secuencia: SecuenciaMusical) -> stream.Score:
        """
        Construye una partitura music21 a partir de una SecuenciaMusical.
        
        Args:
            secuencia: SecuenciaMusical a convertir
            
        Returns:
            stream.Score: partitura music21 lista para exportar
        """
        
        # Crear partitura
        score = stream.Score()
        part = stream.Part()
        
        # Agregar tempo
        part.append(tempo.MetronomeMark(number=ExportadorMidi.TEMPO_DEFECTO))
        
        # Agregar firma de compás
        parte_numerador, parte_denominador = ExportadorMidi.FIRMA_DEFECTO
        part.append(meter.TimeSignature(f'{parte_numerador}/{parte_denominador}'))
        
        # POST-PROCESADO: Fusión de notas y filtro de ruido <---
        eventos_limpios = []
        for evento in secuencia._lista_eventos:
            if evento._duracion < 50: 
                continue # Eliminar ruido/notas fantasma
                
            # Si es la misma nota que la anterior, sumamos duración en vez de re-tocarla
            if eventos_limpios and eventos_limpios[-1]._nota._nota_midi == evento._nota._nota_midi:
                eventos_limpios[-1]._duracion += evento._duracion
            else:
                eventos_limpios.append(evento)

        tiempo_acumulado_ms = 0
        # Agregar eventos
        for evento in eventos_limpios:
            nota_midi = evento._nota._nota_midi
            duracion_ms = evento._duracion
            
            # VELOCITY (Acentos en los beats fuertes) <---
            beat_actual = int(tiempo_acumulado_ms / 500) % 4 # Asumiendo 1 beat = 500ms
            if beat_actual == 0:
                evento._velocidad = 90 # Fuerte en el beat 1
            else:
                evento._velocidad = 50 + random.randint(-10, 10) # Humanizado en débiles
            
            # HUMANIZACIÓN (Imperfección rítmica) <---
            # Mutamos ligeramente la duración real escrita en el MIDI
            duracion_humana = duracion_ms * random.uniform(0.9, 1.1)
            quarter_length = duracion_humana/ 500.0

            if nota_midi == -1:
                # Silencio
                rest = note.Rest(quarterLength=quarter_length)
                part.append(rest)
            else:
                # Nota válida
                try:
                    n = note.Note(nota_midi, quarterLength=quarter_length)
                    n.volume.velocity = evento._velocidad
                    part.append(n)
                except:
                    # Si hay error, crear silencio
                    rest = note.Rest(quarterLength=quarter_length)
                    part.append(rest)
            tiempo_acumulado_ms += duracion_ms

        # Agregar part a score
        score.append(part)
        
        return score
