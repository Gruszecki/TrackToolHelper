import os.path
import time
from pathlib import Path

import pyautogui
import pyperclip
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

import general
import vocals_analysis
from tag_walker import get_band_name, get_song_title
from radioboss_db import is_in_db


BUTTON_BROWSE_SELECTOR = (By.XPATH, '//button[@class="upload"]')
BUTTON_SAVE_SELECTOR = (By.XPATH, '//button[@class="white"]')
DOWNLOAD_VOCAL_SELECTOR = (By.XPATH, '//button[span[text()="Vocal"]]')


class WebWalker:
    def __init__(self, browser):
        match browser:
            case 'Firefox':
                self._driver = webdriver.Firefox()
            case 'Chrome':
                self._driver = webdriver.Chrome()
            case 'Edge':
                self._driver = webdriver.Edge()
            case _:
                self._driver = webdriver.Firefox()

        self.not_found = list()
        self.found_many = list()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._driver.close()

    def force_quit(self):
        self._driver.quit()

    def open_site(self):
        self._driver.get('https://vocalremover.org')

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
        time.sleep(3)


def _get_vocals(audio_path, browser='Firefox'):
    ww = WebWalker(browser)
    ww.open_site()
    ww.upload_file(audio_path)
    ww.save_vocals()
    time.sleep(3)
    ww.force_quit()


def run_loop(audio_path, browser, check_downloads, check_db, check_json, check_folder, *, json_path, folder_path):
    audio_files = general.get_audio_files(audio_path)
    already_in_downloads = [[get_band_name(path), get_song_title(path)] for path in general.get_audio_files(str(Path.home() / 'Downloads'))]
    json_db = vocals_analysis.get_data_from_json(json_path)
    already_in_json = [[d['band'], d['title']] for d in json_db]
    already_in_folder = [[get_band_name(path), get_song_title(path)] for path in general.get_audio_files(folder_path)]

    for audio_file in audio_files:
        audio_file = os.path.normpath(audio_file)
        metadata = [get_band_name(audio_file), get_song_title(audio_file)]

        print(audio_file)

        if check_downloads and metadata in already_in_downloads:
            print('Vocals already extracted to Downloads')
        elif check_db and is_in_db(get_band_name(audio_file), get_song_title(audio_file)):
            print('Vocals already added to database')
        elif check_json and metadata in already_in_json:
            print('Vocals already saved in json file')
        elif check_folder and metadata in already_in_folder:
            print(f'Vocals already present in {folder_path}')
        else:
            try:
                _get_vocals(audio_file, browser)
                print('Done')
            except Exception as e:
                print('Server not responding')
