from PyQt5.QtCore import QDir
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QWidget, QDialog, QFileDialog
from mergewizard.domain.Context import Context
from mergewizard.constants import Setting, Icon
from .ui.SettingsDialog import Ui_SettingsDialog


class SettingsDialog(QDialog):
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self.ui = Ui_SettingsDialog()
        self.ui.setupUi(self)
        self.ui.errorIndicator.setPixmap(QPixmap(Icon.ERROR))
        self.ui.zeditPathButton.setIcon(QIcon(Icon.FOLDER))
        self.ui.zeditPathButton.clicked.connect(lambda: self.showFileDialog())
        self.ui.zeditPathEdit.textChanged.connect(lambda: self.validateZEditPath())

    def loadSettings(self, context: Context):
        # set ui widget values
        self.ui.enableHiding.setChecked(context.enableHidingPlugins)
        hidingMethod = context.hidingMethod
        if hidingMethod == "mohidden":
            self.ui.hideMethod.setChecked(True)
        elif hidingMethod == "optional":
            self.ui.optionalMethod.setChecked(True)
        else:
            self.ui.disableMethod.setChecked(True)
        self.ui.excludeInactiveMods.setChecked(context.excludeInactiveMods)
        self.ui.zeditPathEdit.setText(context.zEditFolder)
        self.ui.modNameTemplate.setText(context.modNameTemplate)
        self.ui.profileNameTemplate.setText(context.profileNameTemplate)
        self.validateZEditPath()

    def storeSettings(self, context: Context):
        context.storeUserSetting(Setting.ENABLE_HIDING_PLUGINS, self.ui.enableHiding.isChecked())
        if self.ui.hideMethod.isChecked():
            context.storeUserSetting(Setting.HIDING_METHOD, "mohidden")
        if self.ui.optionalMethod.isChecked():
            context.storeUserSetting(Setting.HIDING_METHOD, "optional")
        if self.ui.disableMethod.isChecked():
            context.storeUserSetting(Setting.HIDING_METHOD, "disable")
        context.storeUserSetting(Setting.EXCLUDE_INACTIVE_MODS, self.ui.excludeInactiveMods.isChecked())
        context.storeUserSetting(Setting.ZEDIT_FOLDER, self.ui.zeditPathEdit.text())
        context.storeUserSetting(Setting.MODNAME_TEMPLATE, self.ui.modNameTemplate.text())
        context.storeUserSetting(Setting.PROFILENAME_TEMPLATE, self.ui.profileNameTemplate.text())

    def showFileDialog(self):
        dirName = QFileDialog.getExistingDirectory(
            self, self.tr("zEdit Directory"), self.ui.zeditPathEdit.text(), QFileDialog.ShowDirsOnly
        )
        if dirName:
            self.ui.zeditPathEdit.setText(dirName)
        self.validateZEditPath()

    def validateZEditPath(self):
        dir = QDir(self.ui.zeditPathEdit.text())
        if dir.exists("zedit.exe"):
            self.ui.errorIndicator.setVisible(False)
        else:
            self.ui.errorIndicator.setVisible(True)

