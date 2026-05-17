# main.py
from model.EventoMusical import EventoMusical
from model.NotaMusical import NotaMusical
from model.SecuenciaMusical import SecuenciaMusical
from model.TransicionMarkov import TransicionMarkov
from model.MatrizMarkov import MatrizMarkov
from services.MarkovMapper import MarkovMapper
from services.MarkovReducer import MarkovReducer
from services.OrquestadorMapReduce import OrquestadorMapReduce

def main():
    # 2. Creación de los datos de prueba (Mocking)
    # Notas MIDI: 60 (Do), 62 (Re), 64 (Mi), 65 (Fa), 67 (Sol)
    lista_eventos_prueba = [
        EventoMusical(NotaMusical(60), 0.5),
        EventoMusical(NotaMusical(62), 0.5),
        EventoMusical(NotaMusical(64), 1.0),
        EventoMusical(NotaMusical(65), 0.25),
        EventoMusical(NotaMusical(67), 2.0)
    ]

    # 3. Empaquetando en la Secuencia (opcional, por si el mapper lo exige así)
    secuencia_prueba = SecuenciaMusical(lista_eventos_prueba)

    # --- Impresión para verificar la estructura ---
    print("Lista directa para procesar:")
    for evento in lista_eventos_prueba:
        print(evento)

    transformada = MarkovMapper.map_secuencia(secuencia_prueba)
    print("TRANSFORMACIÓN PARA FASE MAP")
    print(transformada)


if __name__ == "__main__":
    main()