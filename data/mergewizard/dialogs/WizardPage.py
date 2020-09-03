from PyQt5.QtWidgets import QWidget, QWizardPage


class WizardPage(QWizardPage):
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)

    def isOkToExit(self) -> bool:
        return True

    def deinitializePage(self) -> None:
        pass

