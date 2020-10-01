from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QWidget, QDialog, QFileDialog
from mergewizard.domain.Context import Context, Validator
from mergewizard.domain.merge.ZEditConfig import ZEditConfig
from mergewizard.constants import Setting, Icon
from .ui.SettingsDialog import Ui_SettingsDialog


class SettingsDialog(QDialog):
    reloadDataRequest = pyqtSignal()

    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self.ui = Ui_SettingsDialog()
        self.ui.setupUi(self)
        self.zeditProfile = None

        self.ui.zeditPathError.setPixmap(QPixmap(Icon.ERROR))
        self.ui.zeditProfileError.setPixmap(QPixmap(Icon.ERROR))
        self.ui.reloadDataButton.setIcon(QIcon(Icon.RELOAD))
        self.ui.reloadDataButton.clicked.connect(lambda: self.onReloadData())
        self.ui.zeditPathButton.setIcon(QIcon(Icon.FOLDER))
        self.ui.zeditPathButton.clicked.connect(lambda: self.showFileDialog())
        self.ui.zeditPathEdit.textChanged.connect(lambda: self.validateZEditPath())

        self.ui.hidePluginsGroup.setId(self.ui.hide, 0)
        self.ui.hidePluginsGroup.setId(self.ui.move, 1)
        self.ui.hidePluginsGroup.setId(self.ui.disable, 2)

        self.ui.mergeMethodGroup.setId(self.ui.clobber, 0)
        self.ui.mergeMethodGroup.setId(self.ui.clean, 1)

        self.ui.archiveActionGroup.setId(self.ui.extract, 0)
        self.ui.archiveActionGroup.setId(self.ui.copy, 1)
        self.ui.archiveActionGroup.setId(self.ui.ignore, 2)

        self.ui.savingMergesGroup.setId(self.ui.sort, 0)
        self.ui.savingMergesGroup.setId(self.ui.prependNew, 1)
        self.ui.savingMergesGroup.setId(self.ui.appendNew, 2)
        self.ui.savingMergesGroup.setId(self.ui.prependChanged, 3)
        self.ui.savingMergesGroup.setId(self.ui.appendChanged, 4)

    def loadSettings(self, context: Context):
        self.zeditProfile = context.settings[Setting.ZEDIT_PROFILE]
        self.gameName = context.profile.gameName()

        # check boxes
        self.ui.enableHiding.setChecked(context.settings[Setting.ENABLE_HIDING_PLUGINS])
        self.ui.enableZMerge.setChecked(context.settings[Setting.ENABLE_ZMERGE_INTEGRATION])
        self.ui.enableLoadingZMerge.setChecked(context.settings[Setting.ENABLE_LOADING_ZMERGE])
        self.ui.excludeInactiveMods.setChecked(context.settings[Setting.EXCLUDE_INACTIVE_MODS])
        self.ui.useGameLoadOrder.setChecked(context.settings[Setting.USE_GAME_LOADORDER])
        self.ui.buildMergedArchive.setChecked(context.settings[Setting.BUILD_MERGED_ARCHIVE])
        self.ui.faceData.setChecked(context.settings[Setting.FACE_DATA])
        self.ui.voiceData.setChecked(context.settings[Setting.VOICE_DATA])
        self.ui.billboardData.setChecked(context.settings[Setting.BILLBOARD_DATA])
        self.ui.stringFiles.setChecked(context.settings[Setting.STRINGS_DATA])
        self.ui.translations.setChecked(context.settings[Setting.TRANSLATIONS_DATA])
        self.ui.iniFiles.setChecked(context.settings[Setting.INI_FILES_DATA])
        self.ui.dialogViews.setChecked(context.settings[Setting.DIALOGS_DATA])
        self.ui.generalAssets.setChecked(context.settings[Setting.GENERAL_ASSETS])

        # text edit fields
        self.ui.zeditPathEdit.setText(context.settings[Setting.ZEDIT_FOLDER])
        self.ui.profileNameTemplate.setText(context.settings[Setting.PROFILENAME_TEMPLATE])
        self.ui.modNameTemplate.setText(context.settings[Setting.MODNAME_TEMPLATE])

        # radio buttons
        hidingMethod = context.settings[Setting.HIDING_METHOD]
        self.ui.hidePluginsGroup.button(hidingMethod).setChecked(True)

        mergeMethod = context.settings[Setting.MERGE_METHOD]
        self.ui.mergeMethodGroup.button(mergeMethod).setChecked(True)

        archiveAction = context.settings[Setting.ARCHIVE_ACTION]
        self.ui.archiveActionGroup.button(archiveAction).setChecked(True)

        mergeOrder = context.settings[Setting.MERGE_ORDER]
        self.ui.savingMergesGroup.button(mergeOrder).setChecked(True)

    def storeSettings(self, context: Context):
        context.settings[Setting.ENABLE_HIDING_PLUGINS] = self.ui.enableHiding.isChecked()
        context.settings[Setting.ENABLE_ZMERGE_INTEGRATION] = self.ui.enableZMerge.isChecked()
        context.settings[Setting.ENABLE_LOADING_ZMERGE] = self.ui.enableLoadingZMerge.isChecked()
        context.settings[Setting.EXCLUDE_INACTIVE_MODS] = self.ui.excludeInactiveMods.isChecked()
        context.settings[Setting.USE_GAME_LOADORDER] = self.ui.useGameLoadOrder.isChecked()
        context.settings[Setting.BUILD_MERGED_ARCHIVE] = self.ui.buildMergedArchive.isChecked()
        context.settings[Setting.FACE_DATA] = self.ui.faceData.isChecked()
        context.settings[Setting.VOICE_DATA] = self.ui.voiceData.isChecked()
        context.settings[Setting.BILLBOARD_DATA] = self.ui.billboardData.isChecked()
        context.settings[Setting.STRINGS_DATA] = self.ui.stringFiles.isChecked()
        context.settings[Setting.TRANSLATIONS_DATA] = self.ui.translations.isChecked()
        context.settings[Setting.INI_FILES_DATA] = self.ui.iniFiles.isChecked()
        context.settings[Setting.DIALOGS_DATA] = self.ui.dialogViews.isChecked()
        context.settings[Setting.GENERAL_ASSETS] = self.ui.generalAssets.isChecked()
        context.settings[Setting.ZEDIT_FOLDER] = self.ui.zeditPathEdit.text()
        context.settings[Setting.PROFILENAME_TEMPLATE] = self.ui.profileNameTemplate.text()
        context.settings[Setting.MODNAME_TEMPLATE] = self.ui.modNameTemplate.text()
        context.settings[Setting.HIDING_METHOD] = self.ui.hidePluginsGroup.checkedId()
        context.settings[Setting.MERGE_METHOD] = self.ui.mergeMethodGroup.checkedId()
        context.settings[Setting.ARCHIVE_ACTION] = self.ui.archiveActionGroup.checkedId()
        context.settings[Setting.MERGE_ORDER] = self.ui.savingMergesGroup.checkedId()
        context.settings[Setting.ZEDIT_PROFILE] = self.ui.zeditProfile.currentText()

    def showFileDialog(self):
        dirName = QFileDialog.getExistingDirectory(
            self, self.tr("zEdit Directory"), self.ui.zeditPathEdit.text(), QFileDialog.ShowDirsOnly
        )
        if dirName:
            self.ui.zeditPathEdit.setText(dirName)
        self.validateZEditPath()

    def validateZEditPath(self):
        v = Validator.folder("zedit.exe")
        if v.validate(self.ui.zeditPathEdit.text(), None):
            self.ui.zeditPathError.setVisible(False)
            self.updateProfilesList()
        else:
            self.ui.zeditPathError.setVisible(True)

    def updateProfilesList(self):
        self.ui.zeditProfile.clear()
        zEditFolder = self.ui.zeditPathEdit.text()
        if not zEditFolder:
            return
        self.profiles = ZEditConfig.getProfiles(self.gameName, zEditFolder)
        for i in range(len(self.profiles)):
            name = self.profiles[i].profileName
            self.ui.zeditProfile.addItem(name, i)
            if name == self.zeditProfile:
                self.ui.zeditProfile.setCurrentIndex(i)
        if self.ui.zeditProfile.currentIndex() < 0:
            self.ui.zeditProfileError.setVisible(True)
        else:
            self.ui.zeditProfileError.setVisible(False)

    def onReloadData(self):
        pass
