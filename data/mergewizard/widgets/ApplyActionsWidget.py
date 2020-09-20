from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget

from .ui.ApplyActionsWidget import Ui_ApplyActionsWidget


class ApplyActionsWidget(QWidget):
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self.ui = Ui_ApplyActionsWidget()
        self.ui.setupUi(self)
        self.ui.warningFrame.setVisible(False)
        self.ui.errorFrame.setVisible(False)
        self.ui.profileError.setText("")
        self.ui.moGroup.setCheckable(False)

        self.initializeProfileList()

    def initializeProfileList(self):
        self.ui.profileBox.addItem("(Current Profile)", -1)
        self.ui.profileBox.addItem("Create new profile ...", -2)
