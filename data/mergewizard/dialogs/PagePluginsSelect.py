from enum import IntEnum, IntFlag, auto
from PyQt5.QtCore import Qt, QModelIndex, QVariant, QPoint, QItemSelectionModel, qInfo
from PyQt5.QtGui import QIcon, QKeySequence
from PyQt5.QtWidgets import QWidget, QAction, QHeaderView

from mergewizard.dialogs.WizardPage import WizardPage
from mergewizard.domain.Context import Context, Validator, INT_VALIDATOR
from mergewizard.models.PluginModel import Column
from mergewizard.models.PluginModelCollection import PluginModelCollection
from mergewizard.views.PluginViewFactory import PluginViewFactory, ViewType
from mergewizard.widgets.Splitter import Splitter
from mergewizard.constants import Icon
from .ui.PagePluginsSelect import Ui_PagePluginsSelect


class PagePluginsSelect(WizardPage):

    # Left panel stack widget
    class AllPageId(IntEnum):
        PluginInfoPanel = 0
        MergeInfoPanel = 1

    # Right panel stack widget
    class SelectedPageId(IntEnum):
        TextPanel = 0
        MergePanel = 1

    # Panel states are stored in settings as a bit mask
    class VisiblePanel(IntFlag):
        PluginInfo = auto()
        MergeInfo = auto()
        TextSelect = auto()
        MergeSelect = auto()
        Filters = auto()

    # This is data that is saved and restored when the
    # DataCache is reloaded after the user changes the settings.
    class DataToRestore:
        filters = 0
        selectedMergeName = ""
        selectedPluginNames = []

    def __init__(self, context: Context, parent: QWidget = None):
        super().__init__(parent)
        self.ui = Ui_PagePluginsSelect()
        self.ui.setupUi(self)
        self.context = context
        self.dataToRestore = self.DataToRestore()

        #  views/models for the top plugin panels
        PluginViewFactory.configureView(ViewType.All, self.ui.pluginsList, context.pluginModel)
        PluginViewFactory.configureView(ViewType.Selected, self.ui.selectedPluginsList, context.pluginModel)

        # splitters
        Splitter.decorate(self.ui.splitter)
        Splitter.decorate(self.ui.allPluginsSplitter)
        Splitter.decorate(self.ui.selectedPluginsSplitter)
        self.ui.allPluginsSplitter.setStretchFactor(0, 2)
        self.ui.allPluginsSplitter.setStretchFactor(1, 1)
        self.ui.selectedPluginsSplitter.setStretchFactor(0, 2)
        self.ui.selectedPluginsSplitter.setStretchFactor(1, 1)
        self.didResizeSplitters = False
        self.resizeSplitter()

        self.ui.pluginsList.selectionModel().currentChanged.connect(lambda c, p: self.showPluginInfo(c))
        self.ui.selectedPluginsList.selectionModel().currentChanged.connect(lambda c, p: self.showPluginInfo(c))
        self.ui.pluginsList.filterChanged.connect(self.updateFilterCount)
        self.context.pluginModel.rowsInserted.connect(lambda: self.updateFilterCount())
        self.context.pluginModel.rowsRemoved.connect(lambda: self.updateFilterCount())
        self.context.pluginModel.dataChanged.connect(lambda: self.updateFilterCount())

        # views/models for the bottom panels
        self.ui.pluginInfoWidget.setPluginModel(context.pluginModel)
        self.ui.mergeInfoWidget.setPluginModel(context.pluginModel)
        self.ui.bulkAddWidget.setPluginModel(context.pluginModel)
        self.ui.mergeSelectWidget.setMergeModel(context.mergeModel)
        self.ui.pluginInfoWidget.doubleClicked.connect(self.onInfoWidgetDoubleClicked)
        self.ui.mergeInfoWidget.doubleClicked.connect(self.onInfoWidgetDoubleClicked)
        self.ui.filterEdit.textChanged.connect(self.ui.pluginsList.setNameFilter)
        self.ui.mergeSelectWidget.ui.selectMergeButton.clicked.connect(self.selectPluginsFromMerge)
        self.ui.pluginFilterWidget.filterChanged.connect(self.ui.pluginsList.setFilter)

        context.dataCache.dataLoadingStarted.connect(self.modelLoadingStarted)
        context.dataCache.dataLoadingCompleted.connect(self.modelLoadingCompleted)

        # Buttons and other actions
        self.installActions()

        # We want to restore the panel to the state it was in when it was last closed.
        # Except, we want the all filters enabled, because it speeds up load time.
        # We save the filter setting and will restore after all the data is loaded.
        visiblePanels, mergeInfoStates, filters = self.getPageSettings()
        self.setPanelLayout(visiblePanels)
        self.setMergeInfoState(mergeInfoStates)

        self.ui.pluginFilterWidget.enableAll()
        self._firstTimeLoadingData = True

    def deinitializePage(self) -> None:
        self.savePageSettings()

    # ----
    # ---- Get and set states of various page elements
    # ----

    def getPanelLayout(self):
        visiblePanels = 0
        visiblePanels |= self.VisiblePanel.PluginInfo if self.isPluginInfoPanelOpen() else visiblePanels
        visiblePanels |= self.VisiblePanel.MergeInfo if self.isMergeInfoPanelOpen() else visiblePanels
        visiblePanels |= self.VisiblePanel.TextSelect if self.isTextPanelOpen() else visiblePanels
        visiblePanels |= self.VisiblePanel.MergeSelect if self.isMergePanelOpen() else visiblePanels
        visiblePanels |= self.VisiblePanel.Filters if self.isFilterPanelOpen() else visiblePanels
        return visiblePanels

    def setPanelLayout(self, visiblePanels: int):
        piVisible = visiblePanels & self.VisiblePanel.PluginInfo
        miVisible = visiblePanels & self.VisiblePanel.MergeInfo
        tsVisible = visiblePanels & self.VisiblePanel.TextSelect
        msVisible = visiblePanels & self.VisiblePanel.MergeSelect
        fVisible = visiblePanels & self.VisiblePanel.Filters
        if piVisible:
            self.openPluginInfoPanel(piVisible)
        else:
            self.openMergeInfoPanel(miVisible)
        if tsVisible:
            self.openTextPanel(tsVisible)
        else:
            self.openMergePanel(msVisible)
        self.openFilterPanel(fVisible)

    def getMergeInfoState(self) -> int:
        return self.ui.mergeInfoWidget.getExpandedStates()

    def setMergeInfoState(self, state: int):
        self.ui.mergeInfoWidget.setExpandedStates(state)

    def getFilters(self):
        return self.ui.pluginsList.filters()

    def setFilters(self, filters: int):
        self.ui.pluginFilterWidget.setFilters(filters)

    # ----
    # ---- Save and restore page settings (when app opens/closes)
    # ----

    def savePageSettings(self) -> None:
        self.context.settings.setInternal("Page1.PluginPanelStates", self.getPanelLayout())
        self.context.settings.setInternal("Page1.MergeInfoStates", self.getMergeInfoState())
        self.context.settings.setInternal("Page1.PluginFilters", self.getFilters())

    def getPageSettings(self) -> None:
        visiblePanels = self.context.settings.internal("Page1.PluginPanelStates", 0, INT_VALIDATOR)
        mergeInfoStates = self.context.settings.internal("Page1.MergeInfoStates", 0, INT_VALIDATOR)
        filters = self.context.settings.internal("Page1.PluginFilters", 0, INT_VALIDATOR)
        return (visiblePanels, mergeInfoStates, filters)

    # ----
    # ---- Opening and closing various panels
    # ----

    def isPluginInfoPanelOpen(self) -> bool:
        return self.ui.allStacked.currentIndex() == self.AllPageId.PluginInfoPanel and self.ui.allStacked.isVisibleTo(
            self
        )

    def isMergeInfoPanelOpen(self) -> bool:
        return self.ui.allStacked.currentIndex() == self.AllPageId.MergeInfoPanel and self.ui.allStacked.isVisibleTo(
            self
        )

    def isFilterPanelOpen(self) -> bool:
        return self.ui.pluginFilterWidget.isVisibleTo(self)

    def isTextPanelOpen(self) -> bool:
        return self.ui.selectedStacked.currentIndex() == self.SelectedPageId.TextPanel and self.ui.selectedStacked.isVisibleTo(
            self
        )

    def isMergePanelOpen(self) -> bool:
        return self.ui.selectedStacked.currentIndex() == self.SelectedPageId.MergePanel and self.ui.selectedStacked.isVisibleTo(
            self
        )

    def openFilterPanel(self, visible: bool = True, withFocus: bool = True) -> None:
        self.ui.pluginFilterWidget.setVisible(visible)
        self.ui.toggleFilterButton.setChecked(visible)
        if visible and withFocus:
            self.ui.pluginFilterWidget.setFocus(True)

    def openPluginInfoPanel(self, visible: bool = True, withFocus: bool = True) -> None:
        if visible:
            self.ui.allStacked.setCurrentIndex(self.AllPageId.PluginInfoPanel)
            if withFocus:
                self.ui.pluginInfoWidget.ui.infoView.setFocus()
        self.ui.allStacked.setVisible(visible)
        self.ui.togglePluginInfoButton.setChecked(visible)
        self.ui.toggleMergeInfoButton.setChecked(False)

    def openMergeInfoPanel(self, visible: bool = True, withFocus: bool = True) -> None:
        if visible:
            self.ui.allStacked.setCurrentIndex(self.AllPageId.MergeInfoPanel)
            if withFocus:
                self.ui.mergeInfoWidget.ui.infoView.setFocus()
        self.ui.allStacked.setVisible(visible)
        self.ui.toggleMergeInfoButton.setChecked(visible)
        self.ui.togglePluginInfoButton.setChecked(False)

    def openTextPanel(self, visible: bool = True, withFocus: bool = True) -> None:
        if visible:
            self.ui.selectedStacked.setCurrentIndex(self.SelectedPageId.TextPanel)
            if withFocus:
                self.ui.bulkAddWidget.ui.edit.setFocus()
        self.ui.selectedStacked.setVisible(visible)
        self.ui.toggleBulkButton.setChecked(visible)
        self.ui.toggleMergeButton.setChecked(False)

    def openMergePanel(self, visible: bool = True, withFocus: bool = True) -> None:
        if visible:
            self.ui.selectedStacked.setCurrentIndex(self.SelectedPageId.MergePanel)
            if withFocus:
                self.ui.mergeSelectWidget.ui.mergeView.setFocus()
        self.ui.selectedStacked.setVisible(visible)
        self.ui.toggleMergeButton.setChecked(visible)
        self.ui.toggleBulkButton.setChecked(False)

    def togglePluginPanelFocus(self):
        if self.ui.pluginsList.hasFocus():
            self.ui.selectedPluginsList.setFocus()
        else:
            self.ui.pluginsList.setFocus()

    def updateFilterCount(self) -> None:
        showing = self.ui.pluginsList.model().rowCount()
        total = self.context.pluginModel.rowCount()
        filtered = total - showing
        self.ui.filterCount.setText(self.tr("Filtered: {}, Showing: {}, Total: {}").format(filtered, showing, total))

    # ----
    # ----  Loading model data
    # ----

    def modelLoadingStarted(self):
        # Hiding all the data by enabling all the filters sped up loading quite a bit.
        # When loading 640 plugins, 533 mods, and 20 merges: this halved the time it took
        # to load and display the data.  Originally, about 6 seconds, down to 2.5 seconds.
        #
        # On the first time through, we don't save the filters because we will be using the ones
        # obtained from Settings when this page was constructed.
        if not self._firstTimeLoadingData:
            self.dataToRestore.filters = self.getFilters()
            self.dataToRestore.selectedMergeName = self.ui.mergeSelectWidget.getSelectedMergeName()
            self.dataToRestore.selectedPluginNames = self.context.pluginModel.selectedPluginNames()
            self.ui.pluginFilterWidget.enableAll()
        else:
            self.dataToRestore.filters = self.context.settings.internal("Page1.PluginFilters", 0, INT_VALIDATOR)
            self.dataToRestore.selectedMergeName = self.getLastLoadedMerge()
            self.dataToRestore.selectedPluginNames = []

    def modelLoadingCompleted(self) -> None:
        self.setFilters(self.dataToRestore.filters)
        self.setUpViewsAfterModelReload()
        self.showPluginInfo()
        self.selectMergeByName(self.dataToRestore.selectedMergeName)
        self.context.pluginModel.selectPluginsByName(self.dataToRestore.selectedPluginNames)
        if self._firstTimeLoadingData:
            self._firstTimeLoadingData = False
            self.resizeSplitter()

    def setUpViewsAfterModelReload(self):
        section = self.ui.pluginsList.sectionForColumn(Column.PluginName)
        if self.ui.pluginsList.model().rowCount() > 0:
            self.ui.pluginsList.resizeColumnToContents(section)
        else:
            self.ui.pluginsList.setColumnWidth(section, self.ui.pluginsList.viewport().width() / 2)

        if self.ui.pluginInfoWidget.isVisible():
            width = self.ui.pluginInfoWidget.ui.infoView.viewport().width() / 2 - 7
        else:
            width = self.ui.pluginsList.header().sectionSize(self.ui.pluginsList.sectionForColumn(Column.PluginName))
        self.ui.pluginInfoWidget.ui.infoView.setColumnWidth(0, width)

    def getLastLoadedMerge(self):
        data = self.context.readMergeWizardFile()
        if data:
            return data.loadedMod

    def selectMergeByName(self, mergeName):
        self.ui.mergeSelectWidget.selectMergeByName(mergeName)
        self.selectPluginsFromMerge()

    def resizeSplitter(self):
        # the Selected Plugin view has fewer columns than the plugin view
        # on the right side of the panel.  Try to size the splitter
        # proportionately.

        # We want to do this only once. We would not want the splitter
        # to jump around after the user has set it's position
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

    # ----
    # ---- Methods related to the InfoView
    # ----

    def showPluginInfo(self, viewIndex: QModelIndex = QModelIndex()) -> None:
        # It does not matter if the view is the allPlugins or selectedPlugins, they share
        # the same PluginModel.  We just need to drill through the proxies to the final index.
        if viewIndex.isValid():
            idx = PluginModelCollection.indexForModel(viewIndex, self.ui.pluginsList.models().pluginModel)
            self.ui.pluginInfoWidget.setRootIndex(idx)
            self.ui.mergeInfoWidget.setRootIndex(idx)
        else:
            idx = self.ui.pluginsList.currentIndex()
            if not idx.isValid():
                idx = self.ui.pluginsList.indexAt(QPoint(0, 0))
            if not idx.isValid():
                self.ui.pluginInfoWidget.setRootIndex(idx)
                self.ui.mergeInfoWidget.setRootIndex(idx)
            else:
                self.ui.pluginsList.selectionModel().setCurrentIndex(
                    idx, QItemSelectionModel.SelectCurrent | QItemSelectionModel.Rows
                )

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

    # ----
    # ---- Methods related to the Merge Panel
    # ----

    def selectPluginsFromMerge(self):
        idx = self.context.mergeModel.selectedMerge()
        if self.context.mergeModel.selectedMerge().isValid():
            # set the title for the group box
            if idx.row() > 0:
                self.ui.pluginSelectionGroup.setTitle(
                    self.tr("Selected Plugins: {}").format(self.ui.mergeSelectWidget.getSelectedMergeName())
                )
            else:
                self.ui.pluginSelectionGroup.setTitle(self.tr("Selected Plugins"))

            # remove plugin selections from the plugin model and select the plugins from the mod's merge.json file
            pluginNames = self.context.mergeModel.selectedMergePluginNames()
            self.context.pluginModel.resetPluginSelection()
            self.context.pluginModel.selectPluginsByName(pluginNames)
        else:
            self.ui.pluginSelectionGroup.setTitle(self.tr("Selected Plugins"))
            self.context.pluginModel.resetPluginSelection()

    # ----
    # ---- Methods related to actions
    # ----

    def installActions(self):
        a = QAction(self)
        a.setShortcut(Qt.ALT + Qt.Key_0)
        a.triggered.connect(lambda: self.togglePluginPanelFocus())

        self.addAction(a)
        a = QAction(self)
        a.setToolTip(self.tr("Toggle Filter Panel (Alt+1)"))
        a.setIcon(QIcon(Icon.FILTER))
        a.setCheckable(True)
        a.setShortcut(Qt.ALT + Qt.Key_1)
        a.triggered.connect(lambda: self.openFilterPanel(not self.isFilterPanelOpen(), True))
        self.ui.toggleFilterButton.setDefaultAction(a)
        a = QAction(self)
        a.setText(self.tr("Toggle Plugin Info (Alt+2)"))
        a.setIcon(QIcon(Icon.INFO))
        a.setCheckable(True)
        a.setShortcut(Qt.ALT + Qt.Key_2)
        a.triggered.connect(lambda: self.openPluginInfoPanel(not self.isPluginInfoPanelOpen(), True))
        self.ui.togglePluginInfoButton.setDefaultAction(a)
        a = QAction(self)
        a.setText(self.tr("Toggle Merge Info (Alt+3)"))
        a.setIcon(QIcon(Icon.MERGE))
        a.setCheckable(True)
        a.setShortcut(Qt.ALT + Qt.Key_3)
        a.triggered.connect(lambda: self.openMergeInfoPanel(not self.isMergeInfoPanelOpen(), True))
        self.ui.toggleMergeInfoButton.setDefaultAction(a)
        a = QAction(self)
        a.setText(self.tr("Toggle Text Entry Panel (Alt+4)"))
        a.setIcon(QIcon(Icon.EDIT))
        a.setCheckable(True)
        a.setShortcut(Qt.ALT + Qt.Key_4)
        a.triggered.connect(lambda: self.openTextPanel(not self.isTextPanelOpen(), True))
        self.ui.toggleBulkButton.setDefaultAction(a)
        a = QAction(self)
        a.setText(self.tr("Toggle Merge Selection Panel (Alt+5)"))
        a.setIcon(QIcon(Icon.MERGE))
        a.setCheckable(True)
        a.setShortcut(Qt.ALT + Qt.Key_5)
        a.triggered.connect(lambda: self.openMergePanel(not self.isMergePanelOpen(), True))
        self.ui.toggleMergeButton.setDefaultAction(a)
