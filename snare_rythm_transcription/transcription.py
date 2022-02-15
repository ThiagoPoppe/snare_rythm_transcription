import librosa
import numpy as np
from music21.note import Rest
from .stream import snare_hit, create_percussive_stream

def estimate_tempo(wave, sr, **kwargs):
    """
        Método para estimar o tempo (BPM) da música utilizando a função
        beat.tempo da biblioteca librosa.
    
        Argumentos:
            - wave (np.array): música na representação vetorial
            - sr (int): taxa de amostragem da música
            - kwargs: outros argumentos para a função librosa.beat.tempo

        Retorno:
            - O valor inteiro do BPM (batidas por minuto).
    """
    tempo = librosa.beat.tempo(wave, sr, **kwargs)
    return int(np.round(tempo))

def estimate_snare_hit_times(wave, sr):
    """
        Método para estimar as batidas da caixa utilizando a função onset.onset_detect
        da biblioteca librosa.

        Argumentos:
            - wave (np.array): música na representação vetorial
            - sr (int): taxa de amostragem da música

        Retorno:
            - Tempos, em segundos, em que ocorrem batidas na caixa.
    """

    # Criando uma modificação da música com 1 segundo de silêncio no começo
    wave_mod = np.zeros(len(wave) + sr)
    wave_mod[sr:] = wave

    # Estimando as batidas da música (agora devemos subtrair 1 segundo do vetor)
    snare_times = librosa.onset.onset_detect(wave_mod, sr, units='time') - 1.0
    # return np.round(snare_times, decimals=2)
    return snare_times

def create_metronome(tempo=60, duration=60, reference_note=4):
    """
        Método para criarmos um metrônomo seguindo um BPM fornecido.

        Argumentos:
            - tempo (int): batimentos por minuto do metrônomo
            - duration (int): duração em segundos do metrônomo
            - reference_note (int): nota de referência (denominador) da figura de tempo.

        Retorno:
            - Um np.array indicando as batidas do metrônomo em segundos.
    """

    # Verificando se a nota de referência é uma potência de 2
    log = np.log2(reference_note)
    if np.floor(log) != np.ceil(log):
        raise ValueError('the reference note must be a power of 2')

    # Definindo o tempo de passo de uma batida para a próxima
    # Basta dividirmos 60 segundos por bpm e subdividir isso de acordo com a nota de referência
    step = (60 / tempo) / (reference_note / 4)
    return np.arange(0, duration, step)

def extract_measures(snare_times, metronome, notes_per_measure):
    """
        Método para extrair as notas de cada compasso.

        Argumentos:
            - snare_times (np.array): os tempos, em segundos, em que ocorrem batidas na caixa
            - metronome (np.array): os tempos, em segundos, em que ocorrem as batidas do metrônomo
            - notes_per_measure (int): numerador da fórmula de compasso, indicando quantas notas há em cada compasso
    
        Retorno:
            - Uma lista representando os compassos da música. Cada posição terá uma outra lista com os tempos em que
              ocorrem as batidas da caixa dentro daquele compasso.
    """

    measures = []
    for i in range(0, len(metronome), notes_per_measure):
        min_t = metronome[i]
        max_t = metronome[i + notes_per_measure]

        # Verificando se já chegamos no final da música
        if min_t > snare_times[-1]:
            break

        # Filtrando os tempos da caixa que estão dentro dos limites do compasso
        mask = (snare_times >= min_t) & (snare_times < max_t)
        measures.append(snare_times[mask])

    return measures

def find_best_time_figure(dt, reference_note, reference_note_duration):
    """
        Método auxiliar para determinar a melhor figura de tempo de uma nota.

        Argumentos:
            - dt (float): diferença de tempo entre as notas.
            - reference_note (int): nota de referência da fórmula de compasso (denominador)
            - reference_note_duration (float): duração, em segundos, da nota de referência
    
        Retorno:
            - A figura de tempo da nota no formato fracionário utilizando a semínima como referência.
              Por exemplo: a semínima terá valor 1 enquanto que uma colcheia terá valor 1/2.
    """

    figure = None
    best_match = np.inf
    
    # Para cada subdivisão iremos verificar qual possui o tempo mais próximo
    for subdiv in [4, 2, 1, 1/2, 1/4]:
        # Verificando com a subdivisão original
        dur = subdiv * reference_note_duration
        if np.abs(dt - dur) < best_match:
            best_match = np.abs(dt - dur)
            figure = subdiv / (reference_note / 4) # precisamos corrigir a subdivisão baseado na figura de tempo

        # Verificando com a subdivisão em tercina (só faz "sentido" em subdivisão binária)
        if reference_note == 4:
            triplet = subdiv / 3
            dur = triplet * reference_note_duration
            if np.abs(dt - dur) < best_match:
                best_match = np.abs(dt - dur)
                figure = triplet

        # Verificando com a subdivisão com ponto (+ 1/2 do tempo)
        dotted = subdiv + (0.5 * subdiv)
        dur = dotted * reference_note_duration
        if np.abs(dt - dur) < best_match:
            best_match = np.abs(dt - dur)
            figure = dotted / (reference_note / 4) # precisamos corrigir a subdivisão baseado na figura de tempo

    return figure

