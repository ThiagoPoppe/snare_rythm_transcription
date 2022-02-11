import sys
from distutils.core import setup

if __name__ == "__main__":
    if sys.version_info[:2] < (3, 6):
        print('Requires Python version 3.6 or later')
        sys.exit(-1)

    setup(
        name='snare_rythm_transcription',
        packages=['snare_rythm_transcription'],
        install_requires=[line.strip() for line in open('requirements.txt')],
        version='0.01',
        description='Dependências para executar o projeto Snare Rythm Transcription da disciplina MIR do DCC/UFMG',
        author='Thiago Martin Poppe'
    )