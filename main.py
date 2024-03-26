from PySide6.QtWidgets import QApplication

import gui


app = QApplication([])
window = gui.MainWindow()
window.show()
app.exec()
