from copy import deepcopy
from typing import List, Callable
from time import perf_counter
from PyQt5.QtCore import pyqtSignal, QObject, QThreadPool

from mobase import IOrganizer
from mergewizard.domain.plugin import Plugins, PluginLoader
from mergewizard.domain.merge import MergeFile as Merge, MergeFileReader
from mergewizard.domain.AsyncWorker import Worker
from mergewizard.domain.MOLog import moPerf, moTime
from mergewizard.models.PluginModel import PluginModel
from mergewizard.models.MergeModel import MergeModel


class ProgressEmitter(QObject):
    def __init__(self, callback: Callable[[], int] = None, maxValue=0):
        super().__init__()
        self._callback = callback
        self._maxValue = maxValue
        self._pluginProgress = 0
        self._mergeProgress = 0
        self._dataCacheProgress = 0

    def reset(self):
        self._pluginProgress = 0
        self._mergeProgress = 0
        self._dataCacheProgress = 0

    @property
    def maxValue(self):
        return self._maxValue

    @maxValue.setter
    def maxValue(self, value):
        self._maxValue = value

    def pluginProgress(self, amount: int) -> None:
        self._pluginProgress = amount
        self._emitProgress()

    def mergeProgress(self, amount: int) -> None:
        self._mergeProgress = amount
        self._emitProgress()

    def dataCacheProgress(self, amount: int) -> None:
        self._dataCacheProgress = amount
        self._emitProgress()

    def _emitProgress(self):
        self._callback.emit(
            (self._pluginProgress + self._mergeProgress + self._dataCacheProgress) * 100 / self._maxValue
        )

    def end(self) -> None:
        self._value = self._maxValue
        if self._callback:
            self._callback.emit(100)


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

        self._progressEmitter = ProgressEmitter(self.dataCacheLoadingProgress)
        self.mergeModelLoadingProgress.connect(self._progressEmitter.mergeProgress)
        self.pluginModelLoadingProgress.connect(self._progressEmitter.pluginProgress)

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
        if self._isLoadingData:
            return
        self._isLoadingData = True
        self._dataStartTime = perf_counter()
        moTime(self._dataStartTime, "Started data loading")
        self.dataCacheLoadingStarted.emit()
        self._progressEmitter.reset()
        self.loadMerges()
        self.loadPlugins()

    def loadMerges(self) -> None:
        if self._isLoadingMerges:
            return
        self._isLoadingMerges = True
        self._progressEmitter.maxValue = 300 if self._isLoadingPlugins else 100
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
        if self._isLoadingPlugins:
            return
        self._isLoadingPlugins = True
        self._progressEmitter.maxValue = 300 if self._isLoadingMerges else 100
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

        count = 0
        total = len(self.__merges)
        for merge in self.__merges:
            self.pluginModel.addPlugin(merge.filename, modName=merge.modName, isMerge=True)
            for pluginFileDesc in merge.plugins:
                self.pluginModel.addPlugin(pluginFileDesc.filename, modName=pluginFileDesc.modName, isMerged=True)
            count = count + 1
            self._progressEmitter.dataCacheProgress(count * 100 / total)
        self._progressEmitter.end()
        self.dataCacheLoadingCompleted.emit()
        self._dataStopTime = perf_counter()
        moPerf(self._dataStartTime, self._dataStopTime, "Finished loading data")

    def setMerges(self, merges: List[Merge]):
        self.__merges = merges
        self.mergeModel.setMerges(merges)
        self.mergeModelLoadingCompleted.emit()

    def setPlugins(self, plugins: Plugins):
        self.__plugins = plugins
        self.pluginModel.setPlugins(deepcopy(plugins))
        self.pluginModelLoadingCompleted.emit()
