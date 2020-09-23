from enum import IntEnum, auto
from typing import List, Tuple
from PyQt5.QtCore import pyqtSlot, Qt, QObject, QAbstractItemModel, QSortFilterProxyModel, QModelIndex, QMimeData


class Column(IntEnum):
    Status = 0
    Message = auto()


class Status(IntEnum):
    Info = 0
    Warn = auto()
    Error = auto()
    Success = auto()
    Debug = auto()


def statusAsString(status: Status):
    labels = ["Info", "Warn", "Error", "Success", "Debug"]
    return labels[status]


class LogModel(QAbstractItemModel):
    def __init__(self, parent: QObject = None):
        super().__init__(parent)
        self.content: List[Tuple[Status, str]] = []

    def logMessage(self, message: str, status: int):
        position = len(self.content)
        self.beginInsertRows(QModelIndex(), position, position)
        self.content.append((status, message))
        self.endInsertRows()

    def logMessages(self, messages: List[str], status: int):
        start = len(self.content)
        end = start + len(messages)
        self.beginInsertRows(QModelIndex(), start, end)
        for message in messages:
            self.content.append((status, message))
        self.endInsertRows()

    def clear(self):
        self.beginRemoveRows(QModelIndex(), 0, len(self.content) - 1)
        self.content = []
        self.endRemoveRows()

    # --- Model method overrides

    def rowCount(self, parent: QModelIndex = QModelIndex()):
        if not parent.isValid():
            return len(self.content)
        return 0

    def columnCount(self, parent: QModelIndex = QModelIndex()):
        if not parent.isValid():
            return len(Column)
        return 0

    def index(self, row: int, col: int, parent: QModelIndex = QModelIndex()):
        if self.hasIndex(row, col, parent):
            return self.createIndex(row, col, 0)
        return QModelIndex()

    def parent(self, idx: QModelIndex):
        return QModelIndex()

    def data(self, idx: QModelIndex, role: int = Qt.DisplayRole):
        if not idx.isValid():
            return None
        if idx.column() == Column.Status:
            if role == Qt.UserRole:
                return self.content[idx.row()][0]
            if role == Qt.DisplayRole:
                return statusAsString(self.content[idx.row()][0])
        if idx.column() == Column.Message:
            if role == Qt.DisplayRole:
                return self.content[idx.row()][1]

    def flags(self, idx: QModelIndex):
        defaults = Qt.ItemIsEnabled | Qt.ItemNeverHasChildren | Qt.ItemIsSelectable
        if idx.isValid():
            return defaults

    def headerData(
        self, section: int, orientation: Qt.Orientation, role: int = Qt.DisplayRole,
    ):
        if orientation == Qt.Horizontal:
            if role == Qt.DisplayRole:
                if section == Column.Status:
                    return self.tr("Status")
                if section == Column.Message:
                    return self.tr("Message")
        return super().headerData(section, orientation, role)

    def mimeTypes(self):
        return ["text/plain"]

    def mimeData(self, indexes: List[QModelIndex]):
        if not indexes:
            return
        content = []
        sortedIndexes = sorted([index for index in indexes if index.isValid()], key=lambda index: index.row())
        for index in sortedIndexes:
            status, msg = self._content[index.row()]
            content.append("{:7} | {}".format(statusAsString(status), msg))
        mimeData = QMimeData()
        mimeData.setText("\n".join(content))
        return mimeData

    @pyqtSlot(str)
    @pyqtSlot(list)
    def info(
        self, value,
    ):
        if isinstance(value, list):
            self.logMessages(value, Status.Info)
        else:
            self.logMessage(value, Status.Info)

    @pyqtSlot(str)
    @pyqtSlot(list)
    def warn(self, value):
        if isinstance(value, list):
            self.logMessages(value, Status.Warn)
        else:
            self.logMessage(value, Status.Warn)

    @pyqtSlot(str)
    @pyqtSlot(list)
    def error(self, value):
        if isinstance(value, list):
            self.logMessages(value, Status.Error)
        else:
            self.logMessage(value, Status.Error)

    @pyqtSlot(str)
    @pyqtSlot(list)
    def success(self, value):
        if isinstance(value, list):
            self.logMessages(value, Status.Success)
        else:
            self.logMessage(value, Status.Success)

    @pyqtSlot(str)
    @pyqtSlot(list)
    def debug(self, value):
        if isinstance(value, list):
            self.logMessages(value, Status.Debug)
        else:
            self.logMessage(value, Status.Debug)

    @pyqtSlot(str, Status)
    @pyqtSlot(list, Status)
    def log(self, value, status):
        if isinstance(value, list):
            self.logMessages(value, status)
        else:
            self.logMessage(value, status)


class LogFilterModel(QSortFilterProxyModel):
    def __init__(self, parent: QObject = None):
        super().__init__(parent)
        self._showDebug = False

    def filterAcceptsRow(self, row: int, parent: QModelIndex):
        if self._showDebug or parent.isValid():
            return True
        idx = self.sourceModel().index(row, 0, parent)
        value = self.sourceModel().data(idx, Qt.UserRole)
        return value != Status.Debug

    def showDebugMessages(self, show: bool):
        self._showDebug = show
        self.invalidateFilter()
