from typing import Set
from os import path
from glob import glob
from PyQt5.QtCore import QThread, pyqtSignal, qInfo
from mobase import IOrganizer, PluginState, ModState
from mergewizard.domain.plugin.Plugin import Plugin
from mergewizard.domain.plugin.Plugins import Plugins
from mergewizard.domain.merge.MergeFile import MergeFile
from mergewizard.domain.MOLog import moWarn


class DataLoader(QThread):
    """ Loads all plugins that MO2 knows about. """

    MOD_ACTIVE = int(ModState.ACTIVE)
    progress = pyqtSignal(int)
    result = pyqtSignal(object)

    def __init__(self, organizer: IOrganizer):
        super().__init__()
        self.__organizer = organizer
        self._stopped = False
        self._plugins = None
        self._pluginNames = None
        self._mergeFiles = None

    def stop(self):
        self._stopped = True

    def run(self):
        # first get enough info to know now how often we
        # should emit progress
        self._pluginNames = self.__organizer.pluginList().pluginNames()
        self._mergeFiles = glob(self.__organizer.modsPath() + "/*/*/merge.json")

        self._total = len(self._pluginNames) * 2 + len(self._mergeFiles)
        self._count = 0
        self._progress = 0

        self.loadPlugins()
        self.loadMergeFiles()
        self.result.emit((self._plugins, self._mergeFiles))

    def loadPlugins(self):
        plugins = Plugins()
        for name in self._pluginNames:
            if self._stopped:
                return
            self.emitProgress()
            plugins.add(self.loadPlugin(name))
        for name in self._pluginNames:
            self.emitProgress()
            for requirement in self.__organizer.pluginList().masters(name):
                if self._stopped:
                    return
                plugins.addRequirement(plugins.get(name), plugins.get(requirement, False))
        self._plugins = plugins

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

    def loadMergeFiles(self):
        mergeFiles: Set[MergeFile] = set()

        for file in self._mergeFiles:
            if self._stopped:
                return
            self.emitProgress()
            try:
                mergeFile = self.loadMergeFromFile(file)
                mergeFile.mergeFilePath = file
                mergeFile.modName = path.basename(path.dirname(path.dirname(file)))
                state: ModState = self.__organizer.modList().state(mergeFile.modName)

                mergeFile.modIsActive = (state & self.MOD_ACTIVE) == self.MOD_ACTIVE
                mergeFiles.add(mergeFile)
                self.addMergeToPlugins(mergeFile)
            except OSError as ex:
                moWarn('Failed to open mergeFile file "{}": {}'.format(file, ex.strerror))
            except ValueError as ex:
                moWarn('Failed to read mergeFile file "{}": {}'.format(file, ex))
        self._mergeFiles = mergeFiles

    def loadMergeFromFile(self, filepath) -> MergeFile:
        with open(filepath, "r", encoding="utf8") as f:
            merge = MergeFile.fromJSON(f.read())
            return merge

    def addMergeToPlugins(self, mergeFile):
        merge = self._plugins.get(mergeFile.filename, False)
        merge.isMerge = True
        merge.mergeFile = mergeFile
        if not merge.modName:
            merge.modName = mergeFile.modName
        for pfd in mergeFile.plugins:
            plugin = self._plugins.get(pfd.filename, False)
            plugin.isMerged = True
            if not plugin.modName:
                plugin.modName = pfd.modName
            self._plugins.addMergeRelationship(merge, plugin)

    def emitProgress(self):
        self._count = self._count + 1
        v = int(self._count * 100 / self._total)
        if v != self._progress:
            self._progress = v
            self.progress.emit(v)
