import json

import librosa
import numpy as np
from PySide6.QtCore import QThread, Signal

import general
import tag_walker
from radioboss_db import is_in_db


vocal_time_database = list()    # List of dicts. Keys: band, title, start, end


class Worker(QThread):
    update_voc = Signal(dict)

    def __init__(self, vocals_path, threshold, look_in_db, look_in_results, db_path):
        super().__init__()
        self.vocals_path = vocals_path
        self.threshold = threshold
        self.is_running = True
        self.look_in_db = look_in_db
        self.look_in_results = look_in_results
        self.db_path = db_path

    def run(self):
        vocals = general.get_audio_files(general.resource_path(self.vocals_path))

        for audio_file in vocals:
            if not self.is_running:
                break

            print(audio_file)

            band_name = tag_walker.get_band_name(audio_file)
            song_title = tag_walker.get_song_title((audio_file))

            if self.look_in_results and _is_in_results(band_name, song_title):
                print(f'{band_name} - {song_title} jest już w rezultatach')
                continue

            if self.look_in_db and is_in_db(band_name, song_title):
                print(f'{band_name} - {song_title} jest już w bazie')
                continue

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
        print('Analiza wokali zostanie zatrzymane')


def _is_in_results(band_name, song_title):
    for result in vocal_time_database:
        if result['band'] == band_name and result['title'] == song_title:
            return True
    return False


def _calculate_vocal(audio_file, threshold):
    print('Loading audio file')
    y, sr = librosa.load(audio_file)
    D = librosa.stft(y)
    magnitude, phase = librosa.magphase(D)
    S_filter = librosa.decompose.nn_filter(magnitude)
    y_recover = librosa.istft(S_filter * phase)
    loudness = librosa.feature.rms(y=y_recover)
    print('Normalizing loudness')
    normalized_loudness = (loudness - np.min(loudness)) / (np.max(loudness) - np.min(loudness))
    normalized_loudness = normalized_loudness[0]
    print('Extracting loud frames according to the threshold')
    loud_frames = np.where(normalized_loudness > threshold)[0]

    if len(loud_frames) > 0:
        print('Loud frames present. Calculating the first and the last timestamp.')
        first_loud_frame = loud_frames[0]
        last_loud_frame = loud_frames[-1]

        hop_length = 512
        first_loud_ms = round((first_loud_frame * hop_length / sr) * 1000)
        last_loud_ms = (last_loud_frame * hop_length / sr) * 1000
        total_length_ms = (len(y) / sr) * 1000
        last_loud_ms_from_end = round(total_length_ms - last_loud_ms)

        print(f'Pierwsza głośna milisekunda: {first_loud_ms}, Ostatnia głośna milisekunda od końca: {last_loud_ms_from_end}')

        if last_loud_ms - first_loud_ms < 3000:
            print('Czy to instrumental?')
            with open('is_it_instrumental.txt', 'a+', encoding='utf-8') as f:
                f.write(f'{audio_file}\n'
                        f'Pierwsza głośna milisekunda: {first_loud_ms}, Ostatnia głośna milisekunda od końca: {last_loud_ms_from_end}\n'
                        f'Czas pomiędzy pierwszą i ostatnią głośną milisekundą: {round(last_loud_ms - first_loud_ms)}\n\n')

                return 0, 0

        return first_loud_ms, last_loud_ms_from_end
    else:
        print('Nie znaleziono żadnych głośnych ramek.')
        return None, None


def save_data(data_path):
    with open(data_path, 'w+', encoding='utf-8') as f:
        json.dump(vocal_time_database, f, ensure_ascii=False, indent=4)


def load_data(data_path):
    with open(data_path, 'r', encoding="utf8") as f:
        for record in json.load(f):
            vocal_time_database.append(record)


def get_data_from_json(data_path):
    with open(data_path, 'r', encoding="utf8") as f:
        return json.load(f)
