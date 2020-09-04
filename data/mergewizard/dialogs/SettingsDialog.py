from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtWidgets import QWidget, QDialog
from mergewizard.domain.Context import Context
from mergewizard.constants import Setting
from .ui.SettingsDialog import Ui_SettingsDialog


class SettingsDialog(QDialog):
    settingsChanged = pyqtSignal(list)  # list of names of settings that changed.

    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self.ui = Ui_SettingsDialog()
        self.ui.setupUi(self)
        self.loadZMerge = True

    def loadSettings(self, context: Context):
        self.loadZMerge = bool(context.getUserSetting(Setting.LOAD_ZMERGE, True))
        self.ui.loadZMerge.setCheckState(Qt.Checked if self.loadZMerge else Qt.Unchecked)

    def storeSettings(self, context: Context):
        newLoadZMerge = self.ui.loadZMerge.checkState() == Qt.Checked
        if self.loadZMerge != newLoadZMerge:
            context.setUserSetting(Setting.LOAD_ZMERGE, newLoadZMerge)
            self.settingsChanged.emit([Setting.LOAD_ZMERGE])
