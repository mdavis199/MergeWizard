from PyQt5.QtWidgets import QWidget
from .ui.ProgressBar import Ui_ProgressBar


class ProgressBar(QWidget):
    def __init(self, parent: QWidget):
        super().__init__(parent)
        self.ui = Ui_ProgressBar()
        self.ui.setupUi(self)
