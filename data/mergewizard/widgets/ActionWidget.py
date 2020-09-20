from typing import List
from enum import Enum, auto
from PyQt5.QtCore import Qt, QSize, qInfo
from PyQt5.QtWidgets import QWidget, QHeaderView

from mergewizard.models.PluginModel import PluginModel
from mergewizard.models.ActionModel import ActionModel
from mergewizard.models.LogModel import LogModel, LogFilterModel
from mergewizard.widgets.Splitter import Splitter
from mergewizard.widgets.CheckableHeader import CheckableHeader
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

    def initialize(self, currentProfile: str, profiles: List[str]):
        """ Called from the wizard page with the data needed to setup
        the profile lists.It also signals updating warning panels """
        self.setCurrentProfile(currentProfile)
        self.setProfileList(profiles)
        self.conditionallyShowWarningFrame()
        self.ui.profileName.clear()
        self.ui.profileError.setVisible(False)
        self.validatePanel()

    def setProfileList(self, profiles: List[str]):
        idx = next((i for i in range(len(profiles)) if profiles[i] == self.currentProfile), -1)
        if idx > -1:
            profiles.pop(idx)
        self.ui.profileBox.clear()
        self.profiles = [self.tr("(Current) {}".format(self.currentProfile))]
        self.profiles.extend(profiles)
        self.profiles.append(self.tr("Create new profile ..."))
        self.ui.profileBox.addItems(self.profiles)
        self.ui.profileBox.setItemData(0, self.ProfileType.Current)
        self.ui.profileBox.setItemData(self.ui.profileBox.count() - 1, self.ProfileType.New)
        self.ui.profileName.setEnabled(False)

    def setCurrentProfile(self, profile: str):
        self.currentProfile = profile

    def conditionallyShowWarningFrame(self):
        self.ui.warningFrame.setVisible(self.pluginModel.missingPluginsAreSelected())

    def selectedProfileName(self) -> str:
        idx = self.ui.profileBox.currentIndex()
        if idx == 0:
            return self.currentProfile
        if idx == self.ui.profileBox.count() - 1:
            return self.ui.profileName.text()
        return self.ui.profileBox.currentText()

    def onProfileSelectionChanged(self, index):
        idx = self.ui.profileBox.currentIndex()
        self.ui.profileName.setEnabled(idx == self.ui.profileBox.count() - 1)
        self.validatePanel()

    def onNewProfileName(self):
        text = self.ui.profileName.text().lower()
        bad = text == self.currentProfile.lower()
        if not bad:
            bad = next((i for i in range(len(self.profiles)) if self.profiles[i].lower() == text), -1) != -1
        if bad:
            self.ui.profileError.setText(self.tr("* Existing profile"))
        self.ui.profileError.setVisible(bad)
        self.validatePanel()

    def validatePanel(self):
        bad = (
            not self.selectedProfileName()
            or self.actionModel().isNoneEnabled()
            or self.ui.profileError.isVisible()
            or self.pluginModel.selectedCount() == 0
        )
        self.ui.applyButton.setDisabled(bad)
