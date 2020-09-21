from PyQt5.QtWidgets import QWidget
from mergewizard.dialogs.WizardPage import WizardPage
from mergewizard.domain.Context import Context
from .ui.PageZMerge import Ui_PageZMerge


class PageZMerge(WizardPage):
    def __init__(self, context: Context, parent: QWidget = None):
        super().__init__(parent)
        self.ui = Ui_PageZMerge()
        self.ui.setupUi(self)
        self.context = context

    def isOkToExit(self):
        return True
