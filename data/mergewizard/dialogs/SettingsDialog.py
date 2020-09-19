from PyQt5.QtWidgets import QWidget, QDialog
from PyQt5.QtCore import qInfo
from mergewizard.domain.Context import Context
from mergewizard.constants import Setting
from .ui.SettingsDialog import Ui_SettingsDialog


class SettingsDialog(QDialog):
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self.ui = Ui_SettingsDialog()
        self.ui.setupUi(self)

    def loadSettings(self, context: Context):
        # set ui widget values
        self.ui.enableHiding.setChecked(context.enableHidingPlugins)
        qInfo("enableHiding? {}".format(self.ui.enableHiding.isChecked()))
        hidingMethod = context.hidingMethod
        if hidingMethod == "mohidden":
            self.ui.hideMethod.setChecked(True)
        elif hidingMethod == "optional":
            self.ui.optionalMethod.setChecked(True)
        else:
            self.ui.disableMethod.setChecked(True)
        self.ui.zeditPathEdit.setText(context.zMergeFolder)
        self.ui.modNameTemplate.setText(context.modNameTemplate)
        self.ui.profileNameTemplate.setText(context.profileNameTemplate)

    def storeSettings(self, context: Context):
        context.storeUserSetting(Setting.ENABLE_HIDING_PLUGINS, self.ui.enableHiding.isChecked())
        if self.ui.hideMethod.isChecked():
            context.storeUserSetting(Setting.HIDING_METHOD, "mohidden")
        if self.ui.optionalMethod.isChecked():
            context.storeUserSetting(Setting.HIDING_METHOD, "optional")
        if self.ui.disableMethod.isChecked():
            context.storeUserSetting(Setting.HIDING_METHOD, "disable")
        context.storeUserSetting(Setting.ZMERGE_FOLDER, self.ui.zeditPathEdit.text())
        context.storeUserSetting(Setting.MODNAME_TEMPLATE, self.ui.modNameTemplate.text())
        context.storeUserSetting(Setting.PROFILENAME_TEMPLATE, self.ui.profileNameTemplate.text())

