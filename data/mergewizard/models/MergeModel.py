from enum import IntEnum, auto
from typing import List

from PyQt5.QtCore import (
    pyqtSignal,
    pyqtSlot,
    Qt,
    QObject,
    QModelIndex,
    QAbstractItemModel,
    QThreadPool,
    QSortFilterProxyModel,
)
from PyQt5.QtGui import QColor, QFont

from mergewizard.domain.AsyncWorker import Worker
from mergewizard.domain.MergeFileReader import MergeFileReader
from mergewizard.domain.Merge import Merge

from . import ItemId as Id


class Role(IntEnum):
    Data = Qt.UserRole


class Column(IntEnum):
    Name = 0
    PluginCount = auto()


class MergeModel(QAbstractItemModel):

    modelLoadingStarted = pyqtSignal()
    modelLoadingProgress = pyqtSignal(int)
    modelLoadingCompleted = pyqtSignal()

    def __init__(self, modFolder: str = "", parent: QObject = None):
        super().__init__(parent)
        self.__placeholder: Merge = Merge("")
        self.__modFolder: str = modFolder
        self.__isLoading: bool = False
        self.__merges: List[Merge] = [self.__placeholder]
        self.__selectedMerge: int = -1  # row that is selected

    def setModFolder(self, modFolder: str):
        self.__modFolder = modFolder

    def isLoading(self) -> bool:
        return self.__isLoading

    def loadMerges(self):
        self.__isLoading = True
        self.modelLoadingStarted.emit()
        worker = Worker(MergeFileReader.loadMerges, self.__modFolder)
        worker.signals.result.connect(self.setMerges)
        worker.signals.progress.connect(self.modelLoadingProgress)
        QThreadPool.globalInstance().start(worker)

    def setMerges(self, merges: List[Merge]):
        if len(self.__merges) > 1:
            self.beginRemoveRows(QModelIndex(), 1, len(self.__merges))
            self.__merges = [self.__placeholder]
            self.endRemoveRows()
        if self.__modFolder:
            if merges:
                self.beginInsertRows(QModelIndex(), 1, len(merges))
                self.__merges = self.__merges + sorted(merges)
                self.endInsertRows()
        self.__isLoading = False
        self.modelLoadingCompleted.emit()

    def setSelectedMerge(self, index: QModelIndex = QModelIndex()):
        self.__selectedMerge = index.row()

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
        return 2

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
                        return self.tr("-- Create NEW Merge --")
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

        if depth == Id.Depth.D1 and idx.column() == 0:
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

    def flags(self, idx: QModelIndex):
        depth = Id.depth(idx)
        if depth == Id.Depth.D0:
            if idx.column() == Column.Name:
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
        return self.sourceModel().data(left).lower() < self.sourceModel().data(right).lower()

    @pyqtSlot(bool)
    def sortByPriority(self, sortByPriority: bool):
        # The plugins in the underlying model are already sorted by priority
        self.sort(-1 if sortByPriority else 0)
        self.invalidate()

    def setSelectedMerge(self, idx: QModelIndex = QModelIndex()):
        sourceIndex = self.sourceModel().index(idx.row(), idx.column())
        self.sourceModel().setSelectedMerge(sourceIndex)
