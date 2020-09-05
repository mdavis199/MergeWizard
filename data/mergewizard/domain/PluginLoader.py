from typing import List, Dict, Callable
from PyQt5.QtCore import QObject, QDir, QFileInfo, pyqtSignal
from mobase import IOrganizer, PluginState
from mergewizard.domain.Plugin import Plugin


class MastersLoader(QObject):
    progressBump = pyqtSignal()

    def __init__(self, organizer: IOrganizer):
        super().__init__()
        self.organizer = organizer
        self.pluginMap: Dict[str, Plugin] = {}
        self.processed: List[str] = []

    def loadMasters(self, plugins: List[Plugin]):
        self.pluginMap = {plugin.key(): plugin for plugin in plugins}
        for plugin in plugins:
            self.loadMastersRecursively(plugin)
            self.progressBump.emit()
        for plugin in self.pluginMap.values():
            plugin.sortRequired()
            self.progressBump.emit()
        return list(self.pluginMap.values())

    def loadMastersRecursively(self, plugin: Plugin):
        if plugin.key() in self.processed:
            return
        self.processed.append(plugin.key())

        for name in self.organizer.pluginList().masters(plugin.pluginName):
            masterPlugin = self.pluginMap.setdefault(name.lower(), Plugin(name, False))  # False => not MOPlugin
            plugin.addMaster(masterPlugin, True)  # True => isDirect
            self.loadMastersRecursively(masterPlugin)
            for indirectPlugin, _ in masterPlugin.requires:
                plugin.addMaster(indirectPlugin, False)  # False => not isDirect


class PluginLoader(QObject):
    progressBump = pyqtSignal()

    def __init__(self, organizer: IOrganizer):
        super().__init__()
        self.__organizer = organizer

    def loadPlugins(self, pluginNames: List[str] = None) -> List[Plugin]:
        if not pluginNames:
            pluginNames = self.__organizer.pluginList().pluginNames()
        return [self.loadPlugin(name) for name in pluginNames]

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
            # plugin.isMerge = self.isModMerged(plugin.modPath)
        self.progressBump.emit()
        return plugin

    # similar to how deorder's hideplugins determines if a mod is a merge
    def isModMerged(self, modPath: str) -> bool:
        return True if self.getMergeFiles(modPath) else False

    def getMergeFiles(self, modPath: str):
        if not modPath:
            return
        modDir = QDir(modPath)
        if not modDir.exists():
            return
        dirs = modDir.entryList(["merge*"], QDir.Dirs)
        if not dirs:
            return
        for d in dirs:
            fileInfo = QFileInfo(modDir, d)
            mergeDir = QDir(fileInfo.absoluteFilePath())
            return mergeDir.entryList(["merge.json", "*_plugins.txt"], QDir.Files)


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


class AsyncPluginLoader:
    @staticmethod
    def loadPlugins(organizer: IOrganizer, progress_callback: Callable[[], int] = None) -> List[Plugin]:
        names = organizer.pluginList().pluginNames()
        pluginLoader = PluginLoader(organizer)
        mastersLoader = MastersLoader(organizer)
        progressEmitter = ProgressEmitter(progress_callback, len(names) * 3)
        pluginLoader.progressBump.connect(progressEmitter.bump)
        mastersLoader.progressBump.connect(progressEmitter.bump)
        plugins = pluginLoader.loadPlugins(names)
        plugins = mastersLoader.loadMasters(plugins)
        progressEmitter.end()
        return plugins
