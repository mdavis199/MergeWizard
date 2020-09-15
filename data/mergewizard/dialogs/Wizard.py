from enum import IntEnum

from PyQt5.QtCore import pyqtSignal, Qt, QSize, QPoint, QVariant
from PyQt5.QtGui import QCloseEvent, QIcon, QKeySequence
from PyQt5.QtWidgets import QWidget, QWizard

from mobase import IOrganizer

from mergewizard.dialogs.PagePluginsSelect import PagePluginsSelect
from mergewizard.dialogs.PageReviewMasters import PageReviewMasters
from mergewizard.dialogs.SettingsDialog import SettingsDialog
from mergewizard.domain.Context import Context
from mergewizard.domain.SavedPluginsFile import SavedPluginsFile
from mergewizard.models.MergeModel import MergeModel
from mergewizard.models.PluginModel import PluginModel
from mergewizard.views.PluginViewFactory import PluginViewFactory
from mergewizard.constants import Icon, Setting


class PageId(IntEnum):
    PagePluginsSelect = 0
    PageReviewMasters = 1


class Wizard(QWizard):

    settingsChanged = pyqtSignal(list)

    def __init__(self, organizer: IOrganizer, parent: QWidget = None):
        super().__init__(parent)
        self.__context = Context(organizer)
        self.__context.dataCache.loadData()

        # self.resize(700, 500)
        self.setWizardStyle(0)
        self.setWindowTitle(self.tr("Merge Wizard"))
        self.setWindowIcon(QIcon(Icon.MERGEWIZARD))
        self.setSizeGripEnabled(True)
        self.setModal(True)
        self.setWindowFlags(Qt.CustomizeWindowHint | Qt.WindowMinMaxButtonsHint | Qt.WindowCloseButtonHint | Qt.Window)
        self.setButtonLayout(
            [self.CustomButton1, self.CancelButton, self.Stretch, self.BackButton, self.NextButton, self.CustomButton2]
        )
        self.setOptions(self.NoBackButtonOnStartPage)
        self.button(self.CustomButton1).setIcon(QIcon(Icon.SETTINGS))
        self.button(self.CustomButton1).setToolTip(self.tr("Set options for MergeWizard"))
        self.button(self.CustomButton1).setVisible(False)  # no setting at this time
        self.button(self.CustomButton2).setVisible(False)  # removing for now
        self.customButtonClicked.connect(self.handleCustomButton)
        self.addWizardPages()
        self.restoreSize()

    def context(self) -> Context:
        return self.__context

    def addWizardPages(self):
        loadZMerge = self.context().getUserSetting(Setting.LOAD_ZMERGE, True)
        PluginViewFactory.excludeMergeColumns = not loadZMerge

        self.setPage(PageId.PagePluginsSelect, PagePluginsSelect(self.context(), self))
        self.setPage(PageId.PageReviewMasters, PageReviewMasters(self.context(), self))
        for pageId in self.pageIds():
            self.settingsChanged.connect(self.page(pageId).settingsChanged)

    def handleCustomButton(self, which: int):
        if which == QWizard.CustomButton1:
            self.showSettingsDialog()

    def showSettingsDialog(self):
        settingsDialog = SettingsDialog(self)
        settingsDialog.loadSettings(self.context())
        settingsDialog.settingsChanged.connect(self.settingsChanged)
        if settingsDialog.exec() == SettingsDialog.Accepted:
            settingsDialog.storeSettings(self.context())

    def keyPressEvent(self, event: QKeySequence) -> None:
        # Prevent escape from closing window
        if event.key() != Qt.Key_Escape:
            super().keyPressEvent(event)

    def closeEvent(self, event: QCloseEvent) -> None:
        if not self.currentPage().isOkToExit():
            event.ignore()
            return
        self.saveSize()
        for id in self.pageIds():
            self.page(id).deinitializePage()
        self.saveSelectedPluginsToFile()

    def saveSelectedPluginsToFile(self):
        pluginsFile = SavedPluginsFile(self.context())
        pluginsFile.write()

    def saveSize(self) -> None:
        self.context().setSetting("WindowMaximized", self.isMaximized())
        if not self.isMaximized():
            self.context().setSetting("WindowHeight", self.size().height())
            self.context().setSetting("WindowWidth", self.size().width())
            self.context().setSetting("WindowX", self.pos().x())
            self.context().setSetting("WindowY", self.pos().y())

    def restoreSize(self) -> None:
        try:
            height = int(self.context().getSetting("WindowHeight", QVariant.Int, 0))
            width = int(self.context().getSetting("WindowWidth", QVariant.Int, 0))
            x = int(self.context().getSetting("WindowX", QVariant.Int, 0))
            y = int(self.context().getSetting("WindowY", QVariant.Int, 0))
        except ValueError:
            height = 0
            width = 0
            x = 0
            y = 0
        if height and width:
            self.resize(QSize(width, height))
        if x and y:
            self.move(QPoint(x, y))
        isMaximized = self.context().getSetting("WindowMaximized", QVariant.Bool, False)
        if isMaximized:
            self.setWindowState(self.windowState() | Qt.WindowMaximized)
