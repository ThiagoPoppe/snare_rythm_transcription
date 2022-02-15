from music21.note import Note
from music21.stream import Stream
from music21.clef import PercussionClef
from music21.tempo import MetronomeMark
from music21.meter import TimeSignature

def snare_hit(midi=38, time_figure=1.0):
    """
        Método auxiliar para criarmos um toque na caixa.

        Argumentos:
            - midi (int): valor em MIDI da "nota" (default = 38)
            - time_figure (float): figura de tempo da nota, utilizando a semínima como referência (default = 1.0)

        Retorno:
            - Esse método retorna um Note do music21 representando um toque na caixa.
    """
    return Note(midi, quarterLength=time_figure)

def create_percussive_stream(tempo=60, time_signature='4/4'):
    """
        Método auxiliar para criarmos um stream percussivo.

        Argumentos:
            - tempo (int): BPM da música (default = 60)
            - time_signature (str): fórmula de compasso da música (default = '4/4')

        Retorno:
            - Um Stream com o BPM e TimeSignature informados.
    """
    stream = Stream()
    stream.insert(0, PercussionClef())
    stream.insert(0, MetronomeMark(number=tempo))
    stream.insert(0, TimeSignature(time_signature))

    return stream