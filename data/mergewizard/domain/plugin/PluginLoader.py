from typing import Callable
from PyQt5.QtCore import QObject, pyqtSlot
from mobase import IOrganizer, PluginState
from mergewizard.domain.plugin.Plugin import Plugin
from mergewizard.domain.plugin.Plugins import Plugins


class ProgressEmitter(QObject):
    def __init__(self, callback: Callable[[], int] = None, maxValue=0):
        super().__init__()
        self.callback = callback
        self.maxValue = maxValue
        self.value = 0

    def setMaxValue(self, value):
        self.maxValue = value

    @pyqtSlot()
    def bump(self):
        self.value = self.value + 1
        if self.callback and self.maxValue:
            self.callback.emit(self.value * 100 / self.maxValue)

    def end(self) -> None:
        self.value = self.maxValue
        if self.callback:
            self.callback.emit(100)


class PluginDataLoader(QObject):
    """ Loads all plugins that MO2 knows about. """

    def __init__(self, organizer: IOrganizer, callback: Callable[[], int]):
        super().__init__()
        self.__organizer = organizer
        self.progressEmitter = ProgressEmitter(callback)

    def loadPlugins(self) -> Plugins:
        """ Constructs a Plugin for each name with data from MO2 and adds it
        to the Plugins data structure.

        The names are iterated twice:
        1. Constructs the plugin as an MO-plugin with data from MO2
        2. Adds relationships between the plugin and its required plugins. For any
        required plugin that is not in the list of names, a Plugin is constructed
        as "non-MO/missing" and added to the Plugins structure.
        """
        pluginNames = self.__organizer.pluginList().pluginNames()
        self.progressEmitter.maxValue = len(pluginNames) * 2

        plugins = Plugins()
        if pluginNames is None:
            pluginNames = self.__organizer.pluginList().pluginNames()
        for name in pluginNames:
            plugins.add(self.loadPlugin(name))
            self.bumpProgress()
        for name in pluginNames:
            self.bumpProgress()
            for requirement in self.__organizer.pluginList().masters(name):
                plugins.addRequirement(plugins.get(name), plugins.get(requirement, False))
        self.progressEmitter.end()
        return plugins

    def bumpProgress(self):
        self.progressEmitter.bump()

    def loadPlugin(self, name: str) -> Plugin:
        plugin = Plugin(name)
        plugin.priority = self.__organizer.pluginList().priority(name)
        plugin.isMaster = self.__organizer.pluginList().isMaster(name)
        state = self.__organizer.pluginList().state(name)
        plugin.isInactive = state != PluginState.ACTIVE
        plugin.isMissing = state == PluginState.MISSING
        mod = self.__organizer.getMod(self.__organizer.pluginList().origin(name))
        if mod:
            plugin.modName = mod.name()
            plugin.modPath = mod.absolutePath()
        return plugin


class PluginLoader:
    @staticmethod
    def loadPlugins(organizer: IOrganizer, progress_callback: Callable[[], int] = None) -> Plugins:
        pluginLoader = PluginDataLoader(organizer, progress_callback)
        plugins = pluginLoader.loadPlugins()
        return plugins
