from typing import List
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QWidget, QWizardPage


class WizardPage(QWizardPage):
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)

    def isOkToExit(self) -> bool:
        return True

    def deinitializePage(self) -> None:
        pass

    @pyqtSlot(list)
    def settingsChanged(self, settings: List[str]) -> None:
        pass
