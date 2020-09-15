from typing import List
from PyQt5.QtCore import QModelIndex, QAbstractItemModel, QAbstractProxyModel
from mergewizard.models.PluginModel import PluginModel
from mergewizard.models.PluginFilterModel import PluginFilterModel
from mergewizard.models.PluginStyleModel import PluginStyleModel
from mergewizard.models.PluginColumnModel import PluginColumnModel


class PluginModelCollection:
    def __init__(self, pluginModel: PluginModel = None):
        self.pluginModel = pluginModel
        self.filterModel = PluginFilterModel()
        self.styleModel = PluginStyleModel()
        self.columnModel = PluginColumnModel()

        self.filterModel.setSourceModel(pluginModel)
        self.styleModel.setSourceModel(self.filterModel)
        self.columnModel.setSourceModel(self.styleModel)

    def setPluginModel(self, pluginModel: PluginModel):
        self.filterModel.setSourceModel(pluginModel)
        self.pluginModel = pluginModel

    @staticmethod
    def indexForModel(
        idx: QModelIndex, desiredModel: QAbstractItemModel,
    ):
        if desiredModel is None:
            return idx.model().index(-1, -1)

        modelIndex = idx
        while modelIndex.model() != desiredModel:
            if isinstance(modelIndex.model(), QAbstractProxyModel):
                modelIndex = modelIndex.model().mapToSource(modelIndex)
            else:
                break
        if modelIndex.model() == desiredModel:
            return modelIndex
        return desiredModel.index(-1, -1)

    @staticmethod
    def indexesForModel(indexes: List[QModelIndex], desiredModel: QAbstractItemModel):
        return [PluginModelCollection.indexForModel(idx, desiredModel) for idx in indexes]
