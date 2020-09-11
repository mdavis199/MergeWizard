from enum import IntEnum, auto
from typing import List
from PyQt5.QtCore import Qt, QObject, QModelIndex, QIdentityProxyModel, QAbstractProxyModel, QSortFilterProxyModel
from PyQt5.QtGui import QIcon, QColor, QFont

import mergewizard.models.ItemId as Id
from mergewizard.models.PluginModel import PluginModel
from mergewizard.models.PluginModelBase import Role, Column as PluginColumn
from mergewizard.constants import Icon

"""
The InfoModel shows the requirement relationships that a Plugin belongs to.

The info is structured as a Tree. One main row for each of the plugins in the PluginModel.
These rows always map one-to-one to the PluginModel.

The child rows are two columns.
Column 0 is a list of all plugins that the parent plugin requires.
Column 1 is a list of all plugins that require the parent.

The standard QSortFilterProxyModel does not work here because the two columns are independent.
Sorting one column alphabetically would cause the other column to be sorted incorrectly.
Filtering out a plugin in one row would incorrectly remove the sibling plugin from the other column.

To avoid that problem, each column is represented by a ReqColumnModel.
These are inserted into their own subclassed QSortFilterProxyModel.  The InfoModel holds
the two filter models and coordinates between them.

TODO: This whole arrangement is just a hack and needs to change.  Just bite the bullet and rewrite
the QSortFilterItemModel.  Need to use persistent indexes anyway.

"""


class Column(IntEnum):
    PluginName = 0


class DataType(IntEnum):
    Requires = 0
    RequiredBy = auto()


class ReqColumnModel(QIdentityProxyModel):
    def __init__(self, dataType: DataType, pluginModel: PluginModel, parent: QObject = None):
        super().__init__(parent)
        self._dataType: DataType = dataType
        self.setSourceModel(pluginModel)

    def rowCount(self, parent: QModelIndex = QModelIndex()):
        if self.sourceModel() is None:
            return 0
        depth = Id.depth(parent)
        if depth == Id.Depth.Invalid:
            return self.sourceModel().rowCount()
        if depth != Id.Depth.D0:
            return 0
        if parent.column() != 0:
            return 0
        requirements, dependents = self.sourceModel().data(self.mapToSource(parent), Role.Associations)
        if self._dataType == DataType.Requires:
            return len(requirements)
        else:
            return len(dependents)

    def columnCount(self, parent: QModelIndex = QModelIndex()):
        return 1

    def index(self, row: int, col: int, parent: QModelIndex = QModelIndex()):
        if self.hasIndex(row, col, parent):
            return self.createIndex(row, col, Id.idForIndex(parent))
        return QModelIndex()

    def parent(self, child: QModelIndex):
        if not child.isValid():
            return QModelIndex()
        parentId = child.internalId()
        if not Id.isValid(parentId):
            return QModelIndex()
        return self.createIndex(Id.row(parentId), Id.column(parentId), Id.parentId(parentId))

    def sibling(self, row: int, col: int, idx: QModelIndex = QModelIndex()):
        if idx.isValid() and self.hasIndex(row, col, idx.parent()):
            return self.index(row, col, idx.parent())
        return QModelIndex()

    def mapToSource(self, proxyIdx: QModelIndex):
        depth = Id.depth(proxyIdx)
        if depth == Id.Depth.Invalid:
            return QModelIndex()
        if depth == Id.Depth.D0:
            return self.sourceModel().index(proxyIdx.row(), PluginColumn.PluginName)
        return QModelIndex()

    def mapFromSource(self, sourceIdx: QModelIndex):
        # source index is for the PluginModel,
        # maps to a depth 0 row
        if not sourceIdx.isValid():
            return QModelIndex()
        return self.index(sourceIdx.row(), Column.PluginName)

    def data(self, idx: QModelIndex, role: int = Qt.DisplayRole):
        depth = Id.depth(idx)
        if depth == Id.Depth.Invalid:
            return None
        if depth == Id.Depth.D0:
            if role == Qt.DisplayRole or role == Role.Data:
                sourceIdx = self.sourceModel().index(idx.row(), PluginColumn.PluginName)
                return self.sourceModel().data(sourceIdx, role)
        if depth == Id.Depth.D1:
            sourceParentIdx = self.sourceModel().index(idx.parent().row(), PluginColumn.PluginName)
            requirements, dependents = self.sourceModel().data(sourceParentIdx, Role.Associations)

            association = requirements[idx.row()] if self._dataType == DataType.Requires else dependents[idx.row()]

            plugin = association.plugin
            isDirect = association.direct

            if role == Role.Data:
                return (plugin, isDirect)

            if role == Qt.DisplayRole:
                return association.plugin.pluginName
            elif role == Qt.DecorationRole:
                if plugin.isMissing:
                    if plugin.isSelected or plugin.isSelectedAsMaster:
                        return QIcon(Icon.INFO_MISSING_SELECTED)
                    return QIcon(Icon.INFO_MISSING)
                else:
                    if plugin.isSelected:
                        return QIcon(Icon.INFO_SELECTED)
                    elif plugin.isSelectedAsMaster:
                        return QIcon(Icon.INFO_SELECTED_AS_MASTER)
                    return QIcon(Icon.INFO_NOT_SELECTED)
            elif role == Qt.FontRole:
                if not isDirect:
                    font = QFont()
                    font.setItalic(True)
                    return font
            elif role == Qt.ForegroundRole:
                if not isDirect:
                    return QColor(Qt.lightGray).darker()


