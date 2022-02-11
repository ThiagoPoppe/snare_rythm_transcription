import os
import copy
import IPython.display as ipd
from midi2audio import FluidSynth
from .exceptions import SoundFontNotFound

def show(music):
    music_cp = copy.deepcopy(music)
    for note in music_cp.recurse().notes:
        note.name = 'B4' # toques na caixa correspondem à posição do B4
    music_cp.show()

def play(music, wavname='music.wav', sound_font='pns_drum_kit.SF2'):
    if not os.path.exists(sound_font):
        raise SoundFontNotFound(sound_font)

    midi_file = music.write('midi')
    fs = FluidSynth(sound_font=sound_font)
    fs.midi_to_audio(midi_file, wavname)
    ipd.display(ipd.Audio(wavname))
