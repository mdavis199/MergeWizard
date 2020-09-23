from enum import IntEnum
from typing import List
from PyQt5.QtCore import pyqtSignal, QObject, QModelIndex, qInfo, qDebug
from mobase import IOrganizer, PluginState, ModState
from mergewizard.domain.ILogger import Status as LogStatus
from mergewizard.models.PluginModelBase import PluginModelBase, Column


"""
NOTE: Impact of changing plugin states (presently MO is not signaling changes in states)

-- Enabling/Disabling plugin changes:
    -- isActive for the specific plugin
    -- priority for all plugins with lower priority
-- Moving plugins:
    -- changes priority of basically all plugins
-- Deactivating mod:
    -- changes priority of basically all plugins
    -- changes isMissing, UNLESS an enabled mod with higher priority has a
       plugin of the same name. (WILL HAVE QUERY or REBUILD THE DATA)
    -- plugin relationhips will NOT change
-- Deactivating a mod that has a merge.json file:  (in addition to above)
    -- will need to remove all plugins in that mod from the merge relationships
-- Hiding/Unhiding plugins:
    -- Similarly to deactivating a plugin, could change isMissing and could reveal a plugin of the same name
    -- Changes priority of plugins




NOTE:  Presently, Plugin relationships are ordered by priority.
This makes it easier to display but impossible to maintain, because everywhere above
that says priority changes, means the Plugin Relationships change.
"""


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
        state = self._organizer.pluginList().state(plugin.pluginName)
        if state == PluginState.INACTIVE:
            idx = self.index(row, Column.IsInactive)
            self.setData(idx, True)
        return plugin.isInactive

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

    def updatePluginStates(self):
        for row in range(len(self._plugins)):
            self.updatePluginState(row)

    def updatePluginState(self, row: int):
        plugin = self._plugins[row]
        priority = self._organizer.pluginList().priority(plugin.pluginName)
        state = self._organizer.pluginList().state(plugin.pluginName)
        isMissing = state == PluginState.MISSING
        isInactive = not isMissing and state != PluginState.ACTIVE
        if plugin.isInactive != isInactive or plugin.isMissing != isMissing or plugin.priority != priority:
            plugin.isInactive = isInactive
            plugin.isMissing = isMissing
            plugin.priority = priority
            self.dataChanged.emit(self.index(row, Column.Priority), self.index(row, Column.IsInactive))

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
        if modsToRemove:
            self.disableMods(list(modsToRemove))

    def getModStats(self):
        """ This is for the action model.
        It's duplicating work in the function above; but these take little time and the
        actions for the actionModel do not need to be super fast"""
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
        return (len(activeMods), len(activeMods) - len(modsToKeep))

    # ------------------------------------------------
    # ---- Methods for logging and MO2 callbacks
    # ------------------------------------------------

    def onRefreshed(self):
        qDebug("OnRefreshed")
        # self.log.emit("ModOrganizer refreshed the plugin list", LogStatus.Debug)

    def onPluginMoved(self, name, old, new):
        qDebug("OnPluginMoved")
        """
        self.log.emit("Plugin {}: load order moved from {} to {}".format(name, old, new), LogStatus.Debug)
        idxName = self.indexForPluginName(name)
        idx = idxName.siblingAtColumn(Column.Priority)
        qDebug(
            "...before idx: r:{}, c:{}, name: {}, val: {}".format(
                idx.row(), idx.column(), self.data(idxName), self.data(idx)
            )
        )
        self.setData(idx, new)
        qDebug("...after idx: r:{}, c:{}, val: {}".format(idx.row(), idx.column(), self.data(idx)))
        """

    def onPluginStateChanged(self, name, state):
        qDebug("onPluginStateChanged")
        # self.log.emit("Plugin {}: changed to {}".format(name, state), LogStatus.Debug)

    def onModStateChanged(self, stateDict):
        qDebug("onModStateChanged")
        # active = (state & ModState.Active) == ModState.Active
        """
        ModStateActive = 2
        for name in stateDict:
            active = (stateDict[name] & ModStateActive) == ModStateActive
            self.log.emit(
                "Mod: {} changed (active? {}, state: {})".format(name, active, stateDict[name]), LogStatus.Debug
            )
        """
