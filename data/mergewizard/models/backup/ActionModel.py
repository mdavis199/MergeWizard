from enum import IntEnum, auto
from functools import reduce
from typing import List
from PyQt5.QtCore import pyqtSignal, Qt, QObject, QModelIndex, QAbstractItemModel, qInfo

from mergewizard.models.PluginModel import PluginModel
from mergewizard.domain.ILogger import Status as LogStatus
from mergewizard.domain.Profile import Profile


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
    Initialize = 0
    EnableSelected = auto()
    EnableMasters = auto()
    DisableOthers = auto()
    MoveSelected = auto()
    DeactivateMods = auto()
    Finalize = auto()


class ActionModel(QAbstractItemModel):
    log = pyqtSignal(str, LogStatus)

    actionText = [
        "Initialize.",
        'Enable plugins in the "Selected Plugins" list.',
        'Enable plugins in the "Plugin Masters" list.',
        "Disable plugins that are not in either list.",
        'Move the "Selected Plugins" to the lowest priority.',
        "Deactivate mods that do not contain enabled plugins.",
        "Finalize.",
    ]

    actionNames = [
        "initialization",
        "enable selected",
        "enable masters",
        "disable others",
        "move selected",
        "deactivate mods",
        "finalization",
    ]

    def __init__(self, profile: Profile = None, parent: QObject = None):
        super().__init__(parent)
        self._pluginActions = [None] * len(Action)
        self._status: List[Status] = [Status.NotStarted] * len(Action)
        self._enabled: List[bool] = [False] * len(Action)
        self._profile: Profile = profile
        self._pluginModel: PluginModel = None
        self._applyToProfile: str = None

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
            if role == Qt.CheckStateRole and idx.row() != Action.Initialize and idx.row() != Action.Finalize:
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
                if idx.row() == Action.Initialize or idx.row() == Action.Finalize:
                    return defaults
                else:
                    return defaults | Qt.ItemIsUserCheckable
            if idx.column() == Column.Status:
                return defaults

    def setData(self, idx: QModelIndex, value, role: int = Qt.EditRole):
        if not idx.isValid():
            return False

        if idx.column() == Column.Action:
            if role == Qt.CheckStateRole and idx.row() != Action.Initialize and idx.row() != Action.Finalize:
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
        self._pluginActions[Action.Initialize] = self.initialize
        self._pluginActions[Action.EnableSelected] = model.enableSelected
        self._pluginActions[Action.EnableMasters] = model.enableMasters
        self._pluginActions[Action.DisableOthers] = model.disableOthers
        self._pluginActions[Action.DeactivateMods] = model.deactivateUnneededMods
        self._pluginActions[Action.MoveSelected] = model.moveSelected
        self._pluginActions[Action.Finalize] = self.finalize

    def setProfile(self, profile: Profile):
        self.profile = profile

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

    def applyActions(self, profile=None):
        self.applyToProfile = profile
        self.resetStatus()
        cancel = False

        for action in Action:
            if self._enabled[action]:
                if cancel:
                    self.setActionStatus(action, Status.Cancelled)
                status = self.applyAction(action)
                if status == Status.Failed:
                    cancel = True
            else:
                self.setActionStatus(action, Status.Skipped)

    def applyAction(self, action: Action):
        self.setActionStatus(action, Status.Working)
        self.logStatus(action, Status.Working)
        result = self._pluginActions[action]()
        status = self.resultToStatus(result)
        self.setActionStatus(action, status)
        self.logStatus(action, status)
        return status

    def resultToStatus(self, result: PluginModel.ActionStatus):
        if result == PluginModel.ActionStatus.Success:
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

    def initialize(self):
        if self.profile.backupFiles():
            self.log.emit("Backed up files from current profile.", LogStatus.Info)
        else:
            self.log.emit("Failed to backup files from current profile.", LogStatus.Error)
            return PluginModel.ActionStatus.Failed

        if self.profile.create(self.applyToProfile):
            self.log.emit("Initialized profile: {}".format(self.applyToProfile), LogStatus.Info)
        else:
            self.log.emit("Failed to initialize profile: {}".format(self.applyToProfile), LogStatus.Error)
            return PluginModel.ActionStatus.Failed
        return PluginModel.ActionStatus.Success

    def finalize(self):
        # we only need to do this if a previous action was performed
        for i in range(len(Action)):
            if i == Action.Initialize:
                continue
            if i < Action.Finalize and self._status[i] != Status.Skipped:
                self._pluginModel.updatePluginStates()
                if self.applyToProfile is not None:
                    if self.profile.restoreBackup():
                        self.log.emit("Restored backup for current profile.", LogStatus.Info)
                        return PluginModel.ActionStatus.Success
                    else:
                        self.log.emit("Failed to restore backup to current profile.", LogStatus.Error)
                        return PluginModel.ActionStatus.Failed

        self.log.emit("No actions were taken. Not updating plugin states.", LogStatus.Info)
        return PluginModel.ActionStatus.Skipped

