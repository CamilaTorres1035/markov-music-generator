from music21 import converter, key, interval

def get_bpm(score):
    tempos = score.flatten().getElementsByClass('MetronomeMark')
    if tempos:
        return tempos[0].number
    return 120

def extract_cleaned_sequences(midi_file):
    # 1. Cargar el archivo
    print(f"Procesando: {midi_file}...")
    score = converter.parse(midi_file)
    
    # 2. Normalización Tonal (Transponer a Do Mayor o La Menor)
    # Esto asegura que todas las canciones "hablen el mismo idioma musical"
    original_key = score.analyze('key')
    
    # Si es mayor, la pasamos a Do Mayor (C). Si es menor, a La Menor (a).
    target_key = key.Key('C') if original_key.mode == 'major' else key.Key('a')
    
    # Calculamos la distancia (intervalo) y transponemos toda la partitura
    transposition_interval = interval.Interval(original_key.tonic, target_key.tonic)
    score = score.transpose(transposition_interval)
    
    # 3. Cuantización Rítmica
    # Ajusta las notas a una cuadrícula (negras, corcheas, semicorcheas)
    # Esto reduce la basura rítmica y consolida la "mochila" de tiempos.
    score = score.quantize([4, 8, 16]) 
    
    # 4. Extracción y Limpieza
    bpm = get_bpm(score)
    elementos = score.flatten().notesAndRests
    sequences = []
    
    for el in elementos:
        duration_ms = int(el.duration.quarterLength * (60000/bpm))
        
        # Filtro de Outliers: Ignorar notas súper cortas (<50ms) o súper largas (>4000ms)
        if duration_ms < 50 or duration_ms > 4000:
            continue
            
        # Extraemos la nota, resolviendo acordes y silencios
        if el.isNote:
            sequences.append((el.pitch.midi, duration_ms))
            
        elif el.isChord:
            # Tomar la melodía principal (nota más aguda del acorde)
            sequences.append((el[-1].pitch.midi, duration_ms))
            
        elif el.isRest:
            # -1 representa un silencio
            sequences.append((-1, duration_ms))
            
    return sequences

# --- Prueba del Pipeline ---
if __name__ == "__main__":
    try:
        # Reemplaza con un archivo de tu PC
        p = extract_cleaned_sequences('ViridianForest.mid') 
        print(f"Extracción exitosa. Total de secuencias: {len(p)}")
        print("Muestra de datos limpios (Primeros 10 eventos):")
        for midi, ms in p[:10]:
            estado = "Silencio" if midi == -1 else f"Nota {midi}"
            print(f"  {estado} -> Duración: {ms}ms")
    except Exception as e:
        print("Asegúrate de tener un archivo MIDI válido en la carpeta.")