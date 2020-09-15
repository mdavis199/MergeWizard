from enum import IntEnum
from PyQt5.QtCore import Qt, QModelIndex, QVariant
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QWidget

from mergewizard.dialogs.WizardPage import WizardPage
from mergewizard.domain.Context import Context
from mergewizard.models.PluginModel import Column
from mergewizard.models.PluginModelCollection import PluginModelCollection
from mergewizard.views.PluginViewFactory import PluginViewFactory, ViewType
from mergewizard.widgets.Splitter import Splitter
from mergewizard.constants import Icon
from .ui.PagePluginsSelect import Ui_PagePluginsSelect


class PagePluginsSelect(WizardPage):
    class AllPageId(IntEnum):
        InfoPanel = 0

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
        self.ui.bulkAddWidget.setPluginModel(context.pluginModel)
        self.ui.mergeSelectWidget.setMergeModel(context.mergeModel)
        self.ui.pluginInfoWidget.doubleClicked.connect(self.onInfoWidgetDoubleClicked)
        self.ui.filterEdit.textChanged.connect(self.ui.pluginsList.setNameFilter)
        self.ui.pluginFilterWidget.filterChanged.connect(self.ui.pluginsList.setFilter)
        self.ui.mergeSelectWidget.ui.selectMergeButton.clicked.connect(self.selectPluginsFromMerge)

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

        # toggle buttons
        self.ui.toggleMergeButton.setIcon(QIcon(Icon.MERGE))
        self.ui.toggleBulkButton.setIcon(QIcon(Icon.EDIT))
        self.ui.toggleInfoButton.setIcon(QIcon(Icon.INFO))
        self.ui.toggleFilterButton.setIcon(QIcon(Icon.FILTER))

        self.ui.toggleBulkButton.clicked.connect(lambda: self.openTextPanel(not self.isTextPanelOpen()))
        self.ui.toggleMergeButton.clicked.connect(lambda: self.openMergePanel(not self.isMergePanelOpen()))
        self.ui.toggleInfoButton.clicked.connect(lambda: self.openInfoPanel(not self.isInfoPanelOpen()))
        self.ui.toggleFilterButton.clicked.connect(lambda: self.openFilterPanel(not self.isFilterPanelOpen()))

        context.dataCache.pluginModelLoadingCompleted.connect(self.setUpViewsAfterModelReload)
        context.dataCache.dataCacheLoadingCompleted.connect(self.modelLoadingCompleted)
        self.restoreSettings()

    def initializePage(self) -> None:
        """ If QWizard is not set to 'independent' pages then this method is called
        everytime the wizard switches from the previous page. Otherwize it is called only
        the first time it switches to this page """
        pass

    def deinitializePage(self) -> None:
        self.saveSettings()

    def saveSettings(self) -> None:
        self.context.setSetting("InfoPanelVisible", self.isInfoPanelOpen())
        self.context.setSetting("TextPanelVisible", self.isTextPanelOpen())
        self.context.setSetting("FilterPanelVisible", self.isFilterPanelOpen())
        self.context.setSetting("PluginFilters", self.ui.pluginsList.filters())

    def restoreSettings(self) -> None:
        visible = self.context.getSetting("InfoPanelVisible", QVariant.Bool, False)
        self.openInfoPanel(visible)
        visible = self.context.getSetting("TextPanelVisible", QVariant.Bool, False)
        self.openTextPanel(visible)
        self.openFilterPanel(False)
        filters = self.context.getSetting("PluginFilters", QVariant.Int, 0)
        if filters:
            self.ui.pluginFilterWidget.enableFilters(filters)

    def isInfoPanelOpen(self) -> bool:
        return self.ui.allStacked.currentIndex() == self.AllPageId.InfoPanel and self.ui.allStacked.isVisible()

    def isFilterPanelOpen(self) -> bool:
        return self.ui.pluginFilterWidget.isVisibleTo(self)

    def isTextPanelOpen(self) -> bool:
        return (
            self.ui.selectedStacked.currentIndex() == self.SelectedPageId.TextPanel
            and self.ui.selectedStacked.isVisible()
        )

    def isMergePanelOpen(self) -> bool:
        return (
            self.ui.selectedStacked.currentIndex() == self.SelectedPageId.MergePanel
            and self.ui.selectedStacked.isVisible()
        )

    def openFilterPanel(self, visible: bool = True) -> None:
        self.ui.pluginFilterWidget.setVisible(visible)
        self.ui.toggleFilterButton.setChecked(visible)

    def openInfoPanel(self, visible: bool = True) -> None:
        if visible:
            self.ui.allStacked.setCurrentIndex(self.AllPageId.InfoPanel)
        self.ui.allStacked.setVisible(visible)
        self.ui.toggleInfoButton.setChecked(visible)

    def openTextPanel(self, visible: bool = True) -> None:
        if visible:
            self.ui.selectedStacked.setCurrentIndex(self.SelectedPageId.TextPanel)
        self.ui.selectedStacked.setVisible(visible)
        self.ui.toggleBulkButton.setChecked(visible)
        self.ui.toggleMergeButton.setChecked(False)

    def openMergePanel(self, visible: bool = True) -> None:
        if visible:
            self.ui.selectedStacked.setCurrentIndex(self.SelectedPageId.MergePanel)
        self.ui.selectedStacked.setVisible(visible)
        self.ui.toggleMergeButton.setChecked(visible)
        self.ui.toggleBulkButton.setChecked(False)

    def updateFilterCount(self) -> None:
        showing = self.ui.pluginsList.model().rowCount()
        total = self.context.pluginModel.rowCount()
        filtered = total - showing
        self.ui.filterCount.setText(self.tr("Filtered: {}, Showing: {}, Total: {}").format(filtered, showing, total))

    def modelLoadingCompleted(self) -> None:
        self.setUpViewsAfterModelReload()
        self.resizeSplitter()
        self.showPluginInfo()

    def setUpViewsAfterModelReload(self):
        width = self.ui.pluginsList.columnWidth(self.ui.pluginsList.sectionForColumn(Column.PluginName))  # pluginname
        self.ui.pluginInfoWidget.ui.infoView.setColumnWidth(0, width / 2)

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
        else:
            idx = PluginModelCollection.indexForModel(
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

