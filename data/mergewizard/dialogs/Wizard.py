from enum import IntEnum

from PyQt5.QtCore import pyqtSignal, Qt, QSize, QPoint, QVariant
from PyQt5.QtGui import QCloseEvent, QIcon, QKeySequence
from PyQt5.QtWidgets import QWidget, QWizard

from mobase import IOrganizer

from mergewizard.dialogs.PagePluginsSelect import PagePluginsSelect
from mergewizard.dialogs.PageApplyChanges import PageApplyChanges
from mergewizard.dialogs.PageZMerge import PageZMerge
from mergewizard.dialogs.SettingsDialog import SettingsDialog
from mergewizard.domain.Context import Context, INT_VALIDATOR, BOOLEAN_VALIDATOR
from mergewizard.domain.SavedPluginsFile import SavedPluginsFile
from mergewizard.views.PluginViewFactory import PluginViewFactory
from mergewizard.constants import Icon, Setting


class PageId(IntEnum):
    PagePluginsSelect = 0
    PageApplyChanges = 1
    PageZMerge = 2


class Wizard(QWizard):
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
        self.button(self.CustomButton1).setVisible(True)  # no setting at this time
        self.button(self.CustomButton2).setVisible(False)  # removing for now
        self.customButtonClicked.connect(self.handleCustomButton)
        self.context().settings.loadUserSettings()
        self.addWizardPages()
        self.restoreSize()

    def context(self) -> Context:
        return self.__context

    def addWizardPages(self):
        self.setPage(PageId.PagePluginsSelect, PagePluginsSelect(self.context(), self))
        self.setPage(PageId.PageApplyChanges, PageApplyChanges(self.context(), self))
        self.setPage(PageId.PageZMerge, PageZMerge(self.context(), self))
        for pageId in self.pageIds():
            self.context().settings.settingChanged.connect(self.page(pageId).settingChanged)

    def handleCustomButton(self, which: int):
        if which == QWizard.CustomButton1:
            self.showSettingsDialog()

    def showSettingsDialog(self):
        settingsDialog = SettingsDialog(self)
        settingsDialog.loadSettings(self.context())
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
        self.__context.dataCache.stopLoading()
        self.saveSize()
        for id in self.pageIds():
            self.page(id).deinitializePage()
        self.__context.settings.storeUserSettings()
        # self.saveSelectedPluginsToFile()

    def saveSelectedPluginsToFile(self):
        pluginsFile = SavedPluginsFile(self.context())
        pluginsFile.write()

    def saveSize(self) -> None:
        self.context().settings.setInternal("Window.Maximized", self.isMaximized())
        if not self.isMaximized():
            self.context().settings.setInternal("Window.Height", self.size().height())
            self.context().settings.setInternal("Window.Width", self.size().width())
            self.context().settings.setInternal("Window.X", self.pos().x())
            self.context().settings.setInternal("Window.Y", self.pos().y())

    def restoreSize(self) -> None:
        isMaximized = self.context().settings.internal("Window.Maximized", False, BOOLEAN_VALIDATOR)
        height = self.context().settings.internal("Window.Height", 0, INT_VALIDATOR)
        width = self.context().settings.internal("Window.Width", 0, INT_VALIDATOR)
        x = self.context().settings.internal("Window.X", 0, INT_VALIDATOR)
        y = self.context().settings.internal("Window.Y", 0, INT_VALIDATOR)
        if height and width:
            self.resize(QSize(width, height))
        if x or y:
            self.move(QPoint(x, y))
        if isMaximized:
            self.setWindowState(self.windowState() | Qt.WindowMaximized)
