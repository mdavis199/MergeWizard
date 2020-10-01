from typing import Set, List
from time import perf_counter
from glob import glob, escape
from PyQt5.QtCore import QThread, pyqtSignal
from mobase import IOrganizer, PluginState, ModState
from mergewizard.domain.plugin.Plugin import Plugin
from mergewizard.domain.plugin.Plugins import Plugins
from mergewizard.domain.merge.MergeFile import MergeFile
from mergewizard.domain.merge.ZEditConfig import ZEditConfig
from mergewizard.domain.mod.Mod import Mod
from mergewizard.domain.MOLog import moWarn, moDebug, moPerf, moTime


class DataLoader(QThread):
    """ Loads all plugins that MO2 knows about. """

    MOD_ACTIVE = int(ModState.ACTIVE)
    progress = pyqtSignal(int)
    result = pyqtSignal(object)

    def __init__(self, organizer: IOrganizer):
        super().__init__()
        self.__organizer = organizer
        self._enableLoadingMergeFiles = False
        self._enableLoadingProfile = False
        self._onlyActiveMerges = False

        self._stopped: bool = False
        self._plugins: Plugins = None
        self._pluginNames: List[str] = None
        self._mergeFiles: List[MergeFile] = None
        self._mods: List[Mod] = None

        # We keep track of the merges we''ve collected. If we already loaded it
        # from the profile, we do not load it from the mod folder.
        self._mergeNames: Set[str] = None

    def loadOnlyActiveMerges(self, onlyActive: bool):
        self._onlyActiveMerges = onlyActive

    def enableLoadingMergeFiles(self, enable: bool):
        self._enableLoadingMergeFiles = enable

    def enableLoadingProfile(self, enable: bool, gameName="", profileName="", zeditFolder=""):
        if enable and (not gameName or not profileName or not zeditFolder):
            moWarn("Skipping merges from zEdit profile: Check zEdit settings in MergeWizard's options.")
            self._enableLoadingProfile = False
            return

        self._enableLoadingProfile, self._gameName, self._profileName, self._zeditFolder = (
            enable,
            gameName,
            profileName,
            zeditFolder,
        )

    def stop(self):
        self._stopped = True

    def emitProgress(self):
        self._count = self._count + 1
        v = int(self._count * 100 / self._total)
        if v != self._progress:
            self._progress = v
            self.progress.emit(v)

    # --------------------------------------------------------------------

    def run(self):
        startTime = perf_counter()
        moTime(startTime, "DataLoader.run - started")
        # -------

        self._count = 0
        self._progress = 0
        self._plugins = Plugins()
        self._mergeFiles = []
        self._mods = []
        self._mergeNames = set()

        # first, get enough info to estimate the progress
        self._pluginNames = self.__organizer.pluginList().pluginNames()
        self._total = len(self._pluginNames) * 2

        self._allMods = self.__organizer.modList().allMods()
        self._total += len(self._allMods)

        if self._enableLoadingMergeFiles:
            self._total += len(self._allMods)

        if self._enableLoadingProfile:
            profile = ZEditConfig.loadProfile(self._gameName, self._profileName, self._zeditFolder)
            self._mergeFiles = profile.merges
            self._total += len(self._mergeFiles)

        self.loadPlugins()
        self.loadMods()
        if self._enableLoadingProfile:
            self.loadProfile()  # we've already loaded it; we're just adding data
        if self._enableLoadingMergeFiles:
            self.loadMergeFiles()
        self.result.emit((self._plugins, self._mergeFiles, self._mods))
        # ----------
        moPerf(startTime, perf_counter(), "DataLoader.run - complete")
        self.progress.emit(100)

    # -----------------------------------------------------------------

    def loadMods(self):
        startTime = perf_counter()
        # -------
        for name in self._allMods:
            self.emitProgress()
            if self._stopped:
                return
            priority = self.__organizer.modList().priority(name)
            state = self.__organizer.modList().state(name)
            active = state & ModState.ACTIVE == ModState.ACTIVE
            self._mods.append(Mod(name, priority, active))
        # -------
        moPerf(startTime, perf_counter(), "DataLoader.loadMods - mods loaded: {}".format(len(self._mods)))

    # -----------------------------------------------------------------

    def loadPlugins(self):
        startTime = perf_counter()
        # -------
        plugins = self._plugins
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
        # -------
        moPerf(startTime, perf_counter(), "DataLoader.loadPlugins - plugins loaded: {}".format(len(plugins)))

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

    # -----------------------------------------------------------------

    def loadProfile(self):
        startTime = perf_counter()
        # -------
        for m in self._mergeFiles:
            self.emitProgress()
            self._mergeNames.add(m.modName)
            state = self.__organizer.modList().state(m.name)
            m.modIsActive = state & ModState.ACTIVE == ModState.ACTIVE
            if not self._onlyActiveMerges or m.modIsActive:
                self.addMergeToPlugins(m)
        # -------
        moPerf(startTime, perf_counter(), "DataLoader.loadProfile - merges loaded: {}".format(len(self._mergeFiles)))

    # -----------------------------------------------------------------

    def loadMergeFiles(self):
        startTime = perf_counter()
        count = len(self._mergeNames)
        # -------
        for mod in self._mods:
            self.emitProgress()
            if not self._onlyActiveMerges or mod.active:
                if mod.name not in self._mergeNames:
                    self.loadMergeFileForMod(mod)
        # -------
        count = len(self._mergeNames) - count
        moPerf(startTime, perf_counter(), "DataLoader.loadMergeFiles - files loaded: {}".format(count))

    def loadMergeFileForMod(self, mod: Mod):
        jsonFile = glob(escape(self.__organizer.getMod(mod.name).absolutePath()) + "/merge - */merge.json")
        if jsonFile:
            try:
                mergeFile = self.loadMergeFromFile(jsonFile[0])
                mergeFile.mergeFilePath = jsonFile[0]
                mergeFile.modIsActive = mod.active
                self.addMergeToPlugins(mergeFile)
                self._mergeFiles.append(mergeFile)
                self._mergeNames.add(mergeFile.modName)
            except OSError as ex:
                moWarn('Failed to open mergeFile file "{}": {}'.format(jsonFile, ex.strerror))
            except ValueError as ex:
                moWarn('Failed to read mergeFile file "{}": {}'.format(jsonFile, ex))

    def loadMergeFromFile(self, filepath) -> MergeFile:
        with open(filepath, "r", encoding="utf8") as f:
            merge = MergeFile.fromJSON(f.read())
            return merge

    # -----------------------------------------------------------------

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
