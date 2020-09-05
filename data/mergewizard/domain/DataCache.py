from typing import List, Dict

from PyQt5.QtCore import pyqtSignal, Qt, QObject, QThreadPool
from mergewizard.domain.Context import Context
from mergewizard.domain.AsyncWorker import Worker
from mergewizard.domain.MergeFileReader import MergeFileReader
from mergewizard.domain.PluginLoader import AsyncPluginLoader
from mergewizard.domain.Merge import Merge
from mergewizard.domain.Plugin import Plugin


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

    def __init__(self, context: Context):
        super().__init__()
        self.context = context
        self._isLoadingMerges = False
        self._isLoadingPlugins = False

        self._merges: List[Merge] = []
        self._plugins: List[Plugin] = []

    def isLoadingMerges(self):
        return self._isLoadingMerges

    def isLoadingPlugins(self):
        return self._isLoadingPlugins

    def isLoading(self):
        return self._isLoadingMerges or self._isLoadingPlugins

    def loadMerges(self):
        self._isLoadingMerges = True
        self.mergeModelLoadingStarted.emit()
        worker = Worker(MergeFileReader.loadMerges, self.modFolder, modFolders)
        worker.signals.result.connect(self.setMerges)
        worker.signals.progress.connect(self.mergeModelLoadingProgress)
        QThreadPool.globalInstance().start(worker)

    def loadPlugins(self):
        self._isLoadingPlugins = True
        self.pluginModelLoadingStarted.emit()
        worker = Worker(AsyncPluginLoader.loadPlugins, self._organizer)
        worker.signals.result.connect(self.setPlugins)
        worker.signals.progress.connect(self.pluginModelLoadingProgress)
        QThreadPool.globalInstance().start(worker)

    def setMerges(self, merges: List[Merge]):
        self._merges = merges

    def setPlugins(self, plugins: List[Plugin]):
        self._plugins = plugins

    def combineModels(self):
        if self.context.mergeModel().isLoading():
            return
        if self.context.pluginModel().isLoading():
            return

    def addMergeInfo(self):
        merges = self.context.mergeModel().merges()
        plugins = self.context.pluginModel().plugins()
        missingMerges = []
        missingMerged = []
        for merge in merges:
            mergeName = merge.filename.lower()
            row = next((i for i in range(len(self._plugins)) if mergeName == self._plugins[i].key), -1)
            if row >= 0:
                self.setData(self.index(row, Column.IsMerge), True)
            else:
                missingMerges.append(merge)
            for plug in merge.plugins:
                plugName = plug.lower()
                row2 = next((j for j in range(len(self._plugins)) if plugName == self.__plugins[j].pluginName), -1)
                if row2 >= 0:
                    self.setData(self.index(row2.Column.IsMerged), True, Qt.EditRole)
                else:
                    missingMerged.append(plug)

    def isOnModPath(self, name: str, expectedPath: str):
        # compare that the mod is on MO Path
        pass
