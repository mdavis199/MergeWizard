from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QWidget, QDialog, QFileDialog
from mergewizard.domain.Context import Context, Validator
from mergewizard.domain.Settings import Settings
from mergewizard.domain.merge.ZEditConfig import ZEditConfig
from mergewizard.constants import Setting, Icon
from .ui.SettingsDialog import Ui_SettingsDialog


class SettingsDialog(QDialog):
    def __init__(self, context: Context, parent: QWidget = None):
        super().__init__(parent)
        self.ui = Ui_SettingsDialog()
        self.ui.setupUi(self)
        self._changedSettings = []

        self.settings = context.settings
        self.gameName = context.profile.gameName()
        self.zeditProfile = None

        self.ui.zeditPathError.setPixmap(QPixmap(Icon.ERROR))
        self.ui.zeditProfileError.setPixmap(QPixmap(Icon.ERROR))
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

    def loadSettings(self):
        self.zeditProfile = self.settings[Setting.ZEDIT_PROFILE]

        # check boxes
        self.ui.enableHiding.setChecked(self.settings[Setting.ENABLE_HIDING_PLUGINS])
        self.ui.enableZMerge.setChecked(self.settings[Setting.ENABLE_ZMERGE_INTEGRATION])
        self.ui.enableLoadingZMerge.setChecked(self.settings[Setting.ENABLE_LOADING_ZMERGE])
        self.ui.excludeInactiveMods.setChecked(self.settings[Setting.EXCLUDE_INACTIVE_MODS])
        self.ui.useGameLoadOrder.setChecked(self.settings[Setting.USE_GAME_LOADORDER])
        self.ui.buildMergedArchive.setChecked(self.settings[Setting.BUILD_MERGED_ARCHIVE])
        self.ui.faceData.setChecked(self.settings[Setting.FACE_DATA])
        self.ui.voiceData.setChecked(self.settings[Setting.VOICE_DATA])
        self.ui.billboardData.setChecked(self.settings[Setting.BILLBOARD_DATA])
        self.ui.stringFiles.setChecked(self.settings[Setting.STRINGS_DATA])
        self.ui.translations.setChecked(self.settings[Setting.TRANSLATIONS_DATA])
        self.ui.iniFiles.setChecked(self.settings[Setting.INI_FILES_DATA])
        self.ui.dialogViews.setChecked(self.settings[Setting.DIALOGS_DATA])
        self.ui.generalAssets.setChecked(self.settings[Setting.GENERAL_ASSETS])

        # text edit fields
        self.ui.zeditPathEdit.setText(self.settings[Setting.ZEDIT_FOLDER])
        self.ui.profileNameTemplate.setText(self.settings[Setting.PROFILENAME_TEMPLATE])
        self.ui.modNameTemplate.setText(self.settings[Setting.MODNAME_TEMPLATE])

        # radio buttons
        self.ui.hidePluginsGroup.button(self.settings[Setting.HIDING_METHOD]).setChecked(True)
        self.ui.mergeMethodGroup.button(self.settings[Setting.MERGE_METHOD]).setChecked(True)
        self.ui.archiveActionGroup.button(self.settings[Setting.ARCHIVE_ACTION]).setChecked(True)
        self.ui.savingMergesGroup.button(self.settings[Setting.MERGE_ORDER]).setChecked(True)

    def storeSettings(self):
        self.settings.settingChanged.connect(self.onSettingChanged)
        self.settings[Setting.ENABLE_HIDING_PLUGINS] = self.ui.enableHiding.isChecked()
        self.settings[Setting.ENABLE_ZMERGE_INTEGRATION] = self.ui.enableZMerge.isChecked()
        self.settings[Setting.ENABLE_LOADING_ZMERGE] = self.ui.enableLoadingZMerge.isChecked()
        self.settings[Setting.EXCLUDE_INACTIVE_MODS] = self.ui.excludeInactiveMods.isChecked()
        self.settings[Setting.USE_GAME_LOADORDER] = self.ui.useGameLoadOrder.isChecked()
        self.settings[Setting.BUILD_MERGED_ARCHIVE] = self.ui.buildMergedArchive.isChecked()
        self.settings[Setting.FACE_DATA] = self.ui.faceData.isChecked()
        self.settings[Setting.VOICE_DATA] = self.ui.voiceData.isChecked()
        self.settings[Setting.BILLBOARD_DATA] = self.ui.billboardData.isChecked()
        self.settings[Setting.STRINGS_DATA] = self.ui.stringFiles.isChecked()
        self.settings[Setting.TRANSLATIONS_DATA] = self.ui.translations.isChecked()
        self.settings[Setting.INI_FILES_DATA] = self.ui.iniFiles.isChecked()
        self.settings[Setting.DIALOGS_DATA] = self.ui.dialogViews.isChecked()
        self.settings[Setting.GENERAL_ASSETS] = self.ui.generalAssets.isChecked()
        self.settings[Setting.ZEDIT_FOLDER] = self.ui.zeditPathEdit.text()
        self.settings[Setting.PROFILENAME_TEMPLATE] = self.ui.profileNameTemplate.text()
        self.settings[Setting.MODNAME_TEMPLATE] = self.ui.modNameTemplate.text()
        self.settings[Setting.HIDING_METHOD] = self.ui.hidePluginsGroup.checkedId()
        self.settings[Setting.MERGE_METHOD] = self.ui.mergeMethodGroup.checkedId()
        self.settings[Setting.ARCHIVE_ACTION] = self.ui.archiveActionGroup.checkedId()
        self.settings[Setting.MERGE_ORDER] = self.ui.savingMergesGroup.checkedId()
        self.settings[Setting.ZEDIT_PROFILE] = self.ui.zeditProfile.currentText()
        self.settings.settingChanged.disconnect(self.onSettingChanged)

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

    # The settings on the first page impact the data shown in the view.
    # The second page is not critical.
    CRITICAL_SETTINGS = [
        Setting.ENABLE_HIDING_PLUGINS,
        Setting.HIDING_METHOD,
        Setting.ENABLE_ZMERGE_INTEGRATION,
        Setting.ZEDIT_FOLDER,
        Setting.ZEDIT_PROFILE,
        Setting.ENABLE_LOADING_ZMERGE,
        Setting.EXCLUDE_INACTIVE_MODS,
    ]

    def onSettingChanged(self, setting):
        if setting in self.CRITICAL_SETTINGS:
            self._changedSettings.append(setting)

    def changedSettings(self):
        return self._changedSettings
