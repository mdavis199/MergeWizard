from copy import deepcopy
from typing import List, Callable
from time import perf_counter
from PyQt5.QtCore import pyqtSignal, QObject, qInfo

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
        self._maxValue = 300

    @property
    def maxValue(self):
        return self._maxValue

    @maxValue.setter
    def maxValue(self, value):
        self._maxValue = value

    def pluginProgress(self, amount: int) -> None:
        # if not amount % 10:
        #    qInfo("Plugin progress: {}".format(amount))
        self._pluginProgress = amount
        self._emitProgress()

    def mergeProgress(self, amount: int) -> None:
        # qInfo("Merge progress: {}".format(amount))
        self._mergeProgress = amount
        self._emitProgress()

    def dataCacheProgress(self, amount: int) -> None:
        # if not amount % 5:
        #    qInfo("Data progress: {}".format(amount))
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
        self._pluginLoader: PluginLoader = None
        self._mergeLoader: MergeFileReader = None

        self._isLoadingData: bool = False

        self._mergeStartTime: float = 0
        self._pluginStartTime: float = 0
        self._dataStartTime: float = 0

        self._progressEmitter = ProgressEmitter(self.dataCacheLoadingProgress)

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
        return self.isLoadingMerges or self.isLoadingPlugins

    @property
    def isLoadingMerges(self) -> bool:
        return self._mergeLoader and self._mergeLoader.isRunning()

    @property
    def isLoadingPlugins(self) -> bool:
        return self._pluginLoader and self._pluginLoader.isRunning()

    # --------------------------------------------------------

    def stopLoading(self) -> None:
        if self.isLoadingMerges:
            self._mergeLoader.stop()
        if self.isLoadingPlugins:
            self._pluginLoader.stop()

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
        if self._mergeLoader and self._mergeLoader.isRunning():
            return
        self._mergeLoader = MergeFileReader(self._organizer.modsPath())
        self._mergeLoader.started.connect(lambda: qInfo("Merge loader started"))
        self._mergeLoader.progress.connect(self._progressEmitter.mergeProgress)
        self._mergeLoader.finished.connect(self._finishedLoadingMerges)
        self._mergeLoader.result.connect(self._setMerges)
        self._mergeLoader.started.connect(self.mergeModelLoadingStarted)
        self._mergeLoader.finished.connect(self.mergeModelLoadingCompleted)
        self._mergeLoader.progress.connect(self.mergeModelLoadingProgress)

        self._mergeStartTime = perf_counter()
        moTime(self._mergeStartTime, "Started loading merges")
        self._mergeLoader.start()

    def loadPlugins(self) -> None:
        if self._pluginLoader and self._pluginLoader.isRunning():
            return
        self._pluginLoader = PluginLoader(self._organizer)
        self._mergeLoader.started.connect(lambda: qInfo("Plugin loader started"))
        self._pluginLoader.progress.connect(self._progressEmitter.pluginProgress)
        self._pluginLoader.finished.connect(self._finishedLoadingPlugins)
        self._pluginLoader.result.connect(self._setPlugins)
        self._pluginLoader.started.connect(self.pluginModelLoadingStarted)
        self._pluginLoader.finished.connect(self.pluginModelLoadingCompleted)
        self._pluginLoader.progress.connect(self.pluginModelLoadingProgress)

        self._pluginStartTime = perf_counter()
        moTime(self._pluginStartTime, "Started loading plugins")
        self._pluginLoader.start()

    def _finishedLoadingMerges(self) -> None:
        moPerf(self._mergeStartTime, perf_counter(), "Finished loading merges")

    def _finishedLoadingPlugins(self) -> None:
        moPerf(self._pluginStartTime, perf_counter(), "Finished loading plugins")

    # ------------------------------------------------
    # Combine the info from the merge model into the
    # plugin model
    # ------------------------------------------------

    def _setMerges(self, merges: List[Merge]):
        self.__merges = merges
        self.mergeModel.setMerges(merges)
        self._combineModels()

    def _setPlugins(self, plugins: Plugins):
        self.__plugins = plugins
        self.pluginModel.setPlugins(deepcopy(plugins))
        self._combineModels()

    def _combineModels(self):
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
        moPerf(self._dataStartTime, perf_counter(), "Finished loading data")
