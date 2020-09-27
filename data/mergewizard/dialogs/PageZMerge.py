from PyQt5.QtCore import QDir, qInfo, QVariant
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QWidget, QComboBox
from mergewizard.dialogs.WizardPage import WizardPage
from mergewizard.domain.Context import Context
from mergewizard.domain.merge.ZEditConfig import ZEditConfig
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

        # error indicators
        self.ui.warningIcon.setPixmap(QPixmap(Icon.ERROR))
        self.ui.warningFrame.setVisible(False)
        self.ui.profileError.setPixmap(QPixmap(Icon.ERROR))
        self.ui.pluginNameError.setPixmap(QPixmap(Icon.ERROR))
        self.ui.modNameError.setPixmap(QPixmap(Icon.ERROR))

        self.setZMergeProfileError()
        self.setPluginNameError()
        self.setModNameError()

        self.ui.modName.setEditable(True)
        self.ui.modName.setInsertPolicy(QComboBox.InsertAtTop)
        self.ui.pluginName.textChanged.connect(lambda: self.validatePluginName())
        self.ui.zmergeProfile.currentIndexChanged.connect(self.loadMergeNames)
        self.ui.modName.currentIndexChanged.connect(self.loadMergeFile)
        self.context.settingChanged.connect(self.settingChanged)

    def initializePage(self):
        self.initializeZEditPath()
        self.loadProfiles()
        self.initializeMOProfileName()
        self.initializeNames()
        self.validatePanel()

    def isOkToExit(self):
        self.context.setSetting("lastZMergeProfile", self.ui.zmergeProfile.currentText())
        return True

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

    def initializeMOProfileName(self):
        # TODO: If we allow creating merges to other MO profile, change this.
        # For now this is okay.
        self.ui.moProfile.setText(self.context.profile.currentProfileName())

    def loadProfiles(self):
        """ This is called whenever the Wizard moves forward to this page and whenever the
        zEdit folder changes in Settings """

        self.profiles = ZEditConfig.getProfiles(self.context.profile.gameName(), self.zEditFolder)
        self.ui.zmergeProfile.clear()
        for i in range(len(self.profiles)):
            name = self.profiles[i].profileName
            self.ui.zmergeProfile.addItem(name, i)
            if name == self.lastProfile:
                self.ui.zmergeProfile.setCurrentIndex(i)

    def loadMergeNames(self, profileRow: int):
        """ Fills in the modName combobox with the mod names from the selected profile.
        This is called by the change signal from the profile combob box """

        self.ui.modName.clear()
        if self.profiles[profileRow].merges:
            self.ui.modName.insertSeparator(0)

        selectedMerge = self.context.mergeModel.selectedMergeName()
        for i in range(len(self.profiles[profileRow].merges)):
            mergeName = self.profiles[profileRow].merges[i].name
            self.ui.modName.addItem(mergeName, i)
            if mergeName == selectedMerge:
                self.ui.modName.setCurrentIndex(self.ui.modName.count() - 1)

    def loadMergeFile(self, modNameRow: int):
        """ Sets the name of the plugin (it it can) and loads the merge view.
        This is called by the change signal from the modName combo box """

        currentMerge = self.ui.modName.currentData()
        if currentMerge is None:
            self.calculateNewPluginName()
            return
        currentProfile = self.ui.zmergeProfile.currentData()
        if currentProfile is not None:
            self.ui.pluginName.setText(self.profiles[currentProfile].merges[currentMerge].filename)

    def calculateNewPluginName(self):
        self.ui.pluginName.clear()

    def initializeNames(self):
        selectedMerge = self.context.dataCache.mergeModel.selectedMergeName()
        # self.ui.modName.setText(selectedMerge)

    def settingChanged(self, setting: int):
        if setting == Setting.ZEDIT_FOLDER:
            self.zEditFolder = self.context.zEditFolder
            self.initializeZMergeProfile()
        if setting == Setting.PROFILENAME_TEMPLATE:
            self.initializeNames()
        if setting == Setting.MODNAME_TEMPLATE:
            self.initializeNames()

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
        self.validatePluginName()
        self.validateModName()

    def validateZMergeProfile(self):
        if self.ui.zmergeProfile.currentIndex() < 0:
            self.setZMergeProfileError("Unable to find a zMerge profile for this game.")
        else:
            self.setZMergeProfileError()

    def validatePluginName(self):
        if not self.ui.pluginName.text():
            self.setPluginNameError("Plugin name cannot be empty.")
        else:
            self.setPluginNameError()

    def validateModName(self):
        pass

