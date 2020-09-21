from enum import IntEnum
from PyQt5.QtCore import Qt, QModelIndex, QVariant, QPoint, QItemSelectionModel
from PyQt5.QtGui import QIcon, QKeySequence
from PyQt5.QtWidgets import QWidget, QAction, QHeaderView

from mergewizard.dialogs.WizardPage import WizardPage
from mergewizard.domain.Context import Context
from mergewizard.models.PluginModel import Column
from mergewizard.models.PluginModelCollection import PluginModelCollection
from mergewizard.views.PluginViewFactory import PluginViewFactory, ViewType
from mergewizard.widgets.Splitter import Splitter
from mergewizard.constants import Icon
from .ui.PagePluginsSelect import Ui_PagePluginsSelect


class PagePluginsSelect(WizardPage):

    # On my system, loading 675 plugins takes about 2 sec to load the data from MO and zEdit files.
    # It takes another 3 seconds for pyQt to display it in the views (when the rows are added in bulk).
    # Here we prevent the progress bar from showing 100% while qt is working on the gui.
    PROGRESS_OFFSET = 1

    # Left panel stack widget
    class AllPageId(IntEnum):
        PluginInfoPanel = 0
        MergeInfoPanel = 1

    # Right panel stack widget
    class SelectedPageId(IntEnum):
        TextPanel = 0
        MergePanel = 1

    def __init__(self, context: Context, parent: QWidget = None):
        super().__init__(parent)
        self.ui = Ui_PagePluginsSelect()
        self.ui.setupUi(self)
        self.context = context

        #  views/models for the top plugin panels
        PluginViewFactory.configureView(ViewType.All, self.ui.pluginsList, context.pluginModel)
        PluginViewFactory.configureView(ViewType.Selected, self.ui.selectedPluginsList, context.pluginModel)

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

        # This speeds up data loading quite a bit.  Will restore everything after loading
        self.ui.pluginFilterWidget.enableAll()
        self.openFilterPanel(False)
        self.openMergeInfoPanel(False)
        self.openMergePanel(False)
        self.openPluginInfoPanel(False)
        self.openTextPanel(False)

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

        # progress bar
        self.ui.progressBar.setRange(0, 100 + self.PROGRESS_OFFSET)
        context.dataCache.dataLoadingStarted.connect(self.modelLoadingStarted)
        context.dataCache.dataLoadingProgress.connect(self.modelLoadingProgress)
        context.dataCache.dataLoadingCompleted.connect(self.modelLoadingCompleted)

        # Buttons and other actions
        self.installActions()

    def initializePage(self) -> None:
        """ If QWizard is not set to 'independent' pages then this method is called
        everytime the wizard switches from the previous page. Otherwise it is called only
        the first time it switches to this page """
        pass

    def deinitializePage(self) -> None:
        self.saveSettings()

    def saveSettings(self) -> None:
        self.context.setSetting("PluginInfoPanelVisible", self.isPluginInfoPanelOpen())
        self.context.setSetting("MergeInfoPanelVisible", self.isMergeInfoPanelOpen())
        self.context.setSetting("TextPanelVisible", self.isTextPanelOpen())
        self.context.setSetting("MergePanelVisible", self.isMergePanelOpen())
        self.context.setSetting("FilterPanelVisible", self.isFilterPanelOpen())
        self.context.setSetting("PluginFilters", self.ui.pluginsList.filters())
        self.context.setSetting("PluginListState", self.ui.mergeInfoWidget.getExpandedStates())

    def restoreSettings(self) -> None:
        piVisible = self.context.getSetting("PluginInfoPanelVisible", QVariant.Bool, False)
        miVisible = self.context.getSetting("MergeInfoPanelVisible", QVariant.Bool, False)
        tVisible = self.context.getSetting("TextPanelVisible", QVariant.Bool, False)
        mVisible = self.context.getSetting("MergePanelVisible", QVariant.Bool, False)
        if piVisible:
            self.openPluginInfoPanel(piVisible)
        else:
            self.openMergeInfoPanel(miVisible)
        if tVisible:
            self.openTextPanel(tVisible)
        else:
            self.openMergePanel(mVisible)
        self.openFilterPanel(False)
        self.ui.mergeInfoWidget.setExpandedStates(self.context.getSetting("PluginListState", QVariant.Int, None))

    def restoreFilterSettings(self):
        fVisible = self.context.getSetting("FilterPanelVisible", QVariant.Bool, False)
        self.openFilterPanel(fVisible)
        filters = self.context.getSetting("PluginFilters", QVariant.Int, 0)
        self.ui.pluginFilterWidget.setFilters(filters)

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

    def modelLoadingStarted(self):
        self.ui.progressLabel.setText(self.tr("Loading data:"))
        self.ui.progressFrame.setVisible(True)

    def modelLoadingProgress(self, value) -> None:
        self.ui.progressBar.setValue(value)
        if value == 100 - self.PROGRESS_OFFSET:
            self.ui.progressLabel.setText(self.tr("Loading views:"))

    def modelLoadingCompleted(self) -> None:
        self.ui.progressFrame.setVisible(False)
        self.ui.progressBar.setValue(0)
        self.restoreSettings()
        self.restoreFilterSettings()
        self.setUpViewsAfterModelReload()
        self.resizeSplitter()
        self.showPluginInfo()

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
        if self.context.mergeModel.selectedMerge().isValid():
            self.ui.pluginSelectionGroup.setTitle(
                self.tr("Plugins Selected for Merge: {}").format(self.ui.mergeSelectWidget.getSelectedMergeName())
            )
            pluginNames = self.context.mergeModel.selectedMergePluginNames()
            self.context.pluginModel.resetPluginSelection()
            self.context.pluginModel.selectPluginsByName(pluginNames)
        else:
            self.ui.pluginsSelectionGroup.setTitle(self.tr("Plugins Selected For Merge"))
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
