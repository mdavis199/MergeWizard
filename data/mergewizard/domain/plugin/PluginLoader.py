from PyQt5.QtCore import QThread, pyqtSignal
from mobase import IOrganizer, PluginState
from mergewizard.domain.plugin.Plugin import Plugin
from mergewizard.domain.plugin.Plugins import Plugins


class PluginLoader(QThread):
    """ Loads all plugins that MO2 knows about. """

    progress = pyqtSignal(int)
    result = pyqtSignal(object)

    def __init__(self, organizer: IOrganizer):
        super().__init__()
        self.__organizer = organizer
        self._stopped = False

    def stop(self):
        self._stopped = True

    def run(self) -> Plugins:
        """ Constructs a Plugin for each name with data from MO2 and adds it
        to the Plugins data structure.

        The names are iterated twice:
        1. Constructs the plugin as an MO-plugin with data from MO2
        2. Adds relationships between the plugin and its required plugins. For any
        required plugin that is not in the list of names, a Plugin is constructed
        as "non-MO/missing" and added to the Plugins structure.
        """
        pluginNames = self.__organizer.pluginList().pluginNames()
        self._total = len(pluginNames) * 2
        self._count = 0
        self._progress = 0

        plugins = Plugins()
        if pluginNames is None:
            pluginNames = self.__organizer.pluginList().pluginNames()
        for name in pluginNames:
            if self._stopped:
                return
            self.emitProgress()
            plugins.add(self.loadPlugin(name))
        for name in pluginNames:
            self.emitProgress()
            for requirement in self.__organizer.pluginList().masters(name):
                if self._stopped:
                    return
                plugins.addRequirement(plugins.get(name), plugins.get(requirement, False))
        self.result.emit(plugins)

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

    def emitProgress(self):
        # QThread.usleep(1)
        self._count = self._count + 1
        v = int(self._count * 100 / self._total)
        if v != self._progress:
            self._progress = v
            self.progress.emit(v)
