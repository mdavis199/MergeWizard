from enum import IntEnum, auto
from functools import reduce
from typing import List, Callable
from PyQt5.QtCore import pyqtSignal, Qt, QObject, QModelIndex, QAbstractItemModel, qInfo, QCoreApplication

from mergewizard.models.ActionLogModel import Status as LogLevel
from mergewizard.models.PluginModel import PluginModel
from mergewizard.models.PluginModelBase import Role as PluginRole
from mergewizard.domain.Profile import Profile


class Column(IntEnum):
    Enable = 0
    Action = 1
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


class ActionHolder:
    def __init__(self, id: Action, required, name: str, text: str, func: Callable = None):
        self._id: Status = id
        self._required: bool = required
        self._enabled: bool = False
        self._name: str = name
        self._text: str = text
        self._func: Callable = func
        self._status = Status.NotStarted

    @property
    def name(self):
        return self._name

    @property
    def id(self):
        return self._id

    @property
    def required(self):
        return self._required

    @property
    def text(self):
        return self._text

    @property
    def function(self):
        return self._func

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, value):
        self._status = value

    @property
    def enabled(self):
        return self._enabled

    @enabled.setter
    def enabled(self, value):
        self._enabled = value


class ActionModel(QAbstractItemModel):
    logMessage = pyqtSignal(LogLevel, str, str)
    started = pyqtSignal()
    finished = pyqtSignal()

    def __init__(self, profile: Profile = None, parent: QObject = None):
        super().__init__(parent)
        self._pluginActions = [None] * len(Action)
        self._status: List[Status] = [Status.NotStarted] * len(Action)
        self._enabled: List[bool] = [False] * len(Action)
        self._profileMgr: Profile = profile
        self._pluginModel: PluginModel = None
        self._profile: str = None
        self._actions = self.createActions()

    def setPluginModel(self, model: PluginModel):
        self._pluginModel = model

    def setProfile(self, profileMgr: Profile):
        self._profileMgr = profileMgr

    def createActions(self):
        return [
            ActionHolder(Action.Initialize, True, "Initialize", "Initialize actions.", self.initializeActions),
            ActionHolder(
                Action.EnableSelected,
                False,
                "Enable Selected",
                'Enable plugins in the "Selected Plugins" list.',
                self.enableSelected,
            ),
            ActionHolder(
                Action.EnableMasters,
                False,
                "Enable Masters",
                'Enable plugins in the "Plugin Masters" list.',
                self.enableMasters,
            ),
            ActionHolder(
                Action.DisableOthers,
                False,
                "Disable Other",
                "Disable plugins that are in neither list.",
                self.disableOthers,
            ),
            ActionHolder(
                Action.MoveSelected,
                False,
                "Move Selected",
                'Move the "Selected Plugins" to the lowest priority.',
                self.moveSelected,
            ),
            ActionHolder(
                Action.DeactivateMods,
                False,
                "Deactivate Mods",
                "Deactivate mods that do not contain enabled plugins.",
                self.deactivateMods,
            ),
            ActionHolder(Action.Finalize, True, "Finalize", "Finalize actions.", self.finalizeActions),
        ]

    def rowCount(self, parent: QModelIndex = QModelIndex()):
        if not parent.isValid():
            return len(self._actions)
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
                s = self._actions[idx.row()].status
                return ["", "Waiting", "Working", "Skipped", "Completed", "Failed", "Cancelled"][s]
            if idx.column() == Column.Action:
                return self._actions[idx.row()].text

        if role == Qt.CheckStateRole and idx.column() == Column.Enable:
            return Qt.Checked if self._actions[idx.row()].enabled else Qt.Unchecked

    def flags(self, idx: QModelIndex):
        if idx.isValid():
            if idx.column() == Column.Enable:
                if self._actions[idx.row()].required:
                    return Qt.ItemNeverHasChildren | Qt.ItemIsSelectable
                else:
                    return Qt.ItemNeverHasChildren | Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsUserCheckable
            else:
                return Qt.ItemNeverHasChildren | Qt.ItemIsSelectable | Qt.ItemIsEnabled
        return super().flags(idx)

    def setData(self, idx: QModelIndex, value, role: int = Qt.EditRole):
        if not idx.isValid():
            return False

        if role == Qt.CheckStateRole and idx.column() == Column.Enable:
            enable = value == Qt.Checked
            if self._actions[idx.row()].enabled != enable:
                self.enableAction(idx.row(), enable)
            return False

        if role == Qt.EditRole and idx.column() == Column.Status:
            if self._actions[idx.row()].status != value:
                self._actions[idx.row()].status = value
                self.dataChanged.emit(idx, idx, [Qt.DisplayRole])
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
                return
            elif role == Qt.CheckStateRole:
                if self.isAllEnabled():
                    return Qt.Checked
                if self.isNoneEnabled():
                    return Qt.Unchecked
                return Qt.PartiallyChecked
        return super().headerData(section, orientation, role)

    def setAllActionsEnabled(self, on: bool):
        for i in range(len(self._actions)):
            self._actions[i].enabled = on
        self.dataChanged.emit(
            self.index(0, Column.Enable), self.index(self.rowCount() - 1, Column.Enable), [Qt.CheckStateRole]
        )
        self.headerDataChanged.emit(Qt.Horizontal, Column.Enable, Column.Enable)

    def enableAction(self, row, enable):
        self._actions[row].enabled = enable
        anyEnabled = False
        for a in self._actions:
            if a.enabled and not a.required:
                anyEnabled = True
                break
        for a in self._actions:
            if a.required:
                a.enabled = anyEnabled
        self.headerDataChanged.emit(Qt.Horizontal, Column.Enable, Column.Action)

    def toggleAll(self):
        self.setAllActionsEnabled(not self.isAllEnabled())

    def isAllEnabled(self):
        for a in self._actions:
            if not a.enabled:
                return False
        return True

    def isAnyEnabled(self):
        for a in self._actions:
            if a.enabled:
                return True
        return False

    def isNoneEnabled(self):
        return not self.isAnyEnabled()

    def isEnabled(self, action: Action):
        return self._actions[action].enabled

    def setStatus(self, action: Action, status: Status):
        self.setData(self.index(action.id, Column.Status), status)

    def setEnabled(self, action: Action, enable: bool):
        self.setData(self.index(action.id, Column.Enable), enable, Qt.CheckStateRole)

    # ----
    # ---- Log interface
    # ----

    def log(self, level: LogLevel, action: Action, msg: str):
        self.logMessage.emit(level, action.name, msg)
        QCoreApplication.processEvents()

    def info(self, action: Action, msg: str):
        self.log(LogLevel.Info, action, msg)

    def warn(self, action: Action, msg: str):
        self.log(LogLevel.Warn, action, msg)

    def error(self, action: Action, msg: str):
        self.log(LogLevel.Error, action, msg)

    def success(self, action: Action, msg: str):
        self.log(LogLevel.Success, action, msg)

    def debug(self, action: Action, msg: str):
        self.log(LogLevel.Debug, action, msg)

    def logStatus(self, action: Action):
        if action.status == Status.Working:
            self.debug(action, self.tr("Started action."))
        elif action.status == Status.Skipped:
            self.debug(action, self.tr("Skipped action."))
        elif action.status == Status.Success:
            self.debug(action, self.tr("Completed action."))
        elif action.status == Status.Cancelled:
            self.debug(action, self.tr("Cancelled action."))
        elif action.status == Status.Failed:
            self.error(action, self.tr("Action failed. Cancelling any remaining actions."))

    # ----
    # ---- Methods related to performing actions
    # ----

    def applyActions(self, profile=None):
        self.started.emit()
        self._profile = profile
        for a in self._actions:
            self.setStatus(a, Status.NotStarted)

        cancel = False
        for action in self._actions:
            if not action.enabled:
                self.setActionStatus(action, Status.Skipped)
            else:
                if cancel and not action.required:
                    self.setActionStatus(action, Status.Cancelled)
                    self._profileMgr.removeBackup(self._profile)
                else:
                    self.setActionStatus(action, Status.Working)
                    action.function(action)
                    if action.status == Status.Failed:
                        cancel = True
        self.finished.emit()

    def setActionStatus(self, action: Action, status: Status):
        self.setStatus(action, status)
        self.logStatus(action)

    # ----
    # ---- The implementations for the actions functions.
    # ----
    # ---- Each function must update the final status for its action.
    # ----

    def initializeActions(self, action: Action):
        self._createdNewProfile = False
        if not self._profileMgr.profileExists(self._profile):
            if self._profileMgr.createProfile(self._profile):
                self.info(action, "Created new profile.")
                self._createdNewProfile = True
            else:
                self.error(action, "Failed to create profile")
                self.setActionStatus(action, Status.Failed)
                return
        else:
            if self._profileMgr.backupFiles(self._profile):
                self.info(action, "Backed up files from profile.")
            else:
                self.error(action, "Failed to backup files from profile")
                self.setActionStatus(action, Status.Failed)
                return
        self.setActionStatus(action, Status.Success)

    def finalizeActions(self, action: Action):
        # This is a required action.  But we only execute it if initialize
        # completed successfully.

        if self._actions[Action.Initialize].status != Status.Success:
            self.setActionStatus(action, Status.Cancelled)
            return

        # we only need to do this if a previous action was performed
        didNothing = True
        for a in self._actions:
            if a.id == Action.Initialize or a.id == Action.Finalize:
                continue
            if a.status == Status.Success or a.status == Status.Failed:
                didNothing = False
                break
        if didNothing:
            self.setActionStatus(action, Status.Skipped)

        self._pluginModel.updatePluginStates()
        self.info(action, "Updated plugin states in MergeWizard.")

        if a.status == Status.Failed:
            if self._profileMgr.restoreBackup(self._profile):
                self._profileMgr.removeBackup(self._profile)
                self.info(action, "Restored files to profile from backup.")
                self.setActionStatus(action.Status.Success)
            else:
                self.warn(action, "Failed to restore backup files to profile.")
                self.setActionStatus(action, Status.Failed)
            return

        self.setActionStatus(action, Status.Success)

    def enableSelected(self, action: Action):
        self.enableRows(action, self._pluginModel.selectedRows())

    def enableMasters(self, action: Action):
        self.enableRows(action, self._pluginModel.selectedMasters())

    def disableOthers(self, action: Action):
        selected = self._pluginModel.selectedRows()
        masters = self._pluginModel.selectedMasters()
        total = self._pluginModel.rowCount()
        rows = [i for i in range(total) if i not in selected and i not in masters]
        self.disableRows(action, rows)

    def enableRows(self, action: Action, rows: List[int]):
        if len(rows) == 0:
            self.info(action, "Not enabling plugins. No plugins are selected.")
            self.setActionStatus(action, Status.Skipped)
            return

        missing = 0
        active = 0
        rowsToChange = []
        for row in rows:
            plugin = self._pluginModel.data(self._pluginModel.index(row, 0), PluginRole.Data)
            if plugin.isMissing:
                missing = missing + 1
            elif not plugin.isInactive:
                active = active + 1
            else:
                rowsToChange.append(row)
        if missing:
            self.warn(action, "Not enabling {} missing plugin(s)".format(missing))
        if not rowsToChange:
            self.info(action, "No plugins require enabling.")
            self.setActionStatus(action, Status.Skipped)
            return
        self.info(action, "Enabling {} of {} plugin(s).".format(len(rowsToChange), len(rows)))
        for row in rowsToChange:
            self._pluginModel.activatePlugin(row)
        self.setActionStatus(action, Status.Success)

    def disableRows(self, action: Action, rows: List[int]):
        if len(rows) == 0:
            self.info(action, "Not disabling plugins. No plugins to disable.")
            self.setActionStatus(action, Status.Skipped)
            return

        missing = 0
        inactive = 0
        rowsToChange = []
        for row in rows:
            plugin = self._pluginModel.data(self._pluginModel.index(row, 0), PluginRole.Data)
            if plugin.isMissing:
                missing = missing + 1
            elif plugin.isInactive:
                inactive = inactive + 1
            else:
                rowsToChange.append(row)
        if missing:
            self.debug(action, "Not disabling {} missing plugin(s)".format(missing))
        if not rowsToChange:
            self.info(action, "No plugins require disabling.")
            self.setActionStatus(action, Status.Skipped)
            return
        self.info(action, "Disabling {} of {} plugin(s).".format(len(rowsToChange), len(rows)))
        for row in rowsToChange:
            self._pluginModel.deactivatePlugin(row)
        self.setActionStatus(action, Status.Success)

    def moveSelected(self, action: Action):
        if self._pluginModel.selectedCount() == 0:
            self.info(action, "Not moving plugins. no plugins are selected.")
            self.setActionStatus(action, Status.Skipped)
            return

        selected = self._pluginModel.selectedRows()
        priority = self._pluginModel.maxPriority()
        missing = 0
        needToMove = []
        for row in reversed(selected):
            plugin = self._pluginModel.data(self._pluginModel.index(row, 0), PluginRole.Data)
            if plugin.isMissing:
                missing = missing + 1
            elif plugin.priority != priority:
                needToMove.append(row)
            priority = priority = 1
        if missing:
            self.warn(action, "Not moving {} missing plugin(s)".format(missing))
        if not needToMove:
            self.info(action, "No plugins require moving.")
            self.setActionStatus(action, Status.Skipped)
            return
        self.info(
            action, "Moving {} of {} plugin(s). (Other plugins may be affected.)".format(len(needToMove), len(selected))
        )
        self._pluginModel.movePlugins(selected)
        self.setActionStatus(action, Status.Success)

    def deactivateMods(self, action: Action):
        total, toChange = self._pluginModel.getModStats()
        if not toChange:
            self.info(action, "No mods require deactivating.")
            self.setActionStatus(action, Status.Skipped)
            return
        self.info(action, "Deactivating {} of {} mods".format(toChange, total))
        self._pluginModel.deactivateUnneededMods()
        self.setActionStatus(action, Status.Success)

