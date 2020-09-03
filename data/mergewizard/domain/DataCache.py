from typing import List, Dict

from PyQt5.QtCore import pyqtSignal, QObject
from mergewizard.domain.Context import Context


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
        context.mergeModel().modelLoadingStarted.connect(self.mergeModelLoadingStarted)
        context.mergeModel().modelLoadingProgress.connect(self.mergeModelLoadingProgress)
        context.mergeModel().modelLoadingCompleted.connect(self.mergeModelLoadingCompleted)
        context.pluginModel().modelLoadingStarted.connect(self.pluginModelLoadingStarted)
        context.pluginModel().modelLoadingProgress.connect(self.pluginModelLoadingProgress)
        context.pluginModel().modelLoadingCompleted.connect(self.pluginModelLoadingCompleted)

        context.mergeModel().modelLoadingCompleted.connect(self.combineModels)
        context.pluginModel().modelLoadingCompleted.connect(self.combineModels)

    def loadModels(self):
        self.context.mergeModel().loadMerges()
        self.context.pluginModel().loadPlugins()

    def combineModels(self):
        if self.context.mergeModel().isLoading():
            return
        if self.context.pluginModel().isLoading():
            return
