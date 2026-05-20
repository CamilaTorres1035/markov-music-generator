"""
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

    lista_eventos_prueba2 = [
        EventoMusical(NotaMusical(60), 0.5),
        EventoMusical(NotaMusical(62), 0.5),
        EventoMusical(NotaMusical(64), 1.0),
        EventoMusical(NotaMusical(65), 0.25),
        EventoMusical(NotaMusical(67), 2.0)
    ]

    # 3. Empaquetando en la Secuencia (opcional, por si el mapper lo exige así)
    secuencia_prueba = SecuenciaMusical(lista_eventos_prueba)
    secuencia_prueba2 = SecuenciaMusical(lista_eventos_prueba2)

    corpus = [secuencia_prueba, secuencia_prueba2]

    orquestador = OrquestadorMapReduce(corpus=corpus)
    lista = orquestador.ejecutar_map_reduce(MarkovMapper.map_secuencia, MarkovReducer.funcion_reduce, MarkovReducer.funcion_combine)
    cerrar = input("E")
    if cerrar == "ESCRIBA E PARA CERRAR CLUSTER":
        orquestador.cerrar() 
    print(lista)



if __name__ == "__main__":
    main()

"""
import random

from model.NotaMusical import NotaMusical
from model.EventoMusical import EventoMusical
from model.SecuenciaMusical import SecuenciaMusical

from services.MarkovMapper import MarkovMapper
from services.MarkovReducer import MarkovReducer
from services.OrquestadorMapReduce import OrquestadorMapReduce


def generar_secuencia_aleatoria(
    longitud: int,
    rango_notas: tuple[int, int],
    duraciones_posibles: list[float]
) -> SecuenciaMusical:

    eventos = []

    for _ in range(longitud):

        nota_midi = random.randint(
            rango_notas[0],
            rango_notas[1]
        )

        duracion = random.choice(
            duraciones_posibles
        )

        nota = NotaMusical(nota_midi)

        evento = EventoMusical(
            nota,
            duracion
        )

        eventos.append(evento)

    return SecuenciaMusical(eventos)


def generar_corpus_aleatorio(
    cantidad_secuencias: int,
    longitud_minima: int,
    longitud_maxima: int
) -> list[SecuenciaMusical]:

    corpus = []

    for _ in range(cantidad_secuencias):

        longitud = random.randint(
            longitud_minima,
            longitud_maxima
        )

        secuencia = generar_secuencia_aleatoria(
            longitud=longitud,
            rango_notas=(60, 72),
            duraciones_posibles=[
                0.25,
                0.5,
                1.0,
                2.0
            ]
        )

        corpus.append(secuencia)

    return corpus


def main():

    random.seed(42)

    corpus = generar_corpus_aleatorio(
        cantidad_secuencias=20,
        longitud_minima=8,
        longitud_maxima=20
    )

    print("Corpus generado:")
    print(f"Cantidad de secuencias: {len(corpus)}")
    print()

    orquestador = OrquestadorMapReduce(
        corpus=corpus
    )

    resultado = orquestador.ejecutar_map_reduce(
        MarkovMapper.map_secuencia,
        MarkovReducer.funcion_reduce,
        MarkovReducer.funcion_combine
    )
    input("A")
    orquestador.cerrar()

    print("Resultado del MapReduce:")
    print()

    for data in resultado:

        print(f"Nota origen: {data._nota_origen}")

        for nota_destino, estadisticas in data._transiciones.items():

            print(
                f"  -> {nota_destino} | "
                f"conteo={estadisticas._conteo} | "
                f"tiempos={estadisticas._tiempos}"
            )

        print()


if __name__ == "__main__":
    main()