from enum import IntEnum, auto
from functools import reduce
from typing import List
from PyQt5.QtCore import pyqtSignal, Qt, QObject, QModelIndex, QAbstractItemModel, qInfo

from mergewizard.models.PluginModel import PluginModel
from mergewizard.domain.ILogger import Status as LogStatus


class Column(IntEnum):
    Action = 0
    Status = auto()


class Status(IntEnum):
    NotStarted = 0
    Waiting = auto()
    Working = auto()
    Skipped = auto()
    Success = auto()
    Failed = auto()
    Cancelled = auto()


class Action(IntEnum):
    EnableSelected = 0
    EnableMasters = auto()
    DisableOthers = auto()
    DeactivateMods = auto()
    MoveSelected = auto()


class ActionModel(QAbstractItemModel):
    log = pyqtSignal(str, LogStatus)

    actionText = [
        'Enable plugins in the "Selected Plugins" list.',
        'Enable plugins in the "Plugin Masters" list.',
        "Disable plugins that are not in either list.",
        "Deactivate mods that do not contain enabled plugins.",
        'Move the "Selected Plugins" to the lowest priority.',
    ]

    actionNames = ["enable selected", "enable masters", "disable others", "move selected", "deactivate mods"]

    def __init__(self, parent: QObject = None):
        super().__init__(parent)
        self._pluginActions = [None] * len(Action)
        self._status: List[Status] = [Status.NotStarted] * len(Action)
        self._enabled: List[bool] = [False] * len(Action)
        self._pluginModel: PluginModel = None

    def rowCount(self, parent: QModelIndex = QModelIndex()):
        if not parent.isValid():
            return len(self.actionText)
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

        if idx.column() == Column.Action:
            if role == Qt.DisplayRole:
                return self.tr(self.actionText[idx.row()])
            if role == Qt.CheckStateRole:
                return Qt.Checked if self._enabled[idx.row()] else Qt.Unchecked

        if idx.column() == Column.Status:
            if role == Qt.DisplayRole:
                if self._status[idx.row()] == Status.NotStarted:
                    return ""
                if self._status[idx.row()] == Status.Waiting:
                    return self.tr("Waiting")
                if self._status[idx.row()] == Status.Working:
                    return self.tr("Working")
                if self._status[idx.row()] == Status.Skipped:
                    return self.tr("Skipped")
                if self._status[idx.row()] == Status.Success:
                    return self.tr("Completed")
                if self._status[idx.row()] == Status.Failed:
                    return self.tr("Failed")
                if self._status[idx.row()] == Status.Cancelled:
                    return self.tr("Cancelled")
                return

    def flags(self, idx: QModelIndex):
        defaults = Qt.ItemIsEnabled | Qt.ItemNeverHasChildren | Qt.ItemIsSelectable
        if idx.isValid():
            if idx.column() == Column.Action:
                return defaults | Qt.ItemIsUserCheckable
            if idx.column() == Column.Status:
                return defaults

    def setData(self, idx: QModelIndex, value, role: int = Qt.EditRole):
        if not idx.isValid():
            return False

        if idx.column() == Column.Action:
            if role == Qt.CheckStateRole:
                enable = value == Qt.Checked
                if self.isActionEnabled(idx.row()) != enable:
                    self._enabled[idx.row()] = value == Qt.Checked
                    self.dataChanged.emit(idx, idx, [role])
                    self.headerDataChanged.emit(Qt.Horizontal, Column.Action, Column.Action)
                    return True
        return False

    def headerData(
        self, section: int, orientation: Qt.Orientation, role: int = Qt.DisplayRole,
    ):
        if orientation == Qt.Horizontal:
            if role == Qt.DisplayRole:
                if section == Column.Action:
                    return self.tr("Action")
                if section == Column.Status:
                    return self.tr("Status")
            elif role == Qt.CheckStateRole:
                if self.isAllEnabled():
                    return Qt.Checked
                if self.isNoneEnabled():
                    return Qt.Unchecked
                return Qt.PartiallyChecked

        return super().headerData(section, orientation, role)

    def toggleAll(self):
        self.setAllActionsEnabled(not self.isAllEnabled())

    def setAllActionsEnabled(self, on: bool):
        self._enabled = [on] * len(Action)
        self.dataChanged.emit(
            self.index(0, Column.Action), self.index(len(self._enabled) - 1, Column.Action), [Qt.CheckStateRole]
        )
        self.headerDataChanged.emit(Qt.Horizontal, Column.Action, Column.Action)

    def isAllEnabled(self):
        return reduce(lambda a, b: a & b, self._enabled)

    def isNoneEnabled(self):
        return not reduce(lambda a, b: a | b, self._enabled)

    # --- Methods related to performing actions

    def setPluginModel(self, model: PluginModel):
        self._pluginModel = model
        self._pluginActions[Action.EnableSelected] = model.enableSelected
        self._pluginActions[Action.EnableMasters] = model.enableMasters
        self._pluginActions[Action.DisableOthers] = model.disableOthers
        self._pluginActions[Action.MoveSelected] = model.moveSelected
        self._pluginActions[Action.DeactivateMods] = model.deactivateUnneededMods

    def hasEnabledActions(self):
        for isEnabled in self._enabled:
            if isEnabled:
                return True
        return False

    def isActionEnabled(self, action: Action):
        return self._enabled[action]

    def setActionEnabled(self, action: Action, enable: bool):
        if self._enabled[action] != enable:
            self._enabled[action] = enable
            idx = self.index(action, Column.Status)
            self.dataChanged.emit(idx, idx)

    def actionStatus(self, action: Action):
        return self._status[action]

    def setActionStatus(self, action: Action, status: Status):
        if self._status[action] != status:
            self._status[action] = status
            idx = self.index(action, Column.Status)
            self.dataChanged.emit(idx, idx)

    def resetStatus(self):
        for i in range(len(self._status)):
            self.setActionStatus(i, Status.NotStarted)

    def applyActions(self):
        self.resetStatus()
        for action in Action:
            if self._enabled[action]:
                self.applyAction(action)
            else:
                self.setActionStatus(action, Status.Skipped)

    def applyAction(self, action: Action):
        self.setActionStatus(action, Status.Working)
        self.logStatus(action, Status.Working)
        result = self._pluginActions[action]()
        status = self.resultToStatus(result)
        self.setActionStatus(action, status)
        self.logStatus(action, status)

    def resultToStatus(self, result: PluginModel.ActionStatus):
        if result == PluginModel.ActionStatus.Completed:
            return Status.Success
        if result == PluginModel.ActionStatus.Skipped:
            return Status.Skipped

    def logStatus(self, action: Action, status: Status):
        name = self.actionNames[action]
        if status == Status.Working:
            qInfo("Started action: {}".format(name))
        if status == Status.Success:
            qInfo("Completed action: {}".format(name))
        if status == Status.Skipped:
            qInfo("Skipped action: {}".format(name))
