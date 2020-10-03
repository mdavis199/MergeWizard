from enum import IntEnum, auto
from typing import List
from copy import deepcopy

from PyQt5.QtCore import pyqtSlot, pyqtSignal, QAbstractItemModel, QModelIndex, QObject, QSortFilterProxyModel, Qt
from PyQt5.QtGui import QColor, QFont, QIcon

from mergewizard.domain.merge import MergeFile
from mergewizard.constants import Icon
import mergewizard.models.ItemId as Id


class Role(IntEnum):
    Data = Qt.UserRole


class Column(IntEnum):
    Active = 0
    Name = auto()
    PluginCount = auto()


class MergeModel(QAbstractItemModel):

    # Emits the index of the current merge

    currentMergeChanged = pyqtSignal(object)

    def __init__(self, parent: QObject = None):
        super().__init__(parent)
        self.__placeholder: MergeFile = MergeFile("")
        self.__merges: List[MergeFile] = [self.__placeholder]
        self.__currentMerge: int = 0

    # ------------------------------------------------
    # Methods for data initialization and access
    # ------------------------------------------------

    # NOTE: These are actually the names of Mods that contain merge.json files

    def setMerges(self, merges: List[MergeFile]):
        if len(self.__merges) > 1:
            self.beginRemoveRows(QModelIndex(), 1, len(self.__merges))
            self.__merges = [self.__placeholder]
            self.endRemoveRows()
        if merges:
            self.beginInsertRows(QModelIndex(), 1, len(merges))
            self.__merges = self.__merges + sorted(merges)
            self.endInsertRows()

    def setCurrentMerge(self, index: QModelIndex = QModelIndex()):
        self.__currentMerge = index.row()
        self.currentMergeChanged.emit(self.index(self.__currentMerge, Column.Name))

    def currentMerge(self) -> QModelIndex:
        return self.index(self.__currentMerge, 1)

    def isCurrentMergeNew(self):
        return self.__currentMerge <= 0

    def currentMergeName(self):
        if self.__currentMerge > 0:
            return self.data(self.currentMerge())
        return ""

    def currentPluginName(self):
        if self.__currentMerge > 0:
            return self.__merges[self.__currentMerge].filename
        return ""

    def currentMergeFile(self):
        return self.__merges[self.__currentMerge]

    def indexForMergeName(self, name) -> QModelIndex:
        if not name:
            return self.index(0, Column.Name)
        row = next((i for i in range(len(self.__merges)) if self.__merges[i].name == name), -1)
        if row >= 0:
            return self.index(row, Column.Name)
        return QModelIndex()

    def currentMergePluginNames(self) -> List[str]:
        if self.__currentMerge < 0:
            return []
        names = []
        merge = self.__merges[self.__currentMerge]
        for pfd in merge.plugins:
            names.append(pfd.filename)
        return names

    def merges(self):
        return self.__merges

    # ------------------------------------------------
    # --- AbstractItemModel overrides
    # ------------------------------------------------
    def rowCount(self, parent: QModelIndex = QModelIndex()):
        depth = Id.depth(parent)
        if depth == Id.Depth.Invalid:
            return len(self.__merges)
        elif depth == Id.Depth.D0:
            return len(self.__merges[parent.row()].plugins)
        return 0

    def columnCount(self, parent: QModelIndex = QModelIndex()):
        return len(Column)

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

    def data(self, idx: QModelIndex, role: int = Qt.DisplayRole):
        depth = Id.depth(idx)
        if depth == Id.Depth.Invalid:
            return

        if depth == Id.Depth.D0:
            if role == Role.Data:
                return self.__merges[idx.row()]
            if role == Qt.DisplayRole:
                if idx.column() == Column.Name:
                    if idx.row() == 0:
                        return self.tr("-- New Merge --")
                    return self.__merges[idx.row()].name
                elif idx.column() == Column.PluginCount:
                    return self.rowCount(idx)
            elif role == Qt.ForegroundRole:
                if idx.column() == Column.PluginCount:
                    return QColor(Qt.lightGray).darker()
            elif role == Qt.FontRole:
                if idx.row() == 0:
                    font = QFont()
                    font.setBold(True)
                    return font
            elif role == Qt.DecorationRole:
                if idx.column() == Column.Active and idx.row() > 0:
                    if not self.__merges[idx.row()].modIsActive:
                        return QIcon(Icon.INACTIVE)

        if depth == Id.Depth.D1 and idx.column() == Column.Name:
            if role == Role.Data:
                return self.__merges[idx.parent().row()]
            if role == Qt.DisplayRole:
                return self.__merges[idx.parent().row()].plugins[idx.row()].filename
            if role == Qt.ForegroundRole:
                return QColor(Qt.lightGray).darker()

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.DisplayRole):
        if orientation == Qt.Horizontal:
            if role == Qt.DisplayRole:
                if section == Column.Name:
                    return self.tr("Mod Name")
                if section == Column.PluginCount:
                    return self.tr("Plugin Count")
            if role == Qt.TextAlignmentRole:
                if section == Column.Active:
                    return Qt.AlignRight

    def flags(self, idx: QModelIndex):
        depth = Id.depth(idx)
        if depth == Id.Depth.D0:
            if idx.column() == Column.Active:
                return Qt.ItemIsEnabled | Qt.ItemIsSelectable
            else:
                return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemNeverHasChildren
        if depth == Id.Depth.D1:
            return Qt.ItemNeverHasChildren
        return Qt.NoItemFlags


class MergeSortModel(QSortFilterProxyModel):
    def __init__(self, parent: QObject = None):
        super().__init__(parent)

    def lessThan(self, left: QModelIndex, right: QModelIndex):
        # This sorts the plugins alpabetically, leaves the mods order unchanged
        depth = Id.depth(left)
        if depth == Id.Depth.D0:
            return left.row() < right.row()
        return (
            self.sourceModel().data(left.siblingAtColumn(Column.Name)).lower()
            < self.sourceModel().data(right.siblingAtColumn(Column.Name)).lower()
        )

    @pyqtSlot(bool)
    def sortByPriority(self, sortByPriority: bool):
        # The plugins in the underlying model are already sorted by priority
        # so we set the sort column  to -1,
        self.sort(-1 if sortByPriority else 0)
        self.invalidate()

        # ----
        # ---- Convenience pass-through methods
        # ----

    def setCurrentMerge(self, idx: QModelIndex = QModelIndex()):
        sourceIndex = self.sourceModel().index(idx.row(), idx.column())
        self.sourceModel().setCurrentMerge(sourceIndex)

    def currentMerge(self) -> QModelIndex:
        self.mapFromSource(self.sourceModel().currentMerge())

    def currentMergeName(self):
        return self.sourceModel().currentMergeName()

    def currentPluginName(self):
        return self.sourceModel().currentPluginName()

    def indexForMergeName(self, name) -> QModelIndex:
        return self.mapFromSource(self.sourceModel().indexForMergeName(name))

    def isCurrentMergeNew(self) -> bool:
        return self.sourceModel().isCurrentMergeNew()
