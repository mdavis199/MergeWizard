from enum import Flag, auto
from PyQt5.QtCore import Qt, QObject, QSortFilterProxyModel, QModelIndex, qInfo
from mergewizard.models.PluginModelBase import Column, Role, isBoolColumn


class Filter(Flag):
    NoFilter = 0
    Inactive = auto()
    Missing = auto()
    Masters = auto()
    Merges = auto()
    Selected = auto()
    All = Inactive | Missing | Masters | Merges | Selected


class PluginType(Flag):
    Any = auto()
    Selected = auto()
    Masters = auto()


class PluginFilterModel(QSortFilterProxyModel):
    def __init__(self, parent: QObject = None):
        super().__init__(parent)
        self._filters = Filter.NoFilter
        self._nameFilter = ""
        self._pluginType = PluginType.Any
        self.setSortRole(Role.Cell)
        self.setSortCaseSensitivity(Qt.CaseInsensitive)
        self.setFilterKeyColumn(Column.PluginName)

    def filters(self):
        return self._filters

    def setFilter(self, filtr: Filter, enabled: bool):
        if enabled:
            self.replaceFilter(self._filters | filtr)
        else:
            self.replaceFilter(self._filters & ~filtr)

    def replaceFilter(self, filtr: Filter):
        if self._filters != filtr:
            self._filters = filtr
            self.invalidateFilter()

    def nameFilter(self):
        return self._nameFilter

    def setNameFilter(self, text: str):
        self._nameFilter = text
        self.invalidateFilter()

    def showOnlySelected(self, show: bool):
        self._pluginType = PluginType.Selected if show else PluginType.Any
        self.invalidateFilter()

    def showOnlyMasters(self, show: bool):
        self._pluginType = PluginType.Masters if show else PluginType.Any
        self.invalidateFilter()

    def toggleSelected(self, idx: QModelIndex):
        sourceIndex = self.mapToSource(idx)
        if sourceIndex.column() == Column.PluginName:
            isSelected = self.sourceModel().data(sourceIndex.siblingAtColumn(Column.IsSelected), Role.Cell)
            self.sourceModel().setData(sourceIndex.siblingAtColumn(Column.IsSelected), not isSelected)

    def filterAcceptsRow(self, sourceRow: int, sourceParent: QModelIndex):
        plugin = self.sourceModel().data(self.sourceModel().index(sourceRow, 0, sourceParent), Role.Data)
        if self._pluginType == PluginType.Selected:
            return plugin.isSelected()

        if self._pluginType == PluginType.Masters:
            return plugin.isSelectedAsMaster() and not plugin.isSelected()

        if self._filters & Filter.Inactive != Filter.NoFilter:
            if plugin.isInactive:
                return False
        if self._filters & Filter.Missing != Filter.NoFilter:
            if plugin.isMissing:
                return False
        if self._filters & Filter.Masters != Filter.NoFilter:
            if plugin.isMaster:
                return False
        if self._filters & Filter.Merges != Filter.NoFilter:
            if plugin.isMerge:
                return False
        if self._filters & Filter.Selected != Filter.NoFilter:
            if plugin.isSelected():
                return False
        if not self._nameFilter:
            return True
        if self._nameFilter.lower() in plugin.pluginName.lower():
            return True
        return False

    def lessThan(self, srcLeft: QModelIndex, srcRight: QModelIndex):
        if isBoolColumn(srcLeft.column()):
            return super().lessThan(srcRight, srcLeft)
        if srcLeft.column() == Column.Priority:
            leftData = self.sourceModel().data(srcLeft)
            rightData = self.sourceModel().data(srcRight)
            if rightData is None or rightData < 0:
                return True
            if leftData is None or leftData < 0:
                return False
        return super().lessThan(srcLeft, srcRight)

    def columnForFilter(self, filtr: Filter):
        if filter == Filter.Inactive:
            return Column.IsInactive
        if filter == Filter.Missing:
            return Column.IsMissing
        if filter == Filter.Masters:
            return Column.IsMaster
        if filter == Filter.Merges:
            return Column.IsMerge
        if filter == Filter.Selected:
            return Column.IsSelected
        return -1