class ReqSortFilterModel(QSortFilterProxyModel):
    def __init__(self, model: ReqColumnModel, parent: QObject = None):
        super().__init__(parent)
        self.setRecursiveFilteringEnabled(True)
        self._includeIndirect = True
        self._sortByPriority = True
        self.setSourceModel(model)

    def includeIndirect(self, includeIndirect: bool):
        self._includeIndirect = includeIndirect
        self.invalidateFilter()

    def sortByPriority(self, sortByPriority: bool):
        self._sortByPriority = sortByPriority
        self.invalidate()
        self.sort(0)

    def lessThan(self, left: QModelIndex, right: QModelIndex):
        depth = Id.depth(left)
        if depth == Id.Depth.D0:
            return left.row() < right.row()

        leftPlugin, _ = self.sourceModel().data(left, Role.Data)
        rightPlugin, _ = self.sourceModel().data(right, Role.Data)

        if not self._sortByPriority:
            return leftPlugin < rightPlugin

        right = rightPlugin.priority
        left = leftPlugin.priority

        noRight = right < 0
        noLeft = left < 0

        if noRight and noLeft:
            return leftPlugin < rightPlugin
        if noRight:
            return True
        if noLeft:
            return False
        return left < right

    # TODO: use -1 as the column to fallback to underlying sort
    def filterAcceptsRow(self, sourceRow: int, sourceParent: QModelIndex):
        if self._includeIndirect:
            return True
        if not sourceParent.isValid():
            return True

        idx = self.sourceModel().index(sourceRow, 0, sourceParent)
        (plugin, isDirect) = self.sourceModel().data(idx, Role.Data)
        return isDirect


