import os
import threading

from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QPushButton, QRadioButton, QLabel, QLineEdit, QFileDialog, QWidget, QTabWidget, QSlider, QTableWidget, QTableWidgetItem, QCheckBox, QMessageBox
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QFont, QPixmap, QPalette, QBrush

import general
import radioboss_db
import vocals_analysis
import vocals_scrapper


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Track Tool Helper")
        self.setWindowFlags(Qt.FramelessWindowHint)

        layout = QVBoxLayout()

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

        self.tab_widget = QTabWidget()
        self.tab1 = QWidget()
        self.tab2 = QWidget()
        self.tab3 = QWidget()

        self.tab_widget.addTab(self.tab1, "get vocs")
        self.tab_widget.addTab(self.tab2, "intro2db")
        self.tab_widget.addTab(self.tab3, "results")

        self.tab1_layout = QVBoxLayout()
        self.tab1.setLayout(self.tab1_layout)

        self.tab2_layout = QVBoxLayout()
        self.tab2.setLayout(self.tab2_layout)

        self.tab3_layout = QVBoxLayout()
        self.tab3.setLayout(self.tab3_layout)

        layout.addWidget(self.tab_widget)

        ################### Tab 1 #####################

        # Songs path
        self.songs_path_layout = QHBoxLayout()

        self.songs_path = QLineEdit()
        self.songs_path.setPlaceholderText("Ścieżka do piosenek")
        self.songs_path.setStyleSheet("background-color: rgba(255, 255, 255, 0.7);")
        self.songs_path_layout.addWidget(self.songs_path)

        self.songs_path_button = QPushButton("Wybierz folder")
        self.songs_path_button.setStyleSheet("background-color: lightblue;")
        self.songs_path_button.clicked.connect(self.select_songs_path)
        self.songs_path_layout.addWidget(self.songs_path_button)

        self.tab1_layout.addLayout(self.songs_path_layout)

        # Options

        self.check_downloads = QCheckBox('Sprawdzaj czy wokalu nie ma w pobranych')
        self.check_downloads.setChecked(True)
        self.tab1_layout.addWidget(self.check_downloads)

        self.check_vox_in_db_layout = QHBoxLayout()

        self.check_vox_in_db = QCheckBox('Sprawdzaj wokal w bazie')
        self.check_vox_in_db.setChecked(True)
        self.check_vox_in_db_layout.addWidget(self.check_vox_in_db)

        self.check_vocs_in_db_path = QLineEdit()
        self.check_vocs_in_db_path.setPlaceholderText("Ścieżka do bazy danych")
        default_db_path = os.path.join(os.environ['APPDATA'], 'djsoft.net', 'tracks.db')
        self.check_vocs_in_db_path.setText(default_db_path) if os.path.exists(default_db_path) else ''
        self.check_vocs_in_db_path.setStyleSheet("background-color: rgba(255, 255, 255, 0.7);")
        self.check_vox_in_db_layout.addWidget(self.check_vocs_in_db_path)

        self.db_path_button = QPushButton("Wybierz bazę")
        self.db_path_button.setStyleSheet("background-color: lightblue;")
        self.db_path_button.clicked.connect(self.select_db_file)
        self.check_vox_in_db_layout.addWidget(self.db_path_button)

        self.tab1_layout.addLayout(self.check_vox_in_db_layout)

        self.check_vox_in_json_layout = QHBoxLayout()

        self.check_vox_in_json = QCheckBox('Sprawdzaj wokal w jsonie')
        self.check_vox_in_json.setChecked(True)
        self.check_vox_in_json_layout.addWidget(self.check_vox_in_json)

        self.check_vox_in_json_path = QLineEdit()
        self.check_vox_in_json_path.setPlaceholderText("*.json")
        self.check_vox_in_json_path.setStyleSheet("background-color: rgba(255, 255, 255, 0.7);")
        self.check_vox_in_json_layout.addWidget(self.check_vox_in_json_path)

        self.check_vox_in_json_button = QPushButton("Wybierz json")
        self.check_vox_in_json_button.setStyleSheet("background-color: lightblue")
        self.check_vox_in_json_button.clicked.connect(self.select_json_path)
        self.check_vox_in_json_layout.addWidget(self.check_vox_in_json_button)

        self.tab1_layout.addLayout(self.check_vox_in_json_layout)

        self.check_vox_in_folder_layout = QHBoxLayout()

        self.check_vox_in_folder = QCheckBox('Sprawdzaj wokal w folderze')
        self.check_vox_in_folder.setChecked(False)
        self.check_vox_in_folder_layout.addWidget(self.check_vox_in_folder)

        self.check_vox_in_folder_path = QLineEdit()
        self.check_vox_in_folder_path.setPlaceholderText("Ścieżka do folderu")
        self.check_vox_in_folder_path.setStyleSheet("background-color: rgba(255, 255, 255, 0.7);")
        self.check_vox_in_folder_layout.addWidget(self.check_vox_in_folder_path)

        self.folder_path_button = QPushButton("Wybierz folder")
        self.folder_path_button.setStyleSheet("background-color: lightblue;")
        self.folder_path_button.clicked.connect(self.select_folder_path)
        self.check_vox_in_folder_layout.addWidget(self.folder_path_button)

        self.tab1_layout.addLayout(self.check_vox_in_folder_layout)

        # Browser pick
        self.browsers_layout = QHBoxLayout()

        self.firefox_button = QRadioButton("Firefox")
        self.firefox_button.setChecked(True)
        self.browsers_layout.addWidget(self.firefox_button)

        self.chrome_button = QRadioButton("Chrome")
        self.browsers_layout.addWidget(self.chrome_button)

        self.edge_button = QRadioButton("Edge")
        self.browsers_layout.addWidget(self.edge_button)

        self.tab1_layout.addLayout(self.browsers_layout)

        # Start button
        self.start_scraping_vocals_button = QPushButton("Start")
        self.start_scraping_vocals_button.setStyleSheet("background-color: lightblue")
        self.start_scraping_vocals_button.clicked.connect(self.start_scraping_vocals)
        self.tab1_layout.addWidget(self.start_scraping_vocals_button)


        ##################### Tab 2 #######################
        THRESHOLD_INIT = 0.5

        # RadioBOSS database
        self.db_path_layout = QHBoxLayout()

        self.db_path = QLineEdit()
        self.db_path.setPlaceholderText("Ścieżka do bazy danych")
        default_db_path = os.path.join(os.environ['APPDATA'], 'djsoft.net', 'tracks.db')
        self.db_path.setText(default_db_path) if os.path.exists(default_db_path) else ''
        self.db_path.setStyleSheet("background-color: rgba(255, 255, 255, 0.7);")
        self.db_path_layout.addWidget(self.db_path)

        self.db_path_button = QPushButton("Wybierz bazę")
        self.db_path_button.setStyleSheet("background-color: lightblue;")
        self.db_path_button.clicked.connect(self.select_db_file)
        self.db_path_layout.addWidget(self.db_path_button)

        self.tab2_layout.addLayout(self.db_path_layout)


        # Vocals
        self.vocals_path_layout = QHBoxLayout()

        self.vocals_path = QLineEdit()
        self.vocals_path.setPlaceholderText("Ścieżka do wokali")
        self.vocals_path.setStyleSheet("background-color: rgba(255, 255, 255, 0.7);")
        self.vocals_path_layout.addWidget(self.vocals_path)

        self.vocals_path_button = QPushButton("Wybierz folder")
        self.vocals_path_button.setStyleSheet("background-color: lightblue;")
        self.vocals_path_button.clicked.connect(self.select_vocals_path)
        self.vocals_path_layout.addWidget(self.vocals_path_button)

        self.read_from_mp3_button = QPushButton("Odczytaj z mp3")
        self.read_from_mp3_button.setStyleSheet("background-color: lightblue")
        self.read_from_mp3_button.clicked.connect(self.read_vocals_time)
        self.vocals_path_layout.addWidget(self.read_from_mp3_button)

        self.stop_button = QPushButton("Stop")
        self.stop_button.setStyleSheet("background-color: lightblue")
        self.stop_button.clicked.connect(self.stop_reading)
        self.vocals_path_layout.addWidget(self.stop_button)

        self.tab2_layout.addLayout(self.vocals_path_layout)


        # Threshold
        self.slider_input_layout = QHBoxLayout()

        self.threshold_label = QLabel("Threshold")
        self.slider_input_layout.addWidget(self.threshold_label)

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(0)
        self.slider.setMaximum(100)
        self.slider.setValue(THRESHOLD_INIT*100)
        self.slider.valueChanged.connect(self.update_input_box)
        self.slider_input_layout.addWidget(self.slider)

        self.input_threshold = QLineEdit()
        self.input_threshold.setFixedWidth(50)
        self.input_threshold.setText(str(THRESHOLD_INIT))
        self.input_threshold.textChanged.connect(self.update_slider)
        self.slider_input_layout.addWidget(self.input_threshold)

        self.tab2_layout.addLayout(self.slider_input_layout)

        # Saving options
        self.omit_vocals_from_db_checkbox = QCheckBox('Nie przetwarzaj wokali dla piosenek, które są już w bazie RadioBossa')
        self.omit_vocals_from_db_checkbox.setChecked(True)
        self.tab2_layout.addWidget(self.omit_vocals_from_db_checkbox)

        self.omit_vocals_from_results_checkbox = QCheckBox('Nie przetwarzaj wokali dla piosenek, które są już wczytane')
        self.omit_vocals_from_results_checkbox.setChecked(True)
        self.tab2_layout.addWidget(self.omit_vocals_from_results_checkbox)

        self.overwrite_checkbox = QCheckBox('Nadpisz piosenkę w bazie')
        self.overwrite_checkbox.setChecked(False)
        self.tab2_layout.addWidget(self.overwrite_checkbox)

        # Json
        self.read_voc_info_buttons_layout = QHBoxLayout()

        self.read_from_json_button = QPushButton("Wczytaj dane z pliku json")
        self.read_from_json_button.setStyleSheet("background-color: lightblue")
        self.read_from_json_button.clicked.connect(self.load_vocals_time)
        self.read_voc_info_buttons_layout.addWidget(self.read_from_json_button)

        self.save_to_json_button = QPushButton("Zapisz dane do pliku json")
        self.save_to_json_button.setStyleSheet("background-color: lightblue")
        self.save_to_json_button.clicked.connect(self.dump_vocals_time)
        self.read_voc_info_buttons_layout.addWidget(self.save_to_json_button)

        self.tab2_layout.addLayout(self.read_voc_info_buttons_layout)

        # Buttons: Read from mp3, save, clear
        self.read_stop_save_clear_buttons_layout = QHBoxLayout()

        self.save_db_button = QPushButton("Zapisz w bazie")
        self.save_db_button.setStyleSheet("background-color: lightblue")
        self.save_db_button.clicked.connect(self.send_vocs_to_db)
        self.read_stop_save_clear_buttons_layout.addWidget(self.save_db_button)

        self.clear_results_button = QPushButton("Czyść wyniki")
        self.clear_results_button.setStyleSheet("background-color: lightyellow")
        self.clear_results_button.clicked.connect(self.clear_results)
        self.read_stop_save_clear_buttons_layout.addWidget(self.clear_results_button)

        self.tab2_layout.addLayout(self.read_stop_save_clear_buttons_layout)


        ###################### Tab 3 #######################

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Band", "Title", "Voc start", "Voc end"])

        self.tab3_layout.addWidget(self.table)


        ##################### Footer #######################

        self.exit_button = QPushButton("Wyjdź")
        self.exit_button.clicked.connect(self.close)
        layout.addWidget(self.exit_button)

        self.version_label = QLabel("v1.0")
        self.version_label.setFont(QFont("Arial", 8))
        self.version_label.setAlignment(Qt.AlignRight)
        layout.addWidget(self.version_label)

        QApplication.setStyle("Fusion")

        self.setFixedSize(500, 340)

        palette = QPalette()
        palette.setBrush(QPalette.Window, QBrush(QPixmap(general.resource_path("background.jpg")).scaled(self.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)))
        self.setPalette(palette)

        self.m_mouse_down = False
        self.m_old_pos = None

    def update_table(self, voc_data):
        row = self.table.rowCount()
        self.table.insertRow(row)
        self.table.setItem(row, 0, QTableWidgetItem(str(voc_data['band'])))
        self.table.setItem(row, 1, QTableWidgetItem(str(voc_data['title'])))
        self.table.setItem(row, 2, QTableWidgetItem(str(voc_data['start'])))
        self.table.setItem(row, 3, QTableWidgetItem(str(voc_data['end'])))

    def update_input_box(self, value):
        self.input_threshold.blockSignals(True)
        self.input_threshold.setText(str(value / 100))
        self.input_threshold.blockSignals(False)

    def update_slider(self, text):
        self.slider.blockSignals(True)
        self.slider.setValue(float(text) * 100)
        self.slider.blockSignals(False)

    def mousePressEvent(self, event):
        self.m_old_pos = event.globalPosition()
        self.m_mouse_down = event.button() == Qt.LeftButton

    def mouseMoveEvent(self, event):
        x = event.globalPosition().x()
        y = event.globalPosition().y()

        if self.m_mouse_down:
            delta = QPointF(event.globalPosition() - self.m_old_pos)
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.m_old_pos = event.globalPosition()

    def mouseReleaseEvent(self, event):
        m_mouse_down = False

    def select_songs_path(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Wybierz folder")
        self.songs_path.setText(folder_path)

    def select_vocals_path(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Wybierz folder z wokalami")
        self.vocals_path.setText(folder_path)

    def select_folder_path(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Wybierz folder z wokalami")
        self.check_vox_in_folder_path.setText(folder_path)

    def select_json_path(self):
        dialog = QFileDialog()
        json_path, _ = dialog.getOpenFileName(filter="JSON files (*.json)")

        if json_path:
            self.check_vox_in_json_path.setText(json_path)

    def select_db_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Wybierz plik z bazą danych")
        if file_path:
            radioboss_db.DB_PATH = file_path
            self.db_path.setText(file_path)
            self.check_vocs_in_db_path.setText(file_path)

    def start_scraping_vocals(self):
        if self.check_vox_in_db.isChecked() and not self.check_vocs_in_db_path.text():
            info_message = QMessageBox(self)
            info_message.setIcon(QMessageBox.Warning)
            info_message.setWindowTitle('Uzupełnij, proszę, wymagane pole')
            info_message.setText('Jeśli chcesz sprawdzać czy wokalu do danej piosenki nie ma już w RadioBossie, musisz najpierw wskazać bazę danych.\n\n'
                                 'Prawdopodobnie nazywa się tracks.db i domyślnie powinna znajdować się w:\n '
                                 'C:\\Users\\<user>\\AppData\\Roaming\\djsoft.net\\')
            info_message.exec()
            return

        if self.check_vox_in_json.isChecked() and not self.check_vox_in_json_path.text():
            info_message = QMessageBox(self)
            info_message.setIcon(QMessageBox.Warning)
            info_message.setWindowTitle('Uzupełnij, proszę, wymagane pole')
            info_message.setText('Jeśli chcesz sprawdzać czy wokal do danej piosenki nie został już zapisany do pliku json, musisz najpierw wskazać plik json.')
            info_message.exec()
            return

        if self.check_vox_in_json.isChecked() and not self.check_vox_in_json_path.text():
            info_message = QMessageBox(self)
            info_message.setIcon(QMessageBox.Warning)
            info_message.setWindowTitle('Uzupełnij, proszę, wymagane pole')
            info_message.setText('Jeśli chcesz sprawdzać czy wokal do danej piosenki nie został już zapisany w folderze, musisz najpierw wskazać folder.')
            info_message.exec()
            return

        if self.firefox_button.isChecked():
            browser = 'Firefox'
        elif self.chrome_button.isChecked():
            browser = 'Chrome'
        elif self.edge_button.isChecked():
            browser = 'Edge'
        else:
            browser = 'Firefox'

        threading.Thread(target=lambda: vocals_scrapper.run_loop(
            self.songs_path.text(),
            browser,
            self.check_downloads.isChecked(),
            self.check_vox_in_db.isChecked(),
            self.check_vox_in_json.isChecked(),
            self.check_vox_in_folder.isChecked(),
            json_path=self.check_vox_in_json_path.text(),
            folder_path=self.check_vox_in_folder_path.text()
        )).start()

    def read_vocals_time(self):
        if self.omit_vocals_from_db_checkbox.isChecked() and not self.db_path.text():
            info_message = QMessageBox(self)
            info_message.setIcon(QMessageBox.Warning)
            info_message.setWindowTitle('Uzupełnij, proszę, wymagane pole')
            info_message.setText('Jeśli chcesz sprawdzać czy dana piosenka jest już w bazie, musisz podać jej lokalizację.\n\n'
                                 'Prawdopodobnie nazywa się tracks.db i domyślnie powinna znajdować się w:\n '
                                 'C:\\Users\\<user>\\AppData\\Roaming\\djsoft.net\\\n\n'
                                 'Miłego dnia.')
            info_message.exec()
        else:
            self.worker = vocals_analysis.Worker(
                vocals_path=self.vocals_path.text(),
                threshold=float(self.input_threshold.text()),
                look_in_db=self.omit_vocals_from_db_checkbox.isChecked(),
                look_in_results=self.omit_vocals_from_results_checkbox.isChecked(),
                db_path=self.db_path.text()
            )
            self.worker.update_voc.connect(self.update_table)
            self.worker.start()

    def load_vocals_time(self):
        dialog = QFileDialog()
        json_path, _ = dialog.getOpenFileName(filter="JSON files (*.json)")

        if json_path:
            vocals_analysis.load_data(json_path)

        self.clear_table_only()

        for record in vocals_analysis.vocal_time_database:
            self.update_table(record)

    def dump_vocals_time(self):
        dialog = QFileDialog()
        json_path, _ = dialog.getSaveFileName(filter="JSON files (*.json)")

        if json_path:
            vocals_analysis.save_data(json_path)

    def stop_reading(self):
        if hasattr(self, 'worker'):
            self.worker.stop()

    def send_vocs_to_db(self):
        if self.db_path.text():
            if not vocals_analysis.vocal_time_database:
                dialog_box = QMessageBox(self)
                dialog_box.setWindowTitle("Czegoś tu nie rozumiem")
                dialog_box.setText('Ale wiesz, że nie masz wczytanych żadnych wyników? '
                                   'Możemy kontynuować, ale i tak nic się nie stanie.\n\n'
                                   'Kontynuujemy?')
                dialog_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
                dialog_box.setIcon(QMessageBox.Question)
                button = dialog_box.exec()

                if button == QMessageBox.No:
                    return

            dialog_box = QMessageBox(self)
            dialog_box.setWindowTitle("Tylko się upewniam")
            dialog_box.setText('Czy RadioBoss jest wyłączony?\n\n'
                                 'Jeśli nie to okej, po prostu będziesz musiał go zresetować, żeby zobaczyć aktualne dane.\n\n'
                                 'Kontynuujemy?')
            dialog_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            dialog_box.setIcon(QMessageBox.Question)
            button = dialog_box.exec()

            if button == QMessageBox.Yes:
                radioboss_db.add_songs_info(self.overwrite_checkbox.isChecked(), vocals_analysis.vocal_time_database)

        else:
            info_message = QMessageBox(self)
            info_message.setIcon(QMessageBox.Warning)
            info_message.setWindowTitle('Uzupełnij, proszę, wymagane pole')
            info_message.setText('Jeśli chcesz uzupełnić bazę RadioBossa, musisz najpierw wskazać bazę danych.\n\n'
                                 'Prawdopodobnie nazywa się tracks.db i domyślnie powinna znajdować się w:\n '
                                 'C:\\Users\\<user>\\AppData\\Roaming\\djsoft.net\\\n'
                                 'Pamiętaj też o wyłączeniu RadioBossa w trakcie aktuailzacji bazy danych.\n\n'
                                 'Miłego dnia.')
            info_message.exec()

    def clear_table_only(self):
        self.table.setRowCount(0)

    def clear_backend_database(self):
        vocals_analysis.vocal_time_database.clear()

    def clear_results(self):
        self.clear_backend_database()
        self.clear_table_only()
        print('Wyniki zostały wyczyszczone')
