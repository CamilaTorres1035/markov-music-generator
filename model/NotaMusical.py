from dataclasses import dataclass
"""
Módulo que define la clase NotaMusical, representando una nota
del estándar MIDI mediante su valor numérico.
"""

@dataclass
class NotaMusical:
    """
    Representa una nota musical mediante su valor en el estándar MIDI.

    El estándar MIDI codifica las notas como enteros en el rango [0, 127],
    donde 60 corresponde al Do central (C4) y cada unidad equivale a un semitono.
    Si la nota es -1, representa un silencio.

    Attributes:
        _nota_midi (int): Valor MIDI de la nota, en el rango [0, 127] o -1 para silencio.
    """
    _nota_midi: int