def transcribe(snare_times, metronome, time_signature='4/4'):
    """
        Método para transcrever o ritmo da caixa da bateria.

        Argumentos:
            - snare_times (np.array): os tempos, em segundos, em que ocorrem batidas na caixa
            - metronome (np.array): os tempos, em segundos, em que ocorrem as batidas do metrônomo
            - time_signature (str): fórmula de compasso da música, por exemplo "4/4".

        Retorno:
            - Lista com "notas" (tanto notas como pausas) do music21. Note que a figura de tempo de cada "nota"
              estará no formato fracionário utilizando a semínima como referência. Por exemplo: a semínima terá
              valor 1 enquanto que uma colcheia terá valor 1/2.
    """

    reference_note_duration = metronome[1] - metronome[0]
    notes_per_measure, reference_note = tuple(map(int, time_signature.split('/')))

    # Computando o limite de notas de referência por compasso
    acc_time_figure = 0.0
    measure_time_figure_limit = notes_per_measure * (4 / reference_note)

    notes = []
    for i, dt in enumerate(np.diff(snare_times)):
        figure = find_best_time_figure(dt, reference_note, reference_note_duration)

        # Verificando se a figura de tempo ultrapassa o limite do compasso
        # Se sim, iremos criar uma nota com o tempo igual ao tempo restante do compasso e pausas
        # para preencher o restante do tempo
        total = np.round(acc_time_figure + figure, decimals=2)
        # total = acc_time_figure + figure
        if total > measure_time_figure_limit:
            note_figure = measure_time_figure_limit - acc_time_figure
            rest_figure = figure - note_figure

            notes.append(snare_hit(time_figure=note_figure))
            notes.append(Rest(quarterLength=rest_figure))
            acc_time_figure = rest_figure # o próximo compasso já foi preenchido pela figura da pausa

        # Senão, podemos apenas inserir uma nota com essa figura de tempo
        else:
            notes.append(snare_hit(time_figure=figure))
            acc_time_figure += figure
            if np.isclose(acc_time_figure, measure_time_figure_limit, rtol=1e-4):
                acc_time_figure = 0.0

    # Devido ao uso do np.diff, não conseguimos encontrar a figura de tempo da última nota com o loop de cima.
    # Mas é simples, a última nota terá como figura de tempo o tempo restante do compasso
    note_figure = measure_time_figure_limit - acc_time_figure
    notes.append(snare_hit(time_figure=note_figure))

    return notes

def transcription_pipeline(wavname, sr=None, tempo=None, time_signature='4/4'):
    """
        Método para transcrever o ritmo da caixa da bateria de um áudio.

        Argumentos:
            - wavname (str): caminho para o arquivo .wav
            - sr (int): taxa de amostragem da música (None -> irá utilizar a taxa original)
            - tempo (int): batidas por minuto da música (None -> irá estimar esse valor)
            - time_signature (str): fórmula de compasso da música, por exemplo "4/4"

        Retorno:
            - Uma Stream do music21 representando a partitura da música transcrita.
    """

    wave, sr = librosa.load(wavname, sr=sr)
    if tempo is None:
        tempo = estimate_tempo(wave, sr, aggregate=np.median)
    
    snare_times = estimate_snare_hit_times(wave, sr)
    notes_per_measure, reference_note = tuple(map(int, time_signature.split('/')))
    metronome = create_metronome(tempo=tempo, reference_note=reference_note)

    stream = create_percussive_stream(tempo, time_signature)
    for note in transcribe(snare_times, metronome, time_signature):
        stream.append(note)

    return stream