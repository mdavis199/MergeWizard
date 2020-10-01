from PyQt5.QtCore import QDir, QVariant, Qt, qInfo
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QWidget, QComboBox, QHeaderView
from mergewizard.dialogs.WizardPage import WizardPage
from mergewizard.domain.Context import Context
from mergewizard.domain.merge.MergeFile import MergeFile
from mergewizard.domain.merge.ZEditConfig import ZEditConfig
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
        # zedit configuration including merges(mods) from current profile
        self.zEditFolder = None
        self.zEditProfile = None
        self.profile = None
        # calculated names for new mods
        self.newPluginName = ""
        self.newModName = ""

        # error indicators
        self.ui.warningIcon.setPixmap(QPixmap(Icon.ERROR))
        self.ui.warningFrame.setVisible(False)
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
        self.context.settings.settingChanged.connect(self.settingChanged)
        self.ui.modName.currentTextChanged.connect(lambda: self.loadMergeFile())
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
    def currentMerge(self):
        return self.ui.modName.currentData()

    def initializePage(self):
        self.initializeMOProfileName()
        self.validateZMergeProfile()
        self.loadMerges()
        self.calculateNewNames()
        self.loadOriginalConfig()

    def isOkToExit(self):
        return True

    def settingChanged(self, setting: int):
        if setting == Setting.ZEDIT_FOLDER:
            self.validateZMergeProfile()
            self.loadMerges()
        if setting == Setting.ZEDIT_PROFILE:
            self.validateZMergeProfile()
            self.loadMerges()
        if setting == Setting.PROFILENAME_TEMPLATE:
            self.initializeNames()
        if setting == Setting.MODNAME_TEMPLATE:
            self.initializeNames()

    def initializeMOProfileName(self):
        # TODO: If we allow creating merges to other MO profile, change this.
        # For now this is okay.
        self.ui.moProfile.setText(self.context.profile.currentProfileName())

    def isNewMerge(self):
        return self.context.mergeModel.isSelectedMergeNew()

    def loadMerges(self):
        """ Fills in the modName combobox with the mod names from the selected profile.
        """
        self.zEditFolder = self.context.settings[Setting.ZEDIT_FOLDER]
        self.zEditProfile = self.context.settings[Setting.ZEDIT_PROFILE]
        self.profile = None
        self.ui.modName.clear()
        if not self.zEditFolder or not self.zEditProfile:
            return
        self.profile = ZEditConfig.getMerges(self.context.profile.gameName(), self.zEditProfile, self.zEditFolder)
        if not self.profile:
            return

        self.ui.modName.insertSeparator(0)
        selectedMergeName = self.context.mergeModel.selectedMergeName()
        for i in range(len(self.profile.merges)):
            mergeName = self.profile.merges[i].name
            self.ui.modName.addItem(mergeName, i)
            if mergeName == selectedMergeName:
                self.ui.modName.setCurrentIndex(self.ui.modName.count() - 1)
        if self.isNewMerge():
            self.ui.modName.setCurrentText(self.newModName)

    def loadMergeFile(self):
        """ Sets the name of the plugin (it it can) and loads the merge view.
        This is called by the change signal from the modName combo box """

        currentMerge = self.ui.modName.currentData()  # None ==> new merge
        if currentMerge is not None:
            self.ui.pluginName.setText(self.profile.merges[currentMerge].filename)
        else:
            self.ui.pluginName.setText(self.newPluginName)

    def calculateNewNames(self):
        self.calculateNewPluginName()
        self.calculateNewModName()

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

    def initializeNames(self):
        selectedMerge = self.context.dataCache.mergeModel.selectedMergeName()
        # self.ui.modName.setText(selectedMerge)

    def loadOriginalConfig(self):
        pass

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

