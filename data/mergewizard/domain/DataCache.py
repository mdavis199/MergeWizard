from copy import deepcopy
from time import perf_counter
from PyQt5.QtCore import pyqtSignal, QObject, qInfo

from mobase import IOrganizer
from mergewizard.domain.plugin import Plugins
from mergewizard.domain.DataLoader import DataLoader
from mergewizard.domain.MOLog import moPerf, moTime
from mergewizard.models.PluginModel import PluginModel
from mergewizard.models.MergeModel import MergeModel


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
        self.__merges = None
        self.__plugins = Plugins()

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

    # --------------------------------------------------------

    def stopLoading(self) -> None:
        if self.isLoading:
            self._dataLoader.stop()

    def loadData(self) -> None:
        if self.isLoading:
            return
        self._dataLoader = DataLoader(self._organizer)
        self._dataLoader.finished.connect(self._finishedLoadingData)
        self._dataLoader.result.connect(self._setData)
        self._dataLoader.started.connect(self.dataLoadingStarted)
        self._dataLoader.finished.connect(self.dataLoadingCompleted)
        self._dataLoader.progress.connect(self.dataLoadingProgress)

        self._dataLoadingStartTime = perf_counter()
        moTime(self._dataLoadingStartTime, "Data loading - started")
        self._dataLoader.start()

    def _finishedLoadingData(self) -> None:
        self._dataLoader.disconnect()
        self._dataLoader = None
        moPerf(self._dataLoadingStartTime, perf_counter(), "Data loading - complete")

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
        moTime(startTime, "Loading data into models - started")
        self.__plugins = data[0]
        self.pluginModel.setPlugins(deepcopy(self.__plugins))
        self.__merges = data[1]
        self.mergeModel.setMerges(self.__merges)
        moPerf(startTime, perf_counter(), "Loading data into models - complete")

