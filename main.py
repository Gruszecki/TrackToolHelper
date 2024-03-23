import os
from pathlib import Path

from splitter import get_vocals_appearance_time
from tag_walker import get_band_name, get_song_title


def get_audio_files(directory, extensions=['.wav', '.mp3']):
    audio_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if any(file.endswith(ext) for ext in extensions):
                audio_files.append(os.path.join(root, file))
    return audio_files


if __name__ == '__main__':
    audio_path = r'C:\Users\wojte\Desktop\Muzyka Nowinki'
    downloads_path = str(Path.home() / 'Downloads')

    audio_files = get_audio_files(audio_path)
    already_extracted = [[get_band_name(path), get_song_title(path)] for path in get_audio_files(downloads_path)]

    for audio_file in audio_files:
        metadata = [get_band_name(audio_file), get_song_title(audio_file)]

        print(audio_file)
        if metadata not in already_extracted:
            try:
                get_vocals_appearance_time(audio_file)
                print('Done')
            except Exception as e:
                print(e)
        else:
            print(f'Vocals already extracted in {downloads_path}')