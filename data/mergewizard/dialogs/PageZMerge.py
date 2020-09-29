from PyQt5.QtCore import QDir, QVariant, Qt
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QWidget, QComboBox, QHeaderView
from mergewizard.dialogs.WizardPage import WizardPage
from mergewizard.domain.Context import Context
from mergewizard.domain.merge.ZEditConfig import ZEditConfig
from mergewizard.domain.merge.MergeFile import MergeFile
from mergewizard.models.MergeFileModel import MergeFileModel
from mergewizard.widgets.ComboBoxDelegate import ComboBoxDelegate
from mergewizard.constants import Setting, Icon
from .ui.PageZMerge import Ui_PageZMerge


class PageZMerge(WizardPage):
    def __init__(self, context: Context, parent: QWidget = None):
        super().__init__(parent)
        self.ui = Ui_PageZMerge()
        self.ui.setupUi(self)
        self.context = context
        self.profiles = []
        self.zEditFolder = ""
        self.lastProfile = context.getSetting("lastZMergeProfile", QVariant.String, "")
        self.newPluginName = ""
        self.newModName = ""

        # error indicators
        self.ui.warningIcon.setPixmap(QPixmap(Icon.ERROR))
        self.ui.warningFrame.setVisible(False)
        self.ui.profileError.setPixmap(QPixmap(Icon.ERROR))
        self.ui.pluginNameError.setPixmap(QPixmap(Icon.ERROR))
        self.ui.modNameError.setPixmap(QPixmap(Icon.ERROR))

        # button
        self.ui.applyButton.setIcon(QIcon(Icon.SAVE))
        self.ui.launchButton.setIcon(QIcon(Icon.LAUNCH))

        # name panel
        self.ui.modName.setEditable(True)
        self.ui.modName.setInsertPolicy(QComboBox.InsertAtTop)

        self.validatePanel()

        # signals
        self.context.settingChanged.connect(self.settingChanged)
        self.ui.zMergeProfile.currentTextChanged.connect(lambda: self.loadMergeNames())
        self.ui.modName.currentTextChanged.connect(lambda: self.loadMergeFile())

        self.ui.zMergeProfile.currentTextChanged.connect(lambda: self.validateZMergeProfile())
        self.ui.modName.currentTextChanged.connect(lambda: self.validateModName())
        self.ui.pluginName.textChanged.connect(lambda: self.validatePluginName())

        # zMerge Views
        self.ui.zMergeConfigView.setModel(MergeFileModel())
        self.ui.zMergeConfigView.header().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.ui.zMergeConfigView.setItemDelegateForColumn(1, ComboBoxDelegate(self))

        self.ui.originalConfigView.setModel(MergeFileModel())
        self.ui.originalConfigView.header().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.ui.originalConfigView.model().isEditable = False

    @property
    def currentProfile(self):
        return self.ui.zMergeProfile.currentData()

    @property
    def currentMerge(self):
        return self.ui.modName.currentData()

    def initializePage(self):
        self.initializeMOProfileName()
        self.calculateNewNames()
        self.initializeZEditPath()
        self.loadOriginalConfig()

    def isOkToExit(self):
        self.context.setSetting("lastZMergeProfile", self.ui.zMergeProfile.currentText())
        return True

    def settingChanged(self, setting: int):
        if setting == Setting.ZEDIT_FOLDER:
            self.zEditFolder = self.context.zEditFolder
            self.initializeZEditPath()
        if setting == Setting.PROFILENAME_TEMPLATE:
            self.initializeNames()
        if setting == Setting.MODNAME_TEMPLATE:
            self.initializeNames()

    def initializeZEditPath(self):
        self.zEditFolder = self.context.zEditFolder
        if not self.zEditFolder:
            self.ui.warningFrame.setVisible(True)
        else:
            dir = QDir(self.context.zEditFolder)
            if dir.exists("zedit.exe"):
                self.ui.warningFrame.setVisible(False)
            else:
                self.ui.warningFrame.setVisible(True)
                self.zEditFolder = ""
        self.loadProfiles()

    def initializeMOProfileName(self):
        # TODO: If we allow creating merges to other MO profile, change this.
        # For now this is okay.
        self.ui.moProfile.setText(self.context.profile.currentProfileName())

    def isNewMerge(self):
        return self.context.mergeModel.isSelectedMergeNew()

    def loadProfiles(self):
        """ This is called whenever the Wizard moves forward to this page and whenever the
        zEdit folder changes in Settings """

        self.ui.zMergeProfile.clear()
        if not self.zEditFolder:
            return
        self.profiles = ZEditConfig.getProfiles(self.context.profile.gameName(), self.zEditFolder)
        for i in range(len(self.profiles)):
            name = self.profiles[i].profileName
            self.ui.zMergeProfile.addItem(name, i)
            if name == self.lastProfile:
                self.ui.zMergeProfile.setCurrentIndex(i)

    def loadMergeNames(self):
        """ Fills in the modName combobox with the mod names from the selected profile.
        This is called by the change signal from the profile combobox """

        self.ui.modName.clear()
        profileRow = self.ui.zMergeProfile.currentData()
        if profileRow is None:
            return

        if self.profiles[profileRow].merges:
            self.ui.modName.insertSeparator(0)

        selectedMergeName = self.context.mergeModel.selectedMergeName()
        for i in range(len(self.profiles[profileRow].merges)):
            mergeName = self.profiles[profileRow].merges[i].name
            self.ui.modName.addItem(mergeName, i)
            if mergeName == selectedMergeName:
                self.ui.modName.setCurrentIndex(self.ui.modName.count() - 1)
        if self.isNewMerge():
            self.ui.modName.setCurrentText(self.newModName)

    def loadMergeFile(self):
        """ Sets the name of the plugin (it it can) and loads the merge view.
        This is called by the change signal from the modName combo box """

        currentMerge = self.ui.modName.currentData()
        currentProfile = self.ui.zMergeProfile.currentData()
        if currentProfile is not None and currentMerge is not None:
            self.ui.pluginName.setText(self.profiles[currentProfile].merges[currentMerge].filename)
        else:
            self.ui.pluginName.setText(self.newPluginName)

    def calculateNewNames(self):
        self.calculateNewPluginName()
        self.calculateNewModName()

    def calculateNewModName(self):
        self.newModName = ""
        if not self.context.modNameTemplate or self.newPluginName == "":
            return

        basename = self.newPluginName[:-4]
        parts = self.context.modNameTemplate.split("$", 1)

        if len(parts) < 2:
            # the template has not "$"
            self.newModName = self.context.modNameTemplate
        else:
            self.newModName = parts[0] + basename + parts[1]

    def calculateNewPluginName(self):
        # Does zMerge always use esp extension?
        EXT = ".esp"
        self.newPluginName = ""
        if not self.context.profileNameTemplate:
            return
        basename = self.ui.moProfile.text()
        parts = self.context.profileNameTemplate.split("$", 1)
        if len(parts) < 2:
            # The template has not "$"
            self.newPluginName = self.context.profileNameTemplate
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

    def initializeNames(self):
        selectedMerge = self.context.dataCache.mergeModel.selectedMergeName()
        # self.ui.modName.setText(selectedMerge)

    def loadOriginalConfig(self):
        pass

    # ----
    # ---- Convenient Accessors
    # ----

    # ----
    # ---- Validation and Error handling
    # ----

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

    def validatePanel(self):
        self.validateZMergeProfile()
        self.validateModName()
        self.validatePluginName()

    def validateZMergeProfile(self):
        if self.ui.zMergeProfile.currentIndex() < 0:
            self.setZMergeProfileError("Unable to find a zMerge profile for this game.")
        else:
            self.setZMergeProfileError()

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

