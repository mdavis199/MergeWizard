from PyQt5.QtCore import Qt, QModelIndex
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QWidget

from mergewizard.dialogs.WizardPage import WizardPage
from mergewizard.domain.Context import Context
from mergewizard.models.PluginModel import Column
from mergewizard.views.PluginViewFactory import PluginViewFactory, ViewType
from mergewizard.widgets.Splitter import Splitter
from mergewizard.constants import Icon, Setting
from .ui.PagePluginsSelect import Ui_PagePluginsSelect


class PagePluginsSelect(WizardPage):

    PROGRESS_OFFSET = 10

    def __init__(self, context: Context, parent: QWidget = None):
        super().__init__(parent)
        self.ui = Ui_PagePluginsSelect()
        self.ui.setupUi(self)
        self.context = context

        showMergeColumns = context.getUserSetting(Setting.LOAD_ZMERGE, True)

        #  views/models for the top plugin panels
        PluginViewFactory.configureView(ViewType.All, self.ui.pluginsList, context.pluginModel(), showMergeColumns)
        PluginViewFactory.configureView(
            ViewType.Selected, self.ui.selectedPluginsList, context.pluginModel(), showMergeColumns
        )
        self.ui.pluginsList.selectionModel().currentChanged.connect(lambda: self.showPluginInfo(ViewType.All))
        self.ui.selectedPluginsList.selectionModel().currentChanged.connect(
            lambda: self.showPluginInfo(ViewType.Selected)
        )
        self.pluginlist_pluginname_section = self.ui.pluginsList.sectionForColumn(Column.PluginName)

        # views/models for the bottom panels
        self.ui.pluginInfoWidget.setPluginModel(context.pluginModel())
        self.ui.bulkAddWidget.setPluginModel(context.pluginModel())
        self.ui.pluginInfoWidget.doubleClicked.connect(self.onInfoWidgetDoubleClicked)
        self.ui.filterEdit.textChanged.connect(self.ui.pluginsList.setNameFilter)

        # splitters
        Splitter.decorate(self.ui.splitter)
        Splitter.decorate(self.ui.allPluginsSplitter)
        Splitter.decorate(self.ui.selectedPluginsSplitter)
        self.ui.allPluginsSplitter.setStretchFactor(0, 2)
        self.ui.allPluginsSplitter.setStretchFactor(1, 1)
        self.ui.selectedPluginsSplitter.setStretchFactor(0, 2)
        self.ui.selectedPluginsSplitter.setStretchFactor(1, 1)
        self.didResizeSplitters = False

        # toggle buttons
        self.ui.toggleBulkButton.setIcon(QIcon(Icon.EDIT))
        self.ui.toggleBulkButton.clicked.connect(
            lambda: self.ui.bulkAddWidget.setVisible(not self.ui.bulkAddWidget.isVisible())
        )
        self.ui.toggleInfoButton.setIcon(QIcon(Icon.INFO))
        self.ui.toggleInfoButton.clicked.connect(
            lambda: self.ui.pluginInfoWidget.setVisible(not self.ui.pluginInfoWidget.isVisible())
        )

        # progressbar
        self.ui.progressBar.setRange(0, 100 + self.PROGRESS_OFFSET)
        context.pluginModel().modelLoadingStarted.connect(self.modelLoadingStarted)
        context.pluginModel().modelLoadingProgress.connect(self.modelLoadingProgress)
        context.pluginModel().modelLoadingCompleted.connect(self.modelLoadingCompleted)
        context.pluginModel().loadPlugins()

    def initializePage(self) -> None:
        self.restoreSettings()

    def deinitializePage(self) -> None:
        self.saveSettings()

    def saveSettings(self) -> None:
        infoPanelVisible = self.isInfoPanelOpen()
        textVisible = self.isTextBoxOpen()
        self.context.setSetting("InfoPanelVisible", infoPanelVisible)
        self.context.setSetting("TextBoxVisible", textVisible)

    def restoreSettings(self) -> None:
        infoPanelVisible = self.context.getSetting("InfoPanelVisible", "false")
        infoPanelVisible = infoPanelVisible == "true" or (isinstance(infoPanelVisible, bool) and infoPanelVisible)
        self.openInfoPanel(infoPanelVisible)
        textVisible = self.context.getSetting("TextBoxVisible", "false")
        textVisible = textVisible == "true" or (isinstance(textVisible, bool) and textVisible)
        self.openTextBox(textVisible)

    def isInfoPanelOpen(self) -> bool:
        return self.ui.pluginInfoWidget.isVisibleTo(self)

    def isTextBoxOpen(self) -> bool:
        return self.ui.bulkAddWidget.isVisibleTo(self)

    def openInfoPanel(self, visible: bool = True) -> None:
        self.ui.pluginInfoWidget.setVisible(visible)

    def openTextBox(self, visible: bool = True) -> None:
        self.ui.bulkAddWidget.setVisible(visible)

    def modelLoadingStarted(self):
        self.ui.progressBar.setVisible(True)
        self.ui.progressBar.setValue(self.PROGRESS_OFFSET)

    def modelLoadingProgress(self, value) -> None:
        self.ui.progressBar.setValue(value + self.PROGRESS_OFFSET)

    def modelLoadingCompleted(self) -> None:
        self.ui.progressFrame.setVisible(False)
        self.setUpViewsAfterModelReload()
        self.resizeSplitter()

    def resizeSplitter(self):
        # the Selected Plugin view has fewer columns than the plugin view
        # on the right side of the panel.  Try to size the splitter
        # proportionately.

        # We want to do this only once. We would not want the splitter
        # to jump around after the user has set it's position
        if not self.didResizeSplitters:
            self.didResizeSplitters = True
            modColumn = self.ui.pluginsList._columns.index(Column.ModName)
            priorityColumn = self.ui.pluginsList._columns.index(Column.Priority)
            samColumn = self.ui.pluginsList._columns.index(Column.IsSelectedAsMaster)
            width = self.ui.pluginsList.header().length()
            diffWidth = (
                self.ui.pluginsList.header().sectionSize(modColumn)
                + self.ui.pluginsList.header().sectionSize(samColumn)
                + self.ui.pluginsList.header().sectionSize(priorityColumn)
            )
            self.ui.splitter.setSizes([width, width - diffWidth])

    def setUpViewsAfterModelReload(self):
        width = self.ui.pluginsList.columnWidth(self.pluginlist_pluginname_section)  # pluginname
        self.ui.pluginInfoWidget.ui.infoView.setColumnWidth(0, width)
        self.ui.pluginsList.setCurrentIndex(self.ui.pluginsList.model().index(0, 0))

    # ----
    # ---- Methods related to the InfoView
    # ----

    def showPluginInfo(self, view: ViewType) -> None:
        idx = QModelIndex()
        # convert view's index to the PluginModel index
        if view == ViewType.Selected and self.ui.selectedPluginsList.currentIndex().isValid():
            idx = self.ui.selectedPluginsList.models().indexForModel(
                self.ui.selectedPluginsList.currentIndex(), self.ui.selectedPluginsList.models().pluginModel
            )
        elif not self.ui.pluginsList.currentIndex().isValid():
            self.ui.pluginsList.setCurrentIndex(self.ui.pluginsList.model().index(0, 0))

        if not idx.isValid():
            idx = self.ui.pluginsList.models().indexForModel(
                self.ui.pluginsList.currentIndex(), self.ui.pluginsList.models().pluginModel
            )
        self.ui.pluginInfoWidget.setRootIndex(idx)
        self.ui.pluginInfoWidget.ui.infoView.scrollToTop()

    def onInfoWidgetDoubleClicked(self, pluginName: str):
        model = self.ui.pluginsList.model()
        indexes = model.match(
            model.index(0, model.sourceColumnToProxy(Column.PluginName)),
            Qt.DisplayRole,
            pluginName,
            1,
            Qt.MatchExactly | Qt.MatchWrap,
        )
        if indexes:
            self.ui.pluginsList.setCurrentIndex(indexes[0])
