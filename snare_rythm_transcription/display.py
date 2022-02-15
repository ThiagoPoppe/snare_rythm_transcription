import os
import copy
import librosa
import IPython.display as ipd
from midi2audio import FluidSynth
from .exceptions import SoundFontNotFound

def show(stream):
    """
        Método para exibir a partitura da música.

        Infelizmente o music21 ainda não suporta muitas features de instrumentos percussivos.
        Para isso, iremos modificar a nota apenas para a sua exibição correta.
        Por exemplo, um toque na caixa está na posição da nota B4 na partitura.

        Argumentos:
            - stream (Stream): música a ser exibida

        Retorno:
            - None

        Observações:
            - Infelizmente o music21 ainda não suporta muitas features de instrumentos percussivos.
              Para isso, iremos modificar a nota apenas para a sua exibição correta.
              Por exemplo, um toque na caixa está na posição da nota B4 na partitura.
    """
    stream_cp = copy.deepcopy(stream)
    for note in stream_cp.recurse().notes:
        note.name = 'B4' # toques na caixa correspondem à posição do B4
        note.stemDirection = 'up'

    stream_cp.show()

def play(stream, wavname='music.wav', sound_font='pns_drum_kit.SF2'):
    """
        Método para tocarmos a música.

        Argumentos:
            - stream (Stream): música a ser exibida
            - wavname: nome do .wav a ser gerado (default = 'music.wav')
            - sound_font: sound font a ser utilizado (default = 'pns_drum_kit.SF2')

        Retorno:
            - None

        Observações:
            - Como estamos trabalhando exclusivamente com percussão, utilizaremos
              por padrão um SoundFont de bateria.
    """
    if not os.path.exists(sound_font):
        raise SoundFontNotFound(sound_font)

    midi_file = stream.write('midi')
    fs = FluidSynth(sound_font=sound_font)
    fs.midi_to_audio(midi_file, wavname)

    wave, sr = librosa.load(wavname, sr=None)
    ipd.display(ipd.Audio(wave, rate=sr))