from model.TransicionMarkov import TransicionMarkov

class MatrizMarkov:
    _matriz: dict[int, list[TransicionMarkov]]
    _estados: set[int]

    def __init__(self, matriz: dict[int, list[TransicionMarkov]], estados:set[int]):
        self._matriz = matriz
        self._estados = estados

    def obtener_transiciones(self, estado:int) -> list[TransicionMarkov]:
        return self._matriz.get(estado)
    
    def existe_estado(self, estado:int) -> bool:
        return estado in self._estados
        