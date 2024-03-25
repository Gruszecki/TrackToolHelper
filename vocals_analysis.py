import librosa
import numpy as np
from PySide6.QtCore import QObject, QThread, Signal

import general
import tag_walker


vocal_time_database = list()


class Worker(QThread):
    update_voc = Signal(dict)

    def __init__(self, vocals_path, threshold):
        super().__init__()
        self.vocals_path = vocals_path
        self.threshold = threshold
        self.is_running = True

    def run(self):
        vocals = general.get_audio_files(general.resource_path(self.vocals_path))

        for audio_file in vocals:
            if not self.is_running:
                break

            band_name = tag_walker.get_band_name(audio_file)
            song_title = tag_walker.get_song_title((audio_file))

            if not (band_name and song_title):
                with open('is_it_instrumental.txt', 'a+', encoding='utf-8') as f:
                    f.write(f'Nie udało się pobrać zespołu ({band_name}) lub/i tytułu ({song_title}) dla {audio_file}\n\n')
                continue

            print(f'{band_name} - {song_title}')

            start, end = _calculate_vocal(audio_file, self.threshold)

            if start is not None and end is not None:
                vocal_time_database.append({'band': band_name, 'title': song_title, 'start': start, 'end': end})
                self.update_voc.emit({'band': band_name, 'title': song_title, 'start': start, 'end': end})

    def stop(self):
        self.is_running = False
        print('Przetwarzanie wokaliz zostanie zatrzymane')


def _calculate_vocal(audio_file, threshold):
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
        first_loud_second = round(first_loud_frame * hop_length / sr, 2)
        last_loud_second = last_loud_frame * hop_length / sr
        total_length_sec = len(y) / sr
        last_loud_second_from_end = round(total_length_sec - last_loud_second, 2)

        print(f'Pierwsza głośna sekunda: {first_loud_second}, Ostatnia głośna sekunda od końca: {last_loud_second_from_end}')

        if last_loud_second - first_loud_second < 3:
            print('Czy to instrumental?')
            with open('is_it_instrumental.txt', 'a+', encoding='utf-8') as f:
                f.write(f'{audio_file}\n'
                        f'Pierwsza głośna sekunda: {first_loud_second}, Ostatnia głośna sekunda od końca: {last_loud_second_from_end}\n'
                        f'Czas pomiędzy pierwszą i ostatnią głośną sekundą: {round(last_loud_second - first_loud_second, 2)}\n\n')

                return 0, 0

        return first_loud_second, last_loud_second_from_end
    else:
        print('Nie znaleziono żadnych głośnych ramek.')
        return None, None
