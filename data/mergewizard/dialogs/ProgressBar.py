from PyQt5.QtCore import pyqtSignal, Qt, QTimer
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

    def acceptAfterDelay(self, msec: int = 0):
        """ After the DataCache loads its data, it takes quite some
        time for the GUI to load it into the views.  This delay
        before closing, makes it look much smoother."""
        QTimer.singleShot(msec, lambda: self.accept())

