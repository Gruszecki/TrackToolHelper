import librosa
import numpy as np

def _split(audio_file, threshold=0.7):
    y, sr = librosa.load(audio_file)
    D = librosa.stft(y)
    magnitude, phase = librosa.magphase(D)
    S_filter = librosa.decompose.nn_filter(magnitude)
    y_recover = librosa.istft(S_filter * phase)
    loudness = librosa.feature.rms(y=y_recover)
    normalized_loudness = (loudness - np.min(loudness)) / (np.max(loudness) - np.min(loudness))
    normalized_loudness = normalized_loudness[0]
    loud_frames = np.where(normalized_loudness > threshold)[0]

    if len(loud_frames) > 0:
        first_loud_frame = loud_frames[0]
        last_loud_frame = loud_frames[-1]

        hop_length = 512
        first_loud_second = first_loud_frame * hop_length / sr
        last_loud_second = last_loud_frame * hop_length / sr
        total_length_sec = len(y) / sr
        last_loud_second_from_end = total_length_sec - last_loud_second

        print(f'Pierwsza głośna sekunda: {first_loud_second}, Ostatnia głośna sekunda od końca: {last_loud_second_from_end}')
    else:
        print('Nie znaleziono żadnych głośnych ramek.')
