from copy import deepcopy
from time import perf_counter
from PyQt5.QtCore import pyqtSignal, QObject

from mobase import IOrganizer
from mergewizard.domain.Settings import Settings
from mergewizard.domain.plugin import Plugins
from mergewizard.domain.DataLoader import DataLoader
from mergewizard.domain.MOLog import moPerf, moTime
from mergewizard.models.PluginModel import PluginModel
from mergewizard.models.MergeModel import MergeModel
from mergewizard.constants import Setting


class DataCache(QObject):

    dataLoadingStarted = pyqtSignal()
    dataLoadingProgress = pyqtSignal(int)
    dataLoadingCompleted = pyqtSignal()

    def __init__(self, organizer: IOrganizer):
        super().__init__()
        self._organizer: IOrganizer = organizer
        self._mergeModel: MergeModel = MergeModel()
        self._pluginModel: PluginModel = PluginModel(organizer)
        self._dataLoader: DataLoader = None

        self._dataLoadingStartTime: float = 0

        # CACHED Data
        self.__mods = None
        self.__merges = None
        self.__plugins: Plugins = None

    # --------------------------------------------------------

    @property
    def mergeModel(self) -> MergeModel:
        return self._mergeModel

    @property
    def pluginModel(self) -> PluginModel:
        return self._pluginModel

    @property
    def organizer(self) -> IOrganizer:
        return self._organizer

    @property
    def isLoading(self) -> bool:
        return self._dataLoader and self._dataLoader.isRunning()

    """ These two properties are for the action model only """

    @property
    def cachedMods(self):
        return deepcopy(self.__mods)

    @property
    def cachedPlugins(self):
        return deepcopy(list(self.__plugins.values()))

    # --------------------------------------------------------

    def stopLoading(self) -> None:
        if self.isLoading:
            self._dataLoader.stop()

    def loadData(self, gameName: str, settings: Settings) -> None:
        if self.isLoading:
            return

        loadFiles = settings[Setting.ENABLE_LOADING_ZMERGE]
        activeOnly = settings[Setting.EXCLUDE_INACTIVE_MODS]
        loadProfile = settings[Setting.ENABLE_ZMERGE_INTEGRATION]
        zeditFolder = settings[Setting.ZEDIT_FOLDER]
        zeditProfile = settings[Setting.ZEDIT_PROFILE]

        self._dataLoader = DataLoader(self._organizer)
        self._dataLoader.loadOnlyActiveMerges(activeOnly)
        self._dataLoader.enableLoadingMergeFiles(loadFiles)
        self._dataLoader.enableLoadingProfile(loadProfile, gameName, zeditProfile, zeditFolder)
        self._dataLoader.finished.connect(self._finishedLoadingData)
        self._dataLoader.result.connect(self._setData)
        self._dataLoader.started.connect(self.dataLoadingStarted)
        self._dataLoader.progress.connect(self.dataLoadingProgress)

        self._dataLoadingStartTime = perf_counter()
        moTime(self._dataLoadingStartTime, "DataCache.loadData - started")
        self._dataLoader.start()

    def _finishedLoadingData(self) -> None:
        self._dataLoader.disconnect()
        self._dataLoader = None
        moPerf(self._dataLoadingStartTime, perf_counter(), "DataCache.loadData - complete")
        self.dataLoadingCompleted.emit()

    # ------------------------------------------------
    # Combine the info from the merge model into the
    # plugin model
    #
    # NOTE: We probably do not need the MergeModel now. We can use the
    # PluginModel with the MergeRelationships.  For now, keeping it.  If we have
    # to reload the plugins, we would not need to reload the mergeFiles.  Let's
    # wait and see how it works out.
    # ------------------------------------------------

    def _setData(self, data):
        startTime = perf_counter()
        moTime(startTime, "DataCache.setData started")
        self.__plugins = data[0]
        self.pluginModel.setPlugins(deepcopy(self.__plugins))
        self.__merges = data[1]
        self.mergeModel.setMerges(self.__merges)
        self.__mods = data[2]
        moPerf(startTime, perf_counter(), "DataCache.setData - complete")
