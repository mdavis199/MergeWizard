from enum import IntEnum, auto
from typing import List, Tuple
from PyQt5.QtCore import pyqtSignal, Qt, QObject, QAbstractItemModel, QSortFilterProxyModel, QModelIndex, QMimeData
from PyQt5.QtGui import QIcon
from mergewizard.constants import Icon


class Column(IntEnum):
    Status = 0
    Stage = auto()
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


class ActionLogModel(QAbstractItemModel):
    def __init__(self, parent: QObject = None):
        super().__init__(parent)
        self.content: List[Tuple[Status, str, str]] = []

    def logMessage(self, status: Status, stage: str, message: str):
        position = len(self.content)
        self.beginInsertRows(QModelIndex(), position, position)
        self.content.append((status, stage, message))
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
        if role == Qt.DisplayRole:
            if idx.column() == Column.Status:
                return statusAsString(self.content[idx.row()][Column.Status])
            return self.content[idx.row()][idx.column()]
        if role == Qt.UserRole:
            return self.content[idx.row()][idx.column()]
        if role == Qt.DecorationRole and idx.column() == Column.Status:
            if self.content[idx.row()][Column.Status] == Status.Info:
                return QIcon(Icon.LOG_INFO)
            if self.content[idx.row()][Column.Status] == Status.Warn:
                return QIcon(Icon.LOG_WARN)
            if self.content[idx.row()][Column.Status] == Status.Error:
                return QIcon(Icon.LOG_ERROR)
            if self.content[idx.row()][Column.Status] == Status.Success:
                return QIcon(Icon.LOG_SUCCESS)
            if self.content[idx.row()][Column.Status] == Status.Debug:
                return QIcon(Icon.LOG_DEBUG)

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
                if section == Column.Stage:
                    return self.tr("Action")
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
            status, stage, msg = self._content[index.row()]
            content.append("{:7} | {} | {}".format(statusAsString(status), stage, msg))
        mimeData = QMimeData()
        mimeData.setText("\n".join(content))
        return mimeData

    def log(self, status: Status, stage: str, msg: str):
        self.logMessage(status, stage, msg)


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
