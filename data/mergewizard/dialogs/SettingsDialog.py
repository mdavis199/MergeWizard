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
        self.savePluginList = True

    def loadSettings(self, context: Context):
        self.loadZMerge = bool(context.getUserSetting(Setting.LOAD_ZMERGE, True))
        self.ui.loadZMerge.setChecked(self.loadZMerge)
        self.savePluginList = bool(context.getUserSetting(Setting.SAVE_PLUGIN_LIST, True))
        self.ui.savePluginList.setChecked(self.savePluginList)

    def storeSettings(self, context: Context):
        changedSettings = []
        newLoadZMerge = self.ui.loadZMerge.isChecked()
        if self.loadZMerge != newLoadZMerge:
            context.setUserSetting(Setting.LOAD_ZMERGE, newLoadZMerge)
            changedSettings.append(Setting.LOAD_ZMERGE)
        newSavePluginList = self.ui.savePluginList.isChecked()
        if self.savePluginList != newSavePluginList:
            context.setUserSetting(Setting.SAVE_PLUGIN_LIST, newSavePluginList)
            changedSettings.append(Setting.SAVE_PLUGIN_LIST)
        if changedSettings:
            self.settingsChanged.emit(changedSettings)
