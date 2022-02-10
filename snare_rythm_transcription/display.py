import os
import IPython.display as ipd
from midi2audio import FluidSynth
from .exceptions import SoundFontNotFound

def show(music):
    png = music.write('lily.png')
    ipd.display(ipd.Image(str(png)))

def play(music, wavname='music.wav', sound_font='/usr/share/sounds/sf2/FluidR3_GM.sf2'):
    if not os.path.exists(sound_font):
        raise SoundFontNotFound(sound_font)

    midi_file = music.write('midi')
    fs = FluidSynth(sound_font=sound_font)
    fs.midi_to_audio(midi_file, wavname)
    ipd.display(ipd.Audio(wavname))
