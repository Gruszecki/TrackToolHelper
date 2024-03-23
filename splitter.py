import librosa
import numpy as np
import time

import pyautogui
import pyperclip
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


BUTTON_BROWSE_SELECTOR = (By.XPATH, '//button[@class="upload"]')
BUTTON_SAVE_SELECTOR = (By.XPATH, '//button[@class="white"]')
DOWNLOAD_VOCAL_SELECTOR = (By.XPATH, '//button[span[text()="Vocal"]]')


class WebWalker:
    def __init__(self):
        self._driver = webdriver.Firefox()
        self.not_found = list()
        self.found_many = list()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._driver.close()

    def open_site(self):
        self._driver.get('https://vocalremover.org/')

    def upload_file(self, audio_path):
        WebDriverWait(self._driver, 5).until(EC.element_to_be_clickable(BUTTON_BROWSE_SELECTOR)).click()
        pyperclip.copy(audio_path)
        time.sleep(2)
        pyautogui.hotkey('ctrl', 'v')
        pyautogui.hotkey('enter')
        time.sleep(30)

    def save_vocals(self):
        WebDriverWait(self._driver, 300).until(EC.element_to_be_clickable(BUTTON_SAVE_SELECTOR)).click()
        self._driver.find_element(*DOWNLOAD_VOCAL_SELECTOR).click()


def _get_vocals(audio_path):
    ww = WebWalker()
    ww.open_site()
    ww.upload_file(audio_path)
    ww.save_vocals()

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


def get_vocals_appearance_time(audio_path):
    _get_vocals(audio_path)
