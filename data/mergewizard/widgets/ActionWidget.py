from typing import List
from enum import Enum, auto
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtWidgets import QWidget, QHeaderView

from mergewizard.models.PluginModel import PluginModel
from mergewizard.models.ActionModel import ActionModel
from mergewizard.models.LogModel import LogModel, LogFilterModel
from mergewizard.widgets.Splitter import Splitter
from mergewizard.widgets.CheckableHeader import CheckableHeader
from mergewizard.constants import Icon
from .ui.ActionWidget import Ui_ActionWidget


class ActionWidget(QWidget):
    class ProfileType(Enum):
        Current = auto()
        New = auto()

    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.ui = Ui_ActionWidget()
        self.ui.setupUi(self)
        self.pluginModel = None
        self.currentProfile = ""
        self.profiles = []

        # splitters
        Splitter.decorate(self.ui.splitter)
        self.ui.splitter.setStretchFactor(0, 1)
        self.ui.splitter.setStretchFactor(1, 1)
        self.ui.splitter.setSizes([500, 500])

        # error indicators
        self.ui.warningIcon.setPixmap(QPixmap(Icon.MISSING))
        self.ui.warningFrame.setVisible(False)
        self.ui.errorFrame.setVisible(False)
        self.ui.profileError.setVisible(False)

        # set up the log panel
        logModel = LogModel()
        logFilterModel = LogFilterModel()
        logFilterModel.setSourceModel(logModel)
        self.ui.logView.setModel(logFilterModel)
        self.ui.logView.resizeColumnToContents(0)
        self.ui.logView.setWordWrap(True)
        self.ui.logView.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)

        # set up the actions panel
        actionModel = ActionModel()
        actionModel.log.connect(logModel.log)
        self.ui.actionView.setModel(actionModel)

        actionHeader = CheckableHeader(parent=self)
        actionHeader.clicked.connect(actionModel.toggleAll)
        actionModel.headerDataChanged.connect(
            lambda: actionHeader.setCheckState(actionModel.headerData(0, Qt.Horizontal, Qt.CheckStateRole))
        )
        self.ui.actionView.setHorizontalHeader(actionHeader)
        actionHeader.setStretchLastSection(True)
        self.ui.actionView.resizeColumnToContents(0)

        # validate panel
        self.ui.profileBox.currentIndexChanged.connect(lambda x: self.onProfileSelectionChanged(x))
        self.ui.profileName.textChanged.connect(lambda: self.onNewProfileName())
        self.actionModel().headerDataChanged.connect(lambda: self.validatePanel())

        self.setActionViewSize()  # set the view height to fit all the rows
        self.ui.applyButton.clicked.connect(lambda x: self.applyActions())

    def setActionViewSize(self):
        h = self.ui.actionView.horizontalHeader().height() + 4
        for i in range(self.ui.actionView.model().rowCount()):
            h = h + self.ui.actionView.rowHeight(i)
        h = h + (self.ui.actionView.rowHeight(0) / 2)
        self.ui.actionView.setMinimumSize(QSize(0, h))

    def logModel(self):
        return self.ui.logView.model().sourceModel()

    def actionModel(self):
        self.logModel().clear()
        return self.ui.actionView.model()

    def showDebugMessages(self, show: bool):
        self.ui.logView.model().showDebugMessages(show)

    def setPluginModel(self, pluginModel: PluginModel):
        self.pluginModel = pluginModel
        pluginModel.log.connect(self.logModel().log)
        self.actionModel().setPluginModel(pluginModel)

    def applyActions(self):
        self.ui.logView.model().sourceModel().clear()
        self.ui.actionView.model().applyActions()

    def createLogContextMenu(self):
        pass

    # ----
    # ---- Methods relating to setting up the profile info
    # ----
    def initialize(self, currentProfile: str, profiles: List[str]):
        """ Called from the wizard page with the data needed to setup
        the profile lists."""
        self.setCurrentProfile(currentProfile)
        self.setProfileList(profiles)
        self.conditionallyShowWarningFrame()
        self.ui.profileName.clear()
        self.setProfileError()
        self.validatePanel()

    def setProfileList(self, profiles: List[str]):
        idx = next((i for i in range(len(profiles)) if profiles[i] == self.currentProfile), -1)
        if idx > -1:
            profiles.pop(idx)
        self.ui.profileBox.clear()
        self.profiles = [self.tr("{} (Current profile)".format(self.currentProfile)), self.tr("Create new profile ...")]
        self.profiles.extend(profiles)
        self.ui.profileBox.addItems(self.profiles)
        self.ui.profileBox.insertSeparator(2)
        self.ui.profileName.setEnabled(False)

    def setCurrentProfile(self, profile: str):
        self.currentProfile = profile

    def conditionallyShowWarningFrame(self):
        self.ui.warningFrame.setVisible(self.pluginModel.missingPluginsAreSelected())

    def selectedProfileName(self) -> str:
        if self.isCurrentProfile():
            return self.currentProfile
        if self.isNewProfile():
            return self.ui.profileName.text()
        return self.ui.profileBox.currentText()

    def onProfileSelectionChanged(self, index):
        if self.isNewProfile():
            self.ui.profileName.setEnabled(True)
            self.onNewProfileName()  # This will call validatePanel
        else:
            self.ui.profileName.setEnabled(False)
            self.setProfileError()
            self.validatePanel()

    def onNewProfileName(self):
        text = self.ui.profileName.text()
        if not text:
            self.setProfileError((self.tr("* Missing profile")))
        else:
            # This checks if the name is an existing profile. If it is,
            # it won't prevent validation, we just inform the user
            text = text.lower()
            bad = text == self.currentProfile.lower()
            if not bad:
                bad = next((i for i in range(len(self.profiles)) if self.profiles[i].lower() == text), -1) != -1
            if bad:
                self.setProfileError((self.tr("* Existing profile")))
            else:
                self.setProfileError()
        self.validatePanel()

    def validatePanel(self):
        bad = (
            not self.selectedProfileName()
            or self.actionModel().isNoneEnabled()
            or self.pluginModel.selectedCount() == 0
        )
        self.ui.applyButton.setDisabled(bad)

    def isNewProfile(self):
        return self.ui.profileBox.currentIndex() == 1

    def isCurrentProfile(self):
        return self.ui.profileBox.currentIndex() == 2

    def setProfileError(self, text=None):
        if not text:
            self.ui.profileError.setVisible(False)
        else:
            self.ui.profileError.setText(text)
            self.ui.profileError.setVisible(True)
