from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtWidgets import QWidget, QDialog
from .ui.ProgressBar import Ui_ProgressBar


class ProgressBar(QDialog):
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self.ui = Ui_ProgressBar()
        self.ui.setupUi(self)
        self.ui.progressBar.setRange(0, 100)
        self.setWindowFlags(Qt.Window)

    def progressBar(self):
        return self.ui.progressBar

    def start(self):
        self.ui.progressBar.setValue(0)
        self.open()

    def setValue(self, value: int):
        self.ui.progressBar.setValue(value)

