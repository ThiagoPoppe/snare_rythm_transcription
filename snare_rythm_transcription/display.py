import os
import copy
import IPython.display as ipd
from midi2audio import FluidSynth
from .exceptions import SoundFontNotFound

def show(music):
    """
        Método para exibir a partitura da música.

        Infelizmente o music21 ainda não suporta muitas features de instrumentos percussivos.
        Para isso, iremos modificar a nota apenas para a sua exibição correta.
        Por exemplo, um toque na caixa está na posição da nota B4 na partitura.
    """
    music_cp = copy.deepcopy(music)
    for note in music_cp.recurse().notes:
        note.name = 'B4' # toques na caixa correspondem à posição do B4
        note.stemDirection = 'up'

    music_cp.show()

def play(music, wavname='music.wav', sound_font='pns_drum_kit.SF2'):
    """
        Método para tocarmos a música.
        Como estamos trabalhando exclusivamente com percussão, utilizaremos
        por padrão um SoundFont de bateria.
    """
    if not os.path.exists(sound_font):
        raise SoundFontNotFound(sound_font)

    midi_file = music.write('midi')
    fs = FluidSynth(sound_font=sound_font)
    fs.midi_to_audio(midi_file, wavname)
    ipd.display(ipd.Audio(wavname))
