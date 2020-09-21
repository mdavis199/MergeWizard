from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import QDir, QFile, QFileInfo, QDirIterator

from mergewizard.dialogs.WizardPage import WizardPage
from mergewizard.domain.Context import Context
from mergewizard.views.PluginViewFactory import PluginViewFactory, ViewType
from mergewizard.widgets.Splitter import Splitter
from .ui.PageReviewMasters import Ui_PageReviewMasters


class PageReviewMasters(WizardPage):
    def __init__(self, context: Context, parent: QWidget = None):
        super().__init__(parent)
        self.ui = Ui_PageReviewMasters()
        self.ui.setupUi(self)
        self.context = context
        self.profilesDir = None
        self.profiles = []

        PluginViewFactory.configureView(ViewType.Masters, self.ui.masterPlugins, context.pluginModel)
        PluginViewFactory.configureView(ViewType.SelectedNoEdit, self.ui.selectedPlugins, context.pluginModel)

        Splitter.decorate(self.ui.verticalSplitter)
        Splitter.decorate(self.ui.topSplitter)
        self.ui.verticalSplitter.setStretchFactor(0, 100)
        self.ui.verticalSplitter.setStretchFactor(1, 1)
        self.ui.actionWidget.setPluginModel(context.pluginModel)

    def initializePage(self):
        self.ui.actionWidget.initialize(self.currentProfile(), self.buildProfileList())

    def isOkToExit(self):
        return True

    def currentProfile(self):
        return self.context.organizer.profileName()

    def buildProfileList(self):
        self.profiles.clear()
        currentPath = QFileInfo(self.context.organizer.profile().absolutePath())
        self.profilesDir = currentPath.dir().absolutePath()
        infos = QDir(currentPath.absolutePath(), "", QDir.IgnoreCase, QDir.NoDotAndDotDot | QDir.Dirs).entryInfoList()
        for info in infos:
            self.profiles.append(info.baseName())
        return self.profiles
