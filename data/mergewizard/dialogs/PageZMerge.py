from copy import deepcopy
from PyQt5.QtCore import QDir, QVariant, Qt, qInfo, QEvent
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QWidget, QComboBox, QHeaderView
from mergewizard.dialogs.WizardPage import WizardPage
from mergewizard.domain.Context import Context
from mergewizard.domain.merge.MergeFile import MergeFile, PluginDesc
from mergewizard.domain.merge.ZEditConfig import ZEditConfig
from mergewizard.domain.MOLog import moDebug
from mergewizard.models.MergeFileModel import MergeFileModel, OptionRow as Option
from mergewizard.widgets.Splitter import Splitter
from mergewizard.widgets.VisibilityWatcher import VisibilityWatcher
from mergewizard.constants import Setting, Icon
from .ui.PageZMerge import Ui_PageZMerge


class PageZMerge(WizardPage):
    def __init__(self, context: Context, parent: QWidget = None):
        super().__init__(parent)
        self.ui = Ui_PageZMerge()
        self.ui.setupUi(self)
        self.context = context

        # The mergeFile from the profile setup by the previous pages
        self.mergeFile = None
        # zedit configuration including merges(mods) from current profile
        self.zEditFolder = None
        self.zEditProfile = None
        self.profile = None
        # calculated names for new mods
        self.newPluginName = ""
        self.newModName = ""

        # ----
        # ---- Finish setting up ui
        # ----

        # Icons
        self.ui.warningFrame.setVisible(False)
        self.ui.warningIcon.setPixmap(QPixmap(Icon.ERROR))
        self.ui.pluginNameError.setPixmap(QPixmap(Icon.ERROR))
        self.ui.modNameError.setPixmap(QPixmap(Icon.ERROR))
        self.ui.applyButton.setIcon(QIcon(Icon.SAVE))
        self.ui.launchButton.setIcon(QIcon(Icon.LAUNCH))
        self.ui.toggleOriginal.setIcon(QIcon(Icon.VIEW))

        # name panel
        self.ui.modName.setEditable(True)
        self.ui.modName.setInsertPolicy(QComboBox.NoInsert)

        self.validatePanel()

        # zMerge Views
        Splitter.decorate(self.ui.splitter)
        self.ui.zMergeConfigView.setModel(MergeFileModel())
        self.ui.zMergeConfigView.header().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.ui.zMergeConfigView.header().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.ui.zMergeConfigView.header().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.ui.zMergeConfigView.header().setVisible(False)
        self.ui.originalConfigView.setModel(MergeFileModel())
        self.ui.originalConfigView.header().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.ui.originalConfigView.header().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.ui.originalConfigView.header().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.ui.originalConfigView.header().setVisible(False)
        self.ui.originalBox.setVisible(False)

        # option groups
        self.ui.methodGroup.setId(self.ui.clobber, 0)
        self.ui.methodGroup.setId(self.ui.clean, 1)
        self.ui.archiveGroup.setId(self.ui.extract, 0)
        self.ui.archiveGroup.setId(self.ui.copy, 1)
        self.ui.archiveGroup.setId(self.ui.ignore, 2)

        # ----
        # ---- Signals
        # ----
        self.ui.useGameLoadOrder.clicked.connect(
            lambda: self.ui.zMergeConfigView.model().setOption(
                Option.UseGameLoadOrder, self.ui.useGameLoadOrder.isChecked()
            )
        )
        self.ui.buildMergedArchive.clicked.connect(
            lambda: self.ui.zMergeConfigView.model().setOption(
                Option.BuildArchive, self.ui.buildMergedArchive.isChecked()
            )
        )
        self.ui.methodGroup.buttonClicked.connect(
            lambda btn: self.ui.zMergeConfigView.model().setOption(Option.Method, btn.text())
        )
        self.ui.archiveGroup.buttonClicked.connect(
            lambda btn: self.ui.zMergeConfigView.model().setOption(Option.ArchiveAction, btn.text())
        )
        self.ui.faceData.clicked.connect(
            lambda: self.ui.zMergeConfigView.model().setOption(Option.HandleFaceData, self.ui.faceData.isChecked())
        )
        self.ui.voiceData.clicked.connect(
            lambda: self.ui.zMergeConfigView.model().setOption(Option.HandleVoiceData, self.ui.voiceData.isChecked())
        )
        self.ui.billboardData.clicked.connect(
            lambda: self.ui.zMergeConfigView.model().setOption(
                Option.HandleBillboards, self.ui.billboardData.isChecked()
            )
        )
        self.ui.stringFiles.clicked.connect(
            lambda: self.ui.zMergeConfigView.model().setOption(
                Option.HandleStringFiles, self.ui.stringFiles.isChecked()
            )
        )
        self.ui.translations.clicked.connect(
            lambda: self.ui.zMergeConfigView.model().setOption(
                Option.HandleTranslations, self.ui.translations.isChecked()
            )
        )
        self.ui.iniFiles.clicked.connect(
            lambda: self.ui.zMergeConfigView.model().setOption(Option.HandleIniFiles, self.ui.iniFiles.isChecked())
        )
        self.ui.dialogViews.clicked.connect(
            lambda: self.ui.zMergeConfigView.model().setOption(
                Option.HandleDialogViews, self.ui.dialogViews.isChecked()
            )
        )
        self.ui.generalAssets.clicked.connect(
            lambda: self.ui.zMergeConfigView.model().setOption(
                Option.CopyGeneralAssets, self.ui.generalAssets.isChecked()
            )
        )
        self.ui.modName.editTextChanged.connect(self.onModNameEdited)
        self.ui.modName.currentTextChanged.connect(lambda x: self.setModName(x))
        self.ui.pluginName.textEdited.connect(lambda x: self.ui.zMergeConfigView.model().setPluginName(x))
        self.ui.pluginName.textChanged.connect(lambda x: self.ui.pluginNameError.setVisible(not x))

        self.ui.launchButton.clicked.connect(self.launchZMerge)
        self.ui.applyButton.clicked.connect(self.saveChanges)
        self.ui.toggleOriginal.clicked.connect(self.toggleOriginalConfig)

        # disable the save changes button if any of the error indicators are showing
        visibilityWatcher = VisibilityWatcher(self)
        visibilityWatcher.add([self.ui.warningFrame, self.ui.modNameError, self.ui.pluginNameError])
        visibilityWatcher.visibilityChanged.connect(lambda x: self.ui.applyButton.setEnabled(not x))

    # ----
    # ---- Initialization
    # ----

    def initializePage(self):
        self.initializeMOProfileName()
        self.validateZMergeProfile()
        self.loadZEditProfile()
        self.loadMergeFile()

    def initializeMOProfileName(self):
        # TODO: If we allow creating merges to other MO profile, change this. For now this is okay.
        self.ui.moProfile.setText(self.context.profile.currentProfileName())

    def loadZEditProfile(self):
        """ Retrieves all the merge configuration from the zedit "merges.json" """
        self.zEditFolder = self.context.settings[Setting.ZEDIT_FOLDER]
        self.zEditProfile = self.context.settings[Setting.ZEDIT_PROFILE]
        self.profile = None
        if not self.zEditFolder or not self.zEditProfile:
            return
        self.profile = ZEditConfig.loadProfile(self.context.profile.gameName(), self.zEditProfile, self.zEditFolder)

    def loadMergeFile(self):
        self.ui.modName.clear()
        if self.context.mergeModel.isCurrentMergeNew():
            self.calculateNewNames()
            mf = self.createMergeFile()
            mf.filename = self.newPluginName
            mf.name = self.newModName
            self.ui.toggleOriginal.setEnabled(False)
            self.ui.originalBox.setVisible(False)
        else:
            original = self.context.mergeModel.currentMergeFile()
            mf = deepcopy(original)
            self.ui.originalConfigView.model().setMergeFile(original)
            self.ui.originalConfigView.expandAll()
            self.ui.toggleOriginal.setEnabled(True)
            self.ui.originalBox.setTitle(self.tr("Original: {}".format(mf.name)))
            self.ui.modName.addItem(mf.name, 0)
        self.setModName(mf.name)
        self.setOptionsFromMergeFile(mf)
        self.setLoadOrder(mf)
        self.setPlugins(mf)
        self.mergeFile = mf
        self.ui.zMergeConfigView.model().setMergeFile(mf)
        # self.ui.zMergeConfigView.header().resizeSections(QHeaderView.ResizeToContents)
        self.ui.zMergeConfigView.resizeColumnToContents(2)
        self.ui.zMergeConfigView.expandAll()

    def createMergeFile(self):
        m = MergeFile()
        m.useGameLoadOrder = self.context.settings[Setting.USE_GAME_LOADORDER]
        m.buildMergedArchive = self.context.settings[Setting.BUILD_MERGED_ARCHIVE]
        m.method = self.ui.methodGroup.button(self.context.settings[Setting.MERGE_METHOD]).text()
        m.archiveAction = self.ui.archiveGroup.button(self.context.settings[Setting.ARCHIVE_ACTION]).text()
        m.handleFaceData = self.context.settings[Setting.FACE_DATA]
        m.handleVoiceData = self.context.settings[Setting.VOICE_DATA]
        m.handleBillboards = self.context.settings[Setting.BILLBOARD_DATA]
        m.handleStringFiles = self.context.settings[Setting.STRINGS_DATA]
        m.handleTranslations = self.context.settings[Setting.TRANSLATIONS_DATA]
        m.handleIniFiles = self.context.settings[Setting.INI_FILES_DATA]
        m.handleDialogViews = self.context.settings[Setting.DIALOGS_DATA]
        m.copyGeneralAssets = self.context.settings[Setting.GENERAL_ASSETS]
        m.isNew = True
        return m

    def setOptionsFromMergeFile(self, mf: MergeFile):
        self.ui.useGameLoadOrder.setChecked(mf.useGameLoadOrder)
        self.ui.buildMergedArchive.setChecked(mf.buildMergedArchive)
        self.ui.clobber.setChecked(mf.method == "Clobber")
        if mf.archiveAction == "Extract":
            self.ui.extract.setChecked(True)
        elif mf.archiveAction == "Copy":
            self.ui.copy.setChecked(True)
        else:
            self.ui.ignore.setChecked(True)
        self.ui.faceData.setChecked(mf.handleFaceData)
        self.ui.voiceData.setChecked(mf.handleVoiceData)
        self.ui.billboardData.setChecked(mf.handleBillboards)
        self.ui.stringFiles.setChecked(mf.handleStringFiles)
        self.ui.translations.setChecked(mf.handleTranslations)
        self.ui.iniFiles.setChecked(mf.handleIniFiles)
        self.ui.dialogViews.setChecked(mf.handleDialogViews)
        self.ui.generalAssets.setChecked(mf.copyGeneralAssets)
        self.ui.modName.setCurrentText(mf.name)
        self.ui.pluginName.setText(mf.filename)

    def setLoadOrder(self, mf: MergeFile):
        mf.loadOrder = self.context.pluginModel.loadOrderNames()

    def setPlugins(self, mf: MergeFile):
        names = self.context.pluginModel.selectedPluginNames()
        paths = self.context.pluginModel.selectedPluginPaths()
        fds = []
        for i in range(len(names)):
            fds.append(PluginDesc(names[i], paths[i]))
        mf.plugins = fds

    # ----
    # ----
    # ----

    def onModNameEdited(self, text):
        if not text:
            self.setModNameError("Mod name cannot be empty.")
            return
        t = text.lower()
        currentMergeName = self.context.mergeModel.currentMergeName()
        if t == currentMergeName.lower():
            self.ui.modName.setCurrentIndex(0)
            self.setModNameError()
        else:
            idx = next((i for i in range(len(self.profile.merges)) if self.profile.merges[i].name.lower() == t), -1)
            if idx > -1:
                self.setModNameError("Merge already exists. Choose another name.")
            else:
                self.setModNameError()

    def setModName(self, text):
        self.ui.zMergeConfigView.model().setModName(text)
        if self.isNewMerge():
            self.ui.zMergeBox.setTitle(self.tr("New Merge: {}".format(text)))
        else:
            self.ui.zMergeBox.setTitle(self.tr("Merge: {}").format(text))

    def isNewMerge(self):
        return self.context.mergeModel.isCurrentMergeNew()

    def calculateNewNames(self):
        self.calculateNewPluginName()
        self.calculateNewModName()

    def calculateNewPluginName(self):
        # Does zMerge always use esp extension?
        EXT = ".esp"
        self.newPluginName = ""
        profileNameTemplate = self.context.settings[Setting.PROFILENAME_TEMPLATE]
        basename = self.ui.moProfile.text()
        parts = profileNameTemplate.split("$", 1)
        if len(parts) < 2:
            # The template has not "$"
            self.newPluginName = profileNameTemplate
            return

        len0 = len(parts[0])
        len1 = len(parts[1])

        if len1:
            if not basename.endswith(parts[1]):
                return
            else:
                basename = basename[:-len1]
        if len0:
            if not basename.startswith(parts[0]):
                return
        basename = basename[len0:]
        self.newPluginName = basename + EXT

    def calculateNewModName(self):
        self.newModName = ""
        modNameTemplate = self.context.settings[Setting.MODNAME_TEMPLATE]
        if not modNameTemplate or self.newPluginName == "":
            return

        basename = self.newPluginName[:-4]
        parts = modNameTemplate.split("$", 1)

        if len(parts) < 2:
            # the template has not "$"
            self.newModName = modNameTemplate
        else:
            self.newModName = parts[0] + basename + parts[1]

    def initializeNames(self):
        selectedMerge = self.context.dataCache.mergeModel.selectedMergeName()
        # self.ui.modName.setText(selectedMerge)

    def toggleOriginalConfig(self):
        self.ui.originalBox.setVisible(self.ui.toggleOriginal.isChecked())

    def launchZMerge(self):
        """ NOTE: We can use a different profile here """
        args = ['-appMode="merge"', '-profile="{}"'.format(self.context.settings[Setting.ZEDIT_PROFILE])]
        path = self.context.settings[Setting.ZEDIT_FOLDER] + "/zedit.exe"
        profile = ""
        handle = self.context.organizer.startApplication(path, args,)
        if handle < 0:
            return
        exitCode = self.context.organizer.waitForApplication(handle)
        moDebug(self.tr("zEdit exited with code {}").format(exitCode))

    def saveChanges(self):
        pass

    # ----
    # ---- How to handle changing settings
    # ----

    def settingChanged(self, setting: int):
        if setting == Setting.ZEDIT_FOLDER:
            self.validateZMergeProfile()
            self.loadProfile()
        if setting == Setting.ZEDIT_PROFILE:
            self.validateZMergeProfile()
            self.loadProfile()
        if setting == Setting.PROFILENAME_TEMPLATE:
            self.initializeNames()
        if setting == Setting.MODNAME_TEMPLATE:
            self.initializeNames()

    # ----
    # ---- Validation and Error handling
    # ----

    def setPluginNameError(self, msg=None):
        if msg:
            self.ui.pluginNameError.setToolTip(msg)
        self.ui.pluginNameError.setVisible(bool(msg))

    def setModNameError(self, msg=None):
        if msg:
            self.ui.modNameError.setToolTip(msg)
        self.ui.modNameError.setVisible(bool(msg))

    def validatePanel(self):
        self.validateModName()
        self.validatePluginName()

    def hasErrors(self):
        return (
            self.ui.warningFrame.isVisible() or self.ui.pluginNameError.isVisible() or self.ui.modNameError.isVisible()
        )

    def validateZMergeProfile(self):
        self.zEditFolder = self.context.settings[Setting.ZEDIT_FOLDER]
        if not self.zEditFolder:
            self.ui.warningLabel.setText(self.tr("Please update settings with the zEdit installation folder."))
            self.ui.warningFrame.setVisible(True)
            self.zEditProfile = None
        else:
            self.zEditProfile = self.context.settings[Setting.ZEDIT_PROFILE]
            if not self.zEditProfile:
                self.ui.warningLabel.setText(self.tr("Please update settings with the zEdit profile name."))
                self.ui.warningFrame.setVisible(True)
            else:
                self.ui.warningFrame.setVisible(False)

    def validateModName(self):
        if not self.ui.modName.currentText():
            self.setModNameError("Mod name cannot be empty.")
        else:
            self.setModNameError()

    def validatePluginName(self):
        if not self.ui.pluginName.text():
            self.setPluginNameError("Plugin name cannot be empty.")
        else:
            self.setPluginNameError()

