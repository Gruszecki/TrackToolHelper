import time

import pyautogui
import pyperclip
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from general import get_audio_files
from tag_walker import get_band_name, get_song_title


BUTTON_BROWSE_SELECTOR = (By.XPATH, '//button[@class="upload"]')
BUTTON_SAVE_SELECTOR = (By.XPATH, '//button[@class="white"]')
DOWNLOAD_VOCAL_SELECTOR = (By.XPATH, '//button[span[text()="Vocal"]]')


class WebWalker:
    def __init__(self, browser):
        match browser:
            case 'firefox':
                self._driver = webdriver.Firefox()
            case 'chrome':
                self._driver = webdriver.Chrome()
            case 'edge':
                self._driver = webdriver.Edge()
            case _:
                self._driver = webdriver.Firefox()

        self.not_found = list()
        self.found_many = list()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._driver.close()

    def open_site(self):
        self._driver.get('https://vocalremover.org/?patreon')

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


def _get_vocals(audio_path, browser='firefox'):
    ww = WebWalker(browser)
    ww.open_site()
    ww.upload_file(audio_path)
    ww.save_vocals()


def run_loop(audio_path='', output_path='', browser='firefox'):
    audio_files = get_audio_files(audio_path)
    already_extracted = [[get_band_name(path), get_song_title(path)] for path in get_audio_files(output_path)]

    for audio_file in audio_files:
        metadata = [get_band_name(audio_file), get_song_title(audio_file)]

        print(audio_file)
        if metadata not in already_extracted:
            try:
                _get_vocals(audio_file, browser)
                print('Done')
            except Exception as e:
                print(e)
        else:
            print(f'Vocals already extracted in {output_path}')
