from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import QDir, QFile, QFileInfo, QDirIterator

from mergewizard.dialogs.WizardPage import WizardPage
from mergewizard.domain.Context import Context
from mergewizard.views.PluginViewFactory import PluginViewFactory, ViewType
from mergewizard.widgets.Splitter import Splitter
from mergewizard.domain.Profile import Profile
from .ui.PageApplyChanges import Ui_PageApplyChanges


class PageApplyChanges(WizardPage):
    def __init__(self, context: Context, parent: QWidget = None):
        super().__init__(parent)
        self.ui = Ui_PageApplyChanges()
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
        self.ui.actionWidget.setProfile(Profile(context.organizer))

    def initializePage(self):
        # this is called whenever the wizard moves forward to this page.
        # We use it to ensure the action widget reflects changes made in the plugin selection
        self.ui.actionWidget.initialize()

    def isOkToExit(self):
        return True
