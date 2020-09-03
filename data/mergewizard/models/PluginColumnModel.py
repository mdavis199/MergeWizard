from typing import List
from PyQt5.QtCore import Qt, QObject, QIdentityProxyModel, QModelIndex


class PluginColumnModel(QIdentityProxyModel):
    def __init__(self, parent: QObject = None):
        super().__init__(parent)
        self._columns: List[int] = []

    def setColumns(self, sourceColumns: List[int]):
        self.beginResetModel()
        self._columns = sourceColumns
        self.endResetModel()

    def columnCount(self, parent: QModelIndex = QModelIndex()):
        return 0 if self.sourceModel() is None else len(self._columns)

    def rowCount(self, parent: QModelIndex = QModelIndex()):
        sourceParent = self.mapToSource(parent).sibling(parent.row(), 0)
        return self.sourceModel().rowCount(sourceParent)

    def sibling(self, row: int, column: int, idx: QModelIndex = QModelIndex()):
        if self.validColumn(column):
            return self.index(row, column, idx.parent())
        return QModelIndex()

    def parent(self, child: QModelIndex = QModelIndex()):
        sourceIdx = self.mapToSource(child)
        sourceParent = sourceIdx.parent()
        if not sourceParent.isValid():
            return QModelIndex()
        return self.createIndex(sourceParent.row(), 0, sourceParent.internalPointer())

    def headerData(
        self, section: int, orientation: Qt.Orientation, role: int = Qt.DisplayRole,
    ):
        if orientation == Qt.Horizontal:
            return self.sourceModel().headerData(self.proxyColumnToSource(section), orientation, role)
        return super().headerData(section, orientation, role)

    def mapToSource(self, proxyIndex: QModelIndex = QModelIndex()):
        if not proxyIndex.isValid():
            return QModelIndex()
        return super().mapToSource(
            self.createIndex(
                proxyIndex.row(), self.proxyColumnToSource(proxyIndex.column()), proxyIndex.internalPointer(),
            )
        )

    def mapFromSource(self, sourceIdx: QModelIndex = QModelIndex()):
        if not sourceIdx.isValid():
            return QModelIndex()
        return self.createIndex(
            sourceIdx.row(), self.sourceColumnToProxy(sourceIdx.column()), sourceIdx.internalPointer(),
        )

    def index(self, row: int, col: int, parent: QModelIndex = QModelIndex()):
        if row < 0:
            return QModelIndex()
        sourceParent = self.mapToSource(parent).sibling(parent.row(), 0)
        sourceIndex = self.sourceModel().index(row, self._columns[col], sourceParent)
        if sourceIndex.isValid():
            return self.createIndex(row, col, sourceIndex.internalPointer())
        return QModelIndex()

    def sort(self, column: int, order: Qt.SortOrder):
        if self.validColumn(column):
            self.sourceModel().sort(self.proxyColumnToSource(column), order)

    def validColumn(self, proxyColumn: int):
        return self.sourceModel() is not None and proxyColumn < len(self._columns)

    def sourceColumnToProxy(self, sourceColumn: int):
        if sourceColumn >= len(self._columns) or sourceColumn < 0:
            return -1
        try:
            return self._columns.index(sourceColumn)
        except ValueError:
            # This can happen when the PluginModel emits a datachanged signal
            # for a column that is not mapped to this proxy model.
            return -1

    def proxyColumnToSource(self, proxyColumn: int):
        return self._columns[proxyColumn]