class PluginInfoModel(QAbstractProxyModel):
    def __init__(self, model: PluginModel, parent: QObject = None):
        super().__init__(parent)
        self.setSourceModel(model)

    def setSourceModel(self, model: PluginModel):
        self.pluginModel = model
        self.requiresModel = ReqSortFilterModel(ReqColumnModel(DataType.Requires, model))
        self.requiredByModel = ReqSortFilterModel(ReqColumnModel(DataType.RequiredBy, model))
        model.dataChanged.connect(self.sourceDataChanged)

    def sourceModel(self):
        return self.pluginModel

    def rowCount(self, parent: QModelIndex = QModelIndex()):
        depth = Id.depth(parent)
        if depth == Id.Depth.Invalid:
            return self.pluginModel.rowCount()
        if depth != Id.Depth.D0:
            return 0
        requiresParentIdx = self.requiresModel.index(parent.row(), 0)
        requiredByParentIdx = self.requiredByModel.index(parent.row(), 0)
        return max(self.requiresModel.rowCount(requiresParentIdx), self.requiredByModel.rowCount(requiredByParentIdx))

    def columnCount(self, parent: QModelIndex = QModelIndex()):
        return 2

    def index(self, row: int, col: int, parent: QModelIndex = QModelIndex()):
        if self.hasIndex(row, col, parent):
            return self.createIndex(row, col, Id.idForIndex(parent))
        return QModelIndex()

    def parent(self, child: QModelIndex = QModelIndex()):
        if not child.isValid():
            return QModelIndex()
        parentId = child.internalId()
        if not Id.isValid(parentId):
            return QModelIndex()
        return self.createIndex(Id.row(parentId), Id.column(parentId), Id.parentId(parentId))

    def mapToSource(self, proxyIdx: QModelIndex = QModelIndex()):
        depth = Id.depth(proxyIdx)
        if depth == Id.Depth.Invalid:
            return QModelIndex()
        if depth == Id.Depth.D0:
            return self.pluginModel.index(proxyIdx.row(), PluginColumn.PluginName)
        return QModelIndex()

    def mapFromSource(self, sourceIdx: QModelIndex = QModelIndex()):
        if not sourceIdx.isValid():
            return QModelIndex()
        return self.index(sourceIdx.row(), Column.PluginName)

    def mapToReqModel(self, dataType: DataType, idx: QModelIndex):
        depth = Id.depth(idx)
        if depth == Id.Depth.Invalid:
            return QModelIndex()
        reqModel = self.requiresModel if dataType == DataType.Requires else self.requiredByModel
        if depth == Id.Depth.D0:
            return reqModel.index(idx.row(), Column.PluginName)
        if depth == Id.Depth.D1:
            return reqModel.index(idx.row(), 0, reqModel.index(idx.parent().row(), 0))

    def flags(self, idx: QModelIndex = QModelIndex()):
        depth = Id.depth(idx)
        if depth == Id.Depth.D0:
            return Qt.ItemIsSelectable | Qt.ItemIsEnabled
        elif depth == Id.Depth.D1:
            return Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemNeverHasChildren
        else:
            return Qt.NoItemFlags

    def data(self, idx: QModelIndex, role: int = Qt.DisplayRole):
        depth = Id.depth(idx)
        if depth == Id.Depth.Invalid:
            return None
        if depth == Id.Depth.D0:  # either model works here
            requiresIdx = self.requiresModel.index(idx.row(), 0)
            return self.requiresModel.data(requiresIdx, role)

        if idx.column() == DataType.Requires:
            requiresIdx = self.mapToReqModel(DataType.Requires, idx)
            return self.requiresModel.data(requiresIdx, role)

        requiredByIdx = self.mapToReqModel(DataType.RequiredBy, idx)
        return self.requiredByModel.data(requiredByIdx, role)

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.DisplayRole):
        if orientation == Qt.Horizontal:
            if role == Qt.DisplayRole:
                if section == DataType.Requires:
                    return self.tr("Requires")
                if section == DataType.RequiredBy:
                    return self.tr("Required By")
        return super().headerData(section, orientation, role)

    def sortByPriority(self, sortByPriority: bool):
        self.layoutAboutToBeChanged.emit([], self.VerticalSortHint)
        self.requiresModel.sortByPriority(sortByPriority)
        self.requiredByModel.sortByPriority(sortByPriority)
        self.layoutChanged.emit()

    def includeIndirect(self, includeIndirect: bool):
        self.layoutAboutToBeChanged.emit()
        self.requiresModel.includeIndirect(includeIndirect)
        self.requiredByModel.includeIndirect(includeIndirect)
        self.layoutChanged.emit()

    def sourceDataChanged(self, topLeft: QModelIndex, bottomRight: QModelIndex, roles: List[int]):
        leftCol = topLeft.column()
        rightCol = bottomRight.column()
        if rightCol == -1:
            rightCol = leftCol
        rightCol = rightCol + 1

        if PluginColumn.PluginOrder in range(leftCol, rightCol) or PluginColumn.MasterOrder in range(leftCol, rightCol):
            self.layoutChanged.emit()
