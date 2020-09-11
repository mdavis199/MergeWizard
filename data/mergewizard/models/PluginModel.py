from enum import IntEnum
from typing import List
from PyQt5.QtCore import (
    pyqtSignal,
    QObject,
    QModelIndex,
    qInfo,
)
from mobase import IOrganizer, PluginState, ModState
from mergewizard.domain.ILogger import Status as LogStatus
from mergewizard.models.PluginModelBase import PluginModelBase, Column


class PluginModel(PluginModelBase):
    """
        This class builds on the base model by adding functionality
        requiring the MO2 interface
    """

    log = pyqtSignal(str, LogStatus)

    def __init__(self, organizer: IOrganizer, parent: QObject = None):
        super().__init__(parent)
        self._organizer = organizer
        self._isLoading = False

        organizer.pluginList().onRefreshed(self.onRefreshed)
        organizer.pluginList().onPluginMoved(self.onPluginMoved)
        organizer.pluginList().onPluginStateChanged(self.onPluginStateChanged)
        organizer.modList().onModStateChanged(self.onModStateChanged)

    # ------------------------------------------------
    # ---- Adding info from MergeModel
    # ------------------------------------------------
    """
    def addMergeInfo(self, merges: List[Merge]):
        missingMerges = []
        missingMerged = []
        for merge in merges:
            mergeName = merge.lower()
            row = next((i for i in range(len(self._plugins)) if mergeName == self._plugins[i].pluginName), -1)
            if row >= 0:
                self.setData(self.index(row, Column.IsMerge), True, Qt.EditRole)
            else:
                missingMerges.append(merge.name)
            for plug in merge.plugins:
                plugName = plug.lower()
                row2 = next((j for j in range(len(self._plugins)) if plugName == self.__plugins[j].pluginName), -1)
                if row2 >= 0:
                    self.setData(self.index(row2.Column.IsMerged), True, Qt.EditRole)
                else:
                    missingMerged.append(plug)
    """
    # ------------------------------------------------
    # ---- MO Interactions
    # ------------------------------------------------

    def activatePlugin(self, row: int):
        plugin = self._plugins[row]
        if not plugin.isInactive:
            return True
        if plugin.isMissing:
            return False
        self._organizer.pluginList().setState(plugin.pluginName, PluginState.ACTIVE)
        state = self._organizer.pluginList().state(plugin.pluginName)
        if state == PluginState.ACTIVE:
            idx = self.index(row, Column.IsInactive)
            self.setData(idx, False)
        return not plugin.isInactive

    def deactivatePlugin(self, row: int):
        plugin = self._plugins[row]
        if plugin.isInactive:
            return True
        if plugin.isMissing:
            return False
        self._organizer.pluginList().setState(plugin.pluginName, PluginState.INACTIVE)
        state = self._organizer.pluginList().state(plugin.pluginName)
        if state == PluginState.INACTIVE:
            idx = self.index(row, Column.IsInactive)
            self.setData(idx, True)
        return plugin.isInactive

    # TODO: refresh list
    def movePlugins(self, rows: List[str]):
        priority = self.maxPriority()
        qInfo("Moving {} plugins, max priority is : {}".format(len(rows), priority))
        for row in reversed(rows):
            plugin = self._plugins[row]
            if plugin.priority != priority:
                self._organizer.pluginList().setPriority(plugin.pluginName, priority)
            priority = priority - 1

    # TODO: refresh list
    def disableMods(self, names: List[str]):
        self._organizer.modList().setActive(names, False)

    # ------------------------------------------------
    # ---- In case we want to allow activating/deactivating by context menu
    # ------------------------------------------------

    def activatePlugins(self, indexes: List[QModelIndex]):
        for idx in indexes:
            if idx.isValid():
                self.activatePlugin(idx.row())

    def deactivatePlugins(self, indexes: List[QModelIndex]):
        for idx in indexes:
            if idx.isValid():
                self.deactivatePlugin(idx.row())

    # ------------------------------------------------
    # ---- Methods for Actions
    # ------------------------------------------------

    class ActionStatus(IntEnum):
        Completed = 0
        Skipped = 1

    def enableSelected(self):
        if not self._selected:
            self.log.emit("Not enabling selected plugins. No plugins are selected.", LogStatus.Info)
            return self.ActionStatus.Skipped
        rowsToEnable = []
        rowsMissing = []
        rowsAlreadyEnabled = []
        for row in self._selected:
            if self._plugins[row].isMissing:
                rowsMissing.append(row)
            elif self._plugins[row].isInactive:
                rowsToEnable.append(row)
            else:
                rowsAlreadyEnabled.append(row)
        if rowsMissing:
            self.log.emit("Not enabling {} missing selected plugin(s).".format(len(rowsMissing)), LogStatus.Warn)
        if not rowsToEnable:
            self.log.emit("No plugins require enabling.", LogStatus.Info)
            return self.ActionStatus.Skipped

        self.log.emit(
            "Enabling {} of {} selected plugin(s).".format(len(rowsToEnable), len(self._selected)), LogStatus.Info
        )
        for row in rowsToEnable:
            self.activatePlugin(row)
        return self.ActionStatus.Completed

    def enableMasters(self):
        if not self._masters:
            self.log.emit("Not enabling masters. No masters are selected.", LogStatus.Info)
            return self.ActionStatus.Skipped
        rowsToEnable = []
        rowsMissing = []
        rowsAlreadyEnabled = []
        for row in self._masters:
            if self._plugins[row].isMissing:
                rowsMissing.append(row)
            elif self._plugins[row].isInactive:
                rowsToEnable.append(row)
            else:
                rowsAlreadyEnabled.append(row)
        if rowsMissing:
            self.log.emit("Not enabling {} missing master(s).".format(len(rowsMissing)), LogStatus.Warn)
        if not rowsToEnable:
            self.log.emit("No masters require enabling.", LogStatus.Info)
            return self.ActionStatus.Skipped

        self.log.emit(
            "Enabling {} of {} plugin master(s).".format(len(rowsToEnable), len(self._masters)), LogStatus.Info
        )
        for row in rowsToEnable:
            self.activatePlugin(row)
        return self.ActionStatus.Completed

    def disableOthers(self):
        rowsToDisable = []
        for row in range(len(self._plugins)):
            plugin = self._plugins[row]
            if not plugin.isSelected and not plugin.isSelectedAsMaster:
                if not plugin.isInactive and not plugin.priority < 0:
                    rowsToDisable.append(row)
        if not rowsToDisable:
            self.log.emit("Not disabling plugins. No plugins to disable.", LogStatus.Info)
            return self.ActionStatus.Skipped

        self.log.emit("Disabling {} plugin(s).".format(len(rowsToDisable)), LogStatus.Info)
        for row in rowsToDisable:
            self.deactivatePlugin(row)
        return self.ActionStatus.Completed

    def moveSelected(self):
        if not self._selected:
            self.log.emit("Not moving plugins. No plugins are selected.", LogStatus.Info)
            return self.ActionStatus.Skipped
        rowsToMove = []
        rowsMissing = []
        for row in self._selected:
            if self._plugins[row].isMissing:
                rowsMissing.append(row)
            else:
                rowsToMove.append(row)
        if rowsMissing:
            self.log.emit("Not moving {} missing plugin(s).".format(len(rowsMissing)), LogStatus.Warn)
        if not rowsToMove:
            self.log.emit("There are no plugins to move.", LogStatus.Info)
            return self.ActionStatus.Skipped
        self.log.emit("Adjusting priority of {} selected plugin(s).".format(len(rowsToMove)), LogStatus.Info)
        self.movePlugins(rowsToMove)
        return self.ActionStatus.Completed

    def maxPriority(self):
        if not self._plugins:
            return -1
        return max(plugin.priority for plugin in self._plugins.values())

    def deactivateUnneededMods(self):
        # this will require a reload of the pluginModel, because plugin
        # priorities will change and plugins will be removed from the plugin list
        modsToKeep = {
            plugin.modName
            for plugin in self._plugins.values()
            if (plugin.isSelected or plugin.isSelectedAsMaster) and not plugin.isMissing
        }
        activeMods = {
            mod
            for mod in self._organizer.modList().allMods()
            if self._organizer.modList().state(mod) & ModState.ACTIVE == ModState.ACTIVE
        }
        modsToRemove = activeMods - modsToKeep
        if not modsToRemove:
            self.log.emit("There are no mods to deactivate.", LogStatus.Info)
            return self.ActionStatus.Skipped
        self.log.emit("Deactivating {} mods.".format(len(modsToRemove)), LogStatus.Info)
        self.disableMods(list(modsToRemove))
        return self.ActionStatus.Completed

    # ------------------------------------------------
    # ---- Methods for logging and MO2 callbacks
    # ------------------------------------------------

    def onRefreshed(self):
        qInfo("OnRefreshed")
        self.log.emit("ModOrganizer refreshed the plugin list", LogStatus.Info)

    def onPluginMoved(self, name, old, new):
        qInfo("OnPluginMoved")
        self.log.emit("Plugin {}: load order moved from {} to {}".format(name, old, new), LogStatus.Info)

    def onPluginStateChanged(self, name, state):
        qInfo("onPluginStateChanged")
        self.log.emit("Plugin {}: changed to {}".format(name, state), LogStatus.Info)

    def onModStateChanged(self, stateDict):
        qInfo("onModStateChanged")
        # active = (state & ModState.Active) == ModState.Active
        ModStateActive = 2
        for name in stateDict:
            active = (stateDict[name] & ModStateActive) == ModStateActive
            self.log.emit(
                "Mod: {} changed (active? {}, state: {})".format(name, active, stateDict[name]), LogStatus.Info
            )
