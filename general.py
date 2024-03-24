import os


def get_audio_files(directory, extensions=['.wav', '.mp3']):
    audio_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if any(file.endswith(ext) for ext in extensions):
                audio_files.append(os.path.join(root, file))
    return audio_files