from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtWidgets import QWidget, QDialog
from mergewizard.domain.Context import Context
from mergewizard.constants import Setting
from .ui.SettingsDialog import Ui_SettingsDialog


class SettingsDialog(QDialog):
    settingsChanged = pyqtSignal(list)

    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self.ui = Ui_SettingsDialog()
        self.ui.setupUi(self)
        self.loadZMerge = True

    def loadSettings(self, context: Context):
        self.loadZMerge = bool(context.getUserSetting(Setting.LOAD_ZMERGE, True))
        self.ui.loadZMerge.setCheckState(Qt.Checked if self.loadZMerge else Qt.Unchecked)

    def storeSettings(self, context: Context):
        if self.loadZMerge != (self.ui.loadZMerge.checkState() == Qt.Checked):
            context.setUserSetting(Setting.LOAD_ZMERGE, not self.loadZMerge)
            self.settingsChanged.emit([Setting.LOAD_ZMERGE])
