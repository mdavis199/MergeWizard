from copy import deepcopy
from typing import List
from time import perf_counter
from PyQt5.QtCore import pyqtSignal, QObject, QThreadPool

from mobase import IOrganizer
from mergewizard.domain.plugin import Plugins, PluginLoader
from mergewizard.domain.merge import MergeFile as Merge, MergeFileReader
from mergewizard.domain.AsyncWorker import Worker
from mergewizard.domain.MOLog import moPerf, moTime
from mergewizard.models.PluginModel import PluginModel
from mergewizard.models.MergeModel import MergeModel


class DataCache(QObject):

    mergeModelLoadingStarted = pyqtSignal()
    mergeModelLoadingProgress = pyqtSignal(int)
    mergeModelLoadingCompleted = pyqtSignal()
    pluginModelLoadingStarted = pyqtSignal()
    pluginModelLoadingProgress = pyqtSignal(int)
    pluginModelLoadingCompleted = pyqtSignal()
    dataCacheLoadingStarted = pyqtSignal()
    dataCacheLoadingProgress = pyqtSignal(int)
    dataCacheLoadingCompleted = pyqtSignal()

    def __init__(self, organizer: IOrganizer):
        super().__init__()
        self._organizer: IOrganizer = organizer
        self._mergeModel: MergeModel = MergeModel()
        self._pluginModel: PluginModel = PluginModel(organizer)

        self._isLoadingMerges: bool = False
        self._isLoadingPlugins: bool = False
        self._isLoadingData: bool = False

        self._programStartTime: float = perf_counter()
        self._mergeStartTime: float = 0
        self._mergeStopTime: float = 0
        self._pluginStartTime: float = 0
        self._pluginStopTime: float = 0
        self._dataStartTime: float = 0
        self._dataStopTime: float = 0

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
    def isLoadingData(self) -> bool:
        return self._isLoadingMerges or self._isLoadingPlugins

    @property
    def isLoadingMerges(self) -> bool:
        return self._isLoadingMerges

    @property
    def isLoadingPlugins(self) -> bool:
        return self._isLoadingPlugins

    # --------------------------------------------------------

    def loadData(self) -> None:
        self._isLoadingData = True
        self._dataStartTime = perf_counter()
        moTime(self._dataStartTime, "Started data loading")
        self.dataCacheLoadingStarted.emit()
        self.loadMerges()
        self.loadPlugins()

    def loadMerges(self) -> None:
        self._isLoadingMerges = True
        self._mergeStartTime = perf_counter()
        moTime(self._mergeStartTime, "Started loading merges")
        self.mergeModelLoadingStarted.emit()
        modFolder = self.organizer.modsPath()
        worker = Worker(MergeFileReader.loadMerges, modFolder)
        worker.signals.result.connect(self.setMerges)
        worker.signals.progress.connect(self.mergeModelLoadingProgress)
        worker.signals.finished.connect(self.finishedLoadingMerges)
        QThreadPool.globalInstance().start(worker)

    def loadPlugins(self) -> None:
        self._isLoadingPlugins = True
        self._pluginStartTime = perf_counter()
        moTime(self._pluginStartTime, "Started loading plugins")
        self.pluginModelLoadingStarted.emit()
        worker = Worker(PluginLoader.loadPlugins, self._organizer)
        worker.signals.result.connect(self.setPlugins)
        worker.signals.progress.connect(self.pluginModelLoadingProgress)
        worker.signals.finished.connect(self.finishedLoadingPlugins)
        QThreadPool.globalInstance().start(worker)

    def finishedLoadingMerges(self) -> None:
        self._isLoadingMerges = False
        self._mergeStopTime = perf_counter()
        moPerf(self._mergeStartTime, self._mergeStopTime, "Finished loading merges")
        self.mergeModelLoadingCompleted.emit()
        self.combineModels()

    def finishedLoadingPlugins(self) -> None:
        self._isLoadingPlugins = False
        self._pluginStopTime = perf_counter()
        moPerf(self._pluginStartTime, self._pluginStopTime, "Finished loading plugins")
        self.pluginModelLoadingCompleted.emit()
        self.combineModels()

    # ------------------------------------------------
    # Combine the info from the merge model into the
    # plugin model
    # ------------------------------------------------

    def combineModels(self):
        if self.isLoadingMerges:
            return
        if self.isLoadingPlugins:
            return
        # self.addMergeInfoToPluginModel()
        self.pluginModel.addMergeInfo(self.__merges)
        self._dataStopTime = perf_counter()
        moPerf(self._dataStartTime, self._dataStopTime, "Finished loading data")

    def setMerges(self, merges: List[Merge]):
        self.__merges = merges
        self.mergeModel.setMerges(merges)

    def setPlugins(self, plugins: Plugins):
        self.__plugins = plugins
        self.pluginModel.setPlugins(deepcopy(plugins))

    def addMergeInfoToPluginModel(self):
        for merge in self.__merges:
            plugin = self.__plugins.get(merge.filename, False)  # False -> non-MO/Missing
            plugin.isMerge = True
            for p in merge.plugins:
                plugin = self.__plugins.get(p, False)  # False -> non-MO/Missing
                plugin.isMerged = True
