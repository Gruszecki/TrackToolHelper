import threading

from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QPushButton, QRadioButton, QLabel, QLineEdit, QFileDialog, QWidget, QTabWidget, QSlider, QTableWidget, QTableWidgetItem, QCheckBox
from PySide6.QtCore import Qt, QStandardPaths, QPointF
from PySide6.QtGui import QFont, QPixmap, QPalette, QBrush

import general
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

        self.input_path = QLineEdit()
        self.input_path.setPlaceholderText("Ścieżka do piosenek")
        self.input_path.setStyleSheet("background-color: rgba(255, 255, 255, 0.7);")
        self.tab1_layout.addWidget(self.input_path)

        self.input_path_button = QPushButton("Wybierz folder")
        self.input_path_button.setStyleSheet("background-color: lightblue;")
        self.input_path_button.clicked.connect(self.select_input_path)
        self.tab1_layout.addWidget(self.input_path_button)

        self.output_path = QLineEdit()
        self.output_path.setText(QStandardPaths.writableLocation(QStandardPaths.DownloadLocation))
        self.output_path.setStyleSheet("background-color: rgba(255, 255, 255, 0.7);")
        self.output_path.setPlaceholderText("Ścieżka outputu")
        self.tab1_layout.addWidget(self.output_path)

        self.output_path_button = QPushButton("Wybierz folder")
        self.output_path_button.setStyleSheet("background-color: lightblue;")
        self.output_path_button.clicked.connect(self.select_output_path)
        self.tab1_layout.addWidget(self.output_path_button)

        self.firefox_button = QRadioButton("Firefox")
        self.firefox_button.setChecked(True)
        self.tab1_layout.addWidget(self.firefox_button)

        self.chrome_button = QRadioButton("Chrome")
        self.tab1_layout.addWidget(self.chrome_button)

        self.edge_button = QRadioButton("Edge")
        self.tab1_layout.addWidget(self.edge_button)

        self.start_button = QPushButton("Start")
        self.start_button.setStyleSheet("background-color: lightblue")
        self.start_button.clicked.connect(self.start_scraping_vocals)
        self.tab1_layout.addWidget(self.start_button)


        ##################### Tab 2 #######################
        THRESHOLD_INIT = 0.5

        self.vocals_path = QLineEdit()
        self.vocals_path.setPlaceholderText("Ścieżka do wokali")
        self.vocals_path.setStyleSheet("background-color: rgba(255, 255, 255, 0.7);")
        self.tab2_layout.addWidget(self.vocals_path)

        self.vocals_path_button = QPushButton("Wybierz folder")
        self.vocals_path_button.setStyleSheet("background-color: lightblue;")
        self.vocals_path_button.clicked.connect(self.select_vocals_path)
        self.tab2_layout.addWidget(self.vocals_path_button)

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

        self.omit_vocals_checkbox = QCheckBox('Nie przetwarzaj wokali dla piosenek, które są już w bazie')
        self.omit_vocals_checkbox.setChecked(True)
        self.tab2_layout.addWidget(self.omit_vocals_checkbox)

        self.overwrite_checkbox = QCheckBox('Nadpisz piosenkę w bazie')
        self.overwrite_checkbox.setChecked(False)
        self.tab2_layout.addWidget(self.overwrite_checkbox)

        self.read_voc_button_layout = QHBoxLayout()

        self.read_button = QPushButton("Odczytaj")
        self.read_button.setStyleSheet("background-color: lightblue")
        self.read_button.clicked.connect(self.read_vocals_time)
        self.read_voc_button_layout.addWidget(self.read_button)

        self.stop_button = QPushButton("Stop")
        self.stop_button.setStyleSheet("background-color: lightblue")
        self.stop_button.clicked.connect(self.stop_reading)
        self.read_voc_button_layout.addWidget(self.stop_button)

        self.save_db_button = QPushButton("Zapisz w bazie")
        self.save_db_button.setStyleSheet("background-color: lightblue")
        self.save_db_button.clicked.connect(self.send_vocs_to_db)
        self.read_voc_button_layout.addWidget(self.save_db_button)

        self.clear_results_button = QPushButton("Czyść wyniki")
        self.clear_results_button.setStyleSheet("background-color: lightyellow")
        self.clear_results_button.clicked.connect(self.clear_results)
        self.read_voc_button_layout.addWidget(self.clear_results_button)

        self.tab2_layout.addLayout(self.read_voc_button_layout)


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

    def select_input_path(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Wybierz folder")
        self.input_path.setText(folder_path)

    def select_vocals_path(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Wybierz folder z wokalami")
        self.vocals_path.setText(folder_path)

    def select_output_path(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Wybierz folder")
        self.output_path.setText(folder_path)

    def start_scraping_vocals(self):
        if self.firefox_button.isChecked():
            browser = 'Firefox'
        elif self.chrome_button.isChecked():
            browser = 'Chrome'
        elif self.edge_button.isChecked():
            browser = 'Edge'
        else:
            browser = 'Firefox'

        threading.Thread(target=lambda: vocals_scrapper.run_loop(self.input_path.text(), self.output_path.text(), browser)).start()

    def read_vocals_time(self):
        self.worker = vocals_analysis.Worker(self.vocals_path.text(), float(self.input_threshold.text()))
        self.worker.update_voc.connect(self.update_table)
        self.worker.start()

    def stop_reading(self):
        if hasattr(self, 'worker'):
            self.worker.stop()

    def send_vocs_to_db(self):
        pass

    def clear_results(self):
        vocals_analysis.vocal_time_database.clear()
        self.table.setRowCount(0)
        print('Wyniki zostały wyczyszczone')


app = QApplication([])
window = MainWindow()
window.show()
app.exec()
