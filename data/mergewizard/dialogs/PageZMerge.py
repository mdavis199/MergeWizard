from PyQt5.QtCore import QDir
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QWidget, QFileDialog
from mergewizard.dialogs.WizardPage import WizardPage
from mergewizard.domain.Context import Context
from mergewizard.constants import Setting, Icon
from .ui.PageZMerge import Ui_PageZMerge


class PageZMerge(WizardPage):
    def __init__(self, context: Context, parent: QWidget = None):
        super().__init__(parent)
        self.ui = Ui_PageZMerge()
        self.ui.setupUi(self)
        self.context = context

        self.ui.folderError.setPixmap(QPixmap(Icon.ERROR))
        self.ui.profileError.setPixmap(QPixmap(Icon.ERROR))
        self.ui.pluginNameError.setPixmap(QPixmap(Icon.ERROR))
        self.ui.modNameError.setPixmap(QPixmap(Icon.ERROR))

        self.setZEditFolderError()
        self.setZMergeProfileError()
        self.setPluginNameError()
        self.setModNameError()

        self.ui.zeditPathButton.setIcon(QIcon(Icon.FOLDER))
        self.ui.zeditPathButton.clicked.connect(lambda: self.showFileDialog())
        self.ui.zeditPathEdit.textChanged.connect(lambda: self.validateZEditPath())
        self.ui.pluginName.textChanged.connect(lambda: self.validatePluginName())
        self.ui.modName.textChanged.connect(lambda: self.validateModName())
        self.context.settingChanged.connect(self.settingChanged)

    def initializePage(self):
        self.initializeMOProfileName()
        self.initializeZEditPath()
        self.initializeZMergeProfile()
        self.initializeNames()
        self.validatePanel()

    def isOkToExit(self):
        return True

    def setZEditFolderError(self, msg=None):
        if msg:
            self.ui.folderError.setToolTip(msg)
        self.ui.folderError.setVisible(bool(msg))

    def setZMergeProfileError(self, msg=None):
        if msg:
            self.ui.profileError.setToolTip(msg)
        self.ui.profileError.setVisible(bool(msg))

    def setPluginNameError(self, msg=None):
        if msg:
            self.ui.pluginNameError.setToolTip(msg)
        self.ui.pluginNameError.setVisible(bool(msg))

    def setModNameError(self, msg=None):
        if msg:
            self.ui.modNameError.setToolTip(msg)
        self.ui.modNameError.setVisible(bool(msg))

    def showFileDialog(self):
        dirName = QFileDialog.getExistingDirectory(
            self, self.tr("zEdit Directory"), self.ui.zeditPathEdit.text(), QFileDialog.ShowDirsOnly
        )
        if dirName:
            self.ui.zeditPathEdit.setText(dirName)
        self.validateZEditPath()

    def validatePanel(self):
        self.validateZEditPath()
        self.validateZMergeProfile()
        self.validatePluginName()
        self.validateModName()

    def validateZEditPath(self):
        if not self.ui.zeditPathEdit.text():
            self.setZEditFolderError("Path cannot be empty.")
        dir = QDir(self.ui.zeditPathEdit.text())
        if dir.exists("zedit.exe"):
            self.setZEditFolderError()
        else:
            self.setZEditFolderError(self.tr('Path does not include "zedit.exe".'))

    def validateZMergeProfile(self):
        if self.ui.zmergeProfile.currentIndex() < 0:
            self.setZMergeProfileError("Unable to find a zMerge profile for this game.")
        else:
            self.setZEditFolderError()

    def validatePluginName(self):
        if not self.ui.pluginName.text():
            self.setPluginNameError("Plugin name cannot be empty.")
        else:
            self.setPluginNameError()

    def validateModName(self):
        if not self.ui.modName.text():
            self.setModNameError("Mod name cannot be empty.")
        else:
            self.setModNameError()

    def settingChanged(self, setting: int):
        if setting == Setting.ZEDIT_FOLDER:
            self.ui.zeditPathEdit.setText("")
            self.initializeZMergeProfile()
        if setting == Setting.PROFILENAME_TEMPLATE:
            self.initializeNames()
        if setting == Setting.MODNAME_TEMPLATE:
            self.initializeNames()

    def initializeMOProfileName(self):
        # TODO: If we allow creating merges to other MO profile, change this.
        # For now this is okay.
        self.ui.moProfile.setText(self.context.profile.currentProfileName())

    def initializeZEditPath(self):
        if not self.ui.zeditPathEdit.text():
            self.ui.zeditPathEdit.setText(self.context.zEditFolder)

    def initializeZMergeProfile(self):
        pass

    def initializeNames(self):
        selectedMerge = self.context.dataCache.mergeModel.selectedMergeName()
        self.ui.modName.setText(selectedMerge)

