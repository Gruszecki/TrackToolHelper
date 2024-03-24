import threading

from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QPushButton, QRadioButton, QLabel, QLineEdit, QFileDialog, QWidget
from PySide6.QtCore import Qt, QStandardPaths, QPointF
from PySide6.QtGui import QFont, QPixmap, QPalette, QBrush

import general
import vocals_scrapper


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Track Tool Helper")
        self.setWindowFlags(Qt.FramelessWindowHint)

        layout = QVBoxLayout()

        self.input_path = QLineEdit()
        self.input_path.setPlaceholderText("Ścieżka do piosenek")
        self.input_path.setStyleSheet("background-color: rgba(255, 255, 255, 0.7);")
        layout.addWidget(self.input_path)

        self.input_path_button = QPushButton("Wybierz folder")
        self.input_path_button.setStyleSheet("background-color: lightblue;")
        self.input_path_button.clicked.connect(self.select_input_path)
        layout.addWidget(self.input_path_button)

        self.output_path = QLineEdit()
        self.output_path.setText(QStandardPaths.writableLocation(QStandardPaths.DownloadLocation))
        self.output_path.setStyleSheet("background-color: rgba(255, 255, 255, 0.7);")
        self.output_path.setPlaceholderText("Ścieżka outputu")
        layout.addWidget(self.output_path)

        self.output_path_button = QPushButton("Wybierz folder")
        self.output_path_button.setStyleSheet("background-color: lightblue;")
        self.output_path_button.clicked.connect(self.select_output_path)
        layout.addWidget(self.output_path_button)

        self.firefox_button = QRadioButton("Firefox")
        self.firefox_button.setChecked(True)
        layout.addWidget(self.firefox_button)

        self.chrome_button = QRadioButton("Chrome")
        layout.addWidget(self.chrome_button)

        self.edge_button = QRadioButton("Edge")
        layout.addWidget(self.edge_button)

        self.start_button = QPushButton("Start")
        self.start_button.setStyleSheet("background-color: lightblue")
        self.start_button.clicked.connect(self.start_scraping_vocals)
        layout.addWidget(self.start_button)

        self.exit_button = QPushButton("Wyjdź")
        self.exit_button.clicked.connect(self.close)
        layout.addWidget(self.exit_button)

        self.version_label = QLabel("v0.1")
        self.version_label.setFont(QFont("Arial", 8))
        self.version_label.setAlignment(Qt.AlignRight)
        layout.addWidget(self.version_label)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

        QApplication.setStyle("Fusion")

        self.setFixedSize(500, 300)

        palette = QPalette()
        palette.setBrush(QPalette.Window, QBrush(QPixmap(general.resource_path("background.jpg")).scaled(self.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)))
        self.setPalette(palette)

        self.m_mouse_down = False
        self.m_old_pos = None

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

    def select_output_path(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Wybierz folder")
        self.output_path.setText(folder_path)


app = QApplication([])
window = MainWindow()
window.show()
app.exec()
