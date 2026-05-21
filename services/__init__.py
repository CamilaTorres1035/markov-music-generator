"""
Services: Capa de servicios/adaptadores para I/O y procesamiento externo.

Proporciona interfaces entre el modelo de dominio y recursos externos
(archivos MIDI, bases de datos, APIs, etc.).
"""

from .ConstructorCorpusMidi import ConstructorCorpusMidi
from .ExportadorMidi import ExportadorMidi

__all__ = ["ConstructorCorpusMidi", "ExportadorMidi"]
