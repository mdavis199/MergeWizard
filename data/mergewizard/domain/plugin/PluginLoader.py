from typing import List, Callable, Optional
from PyQt5.QtCore import QObject, pyqtSignal
from mobase import IOrganizer, PluginState
from mergewizard.domain.plugin.Plugin import Plugin
from mergewizard.domain.plugin.Plugins import Plugins


class PluginDataLoader(QObject):
    """ Loads all plugins that MO2 knows about. """

    progressBump = pyqtSignal()

    def __init__(self, organizer: IOrganizer):
        super().__init__()
        self.__organizer = organizer

    def loadPlugins(self, pluginNames: Optional[List[str]] = None) -> Plugins:
        """ Constructs a Plugin for each name with data from MO2 and adds it
        to the Plugins data structure.

        The names are iterated twice:
        1. Constructs the plugin as an MO-plugin with data from MO2
        2. Adds relationships between the plugin and its required plugins. For any
        required plugin that is not in the list of names, a Plugin is constructed
        as "non-MO/missing" and added to the Plugins structure.
        """
        plugins = Plugins()
        if pluginNames is None:
            pluginNames = self.__organizer.pluginList().pluginNames()
        for name in pluginNames:
            plugins.add(self.loadPlugin(name))
            self.progressBump.emit()
        for name in pluginNames:
            self.progressBump.emit()
            for requirement in self.__organizer.pluginList().masters(name):
                plugins.addRequirement(plugins.get(name), plugins.get(requirement, False))
        return plugins

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


class ProgressEmitter(QObject):
    def __init__(self, callback: Callable[[], int] = None, maxValue=0):
        self.reset(callback, maxValue)

    def reset(self, callback: Callable[[], int] = None, maxValue=0):
        self.callback = callback
        self.maxValue = maxValue
        self.value = 0

    def bump(self, amount: int = 1) -> None:
        self.value = self.value + amount
        if self.callback and self.maxValue:
            self.callback.emit(self.value * 100 / self.maxValue)

    def end(self) -> None:
        self.value = self.maxValue
        if self.callback:
            self.callback.emit(100)


class PluginLoader:
    @staticmethod
    def loadPlugins(
        organizer: IOrganizer, names: Optional[List[str]] = None, progress_callback: Callable[[], int] = None
    ) -> Plugins:
        if names is None:
            names = organizer.pluginList().pluginNames()
        pluginLoader = PluginDataLoader(organizer)
        progressEmitter = ProgressEmitter(progress_callback, len(names) * 2)
        pluginLoader.progressBump.connect(progressEmitter.bump)
        plugins = pluginLoader.loadPlugins(names)
        progressEmitter.end()
        return plugins
