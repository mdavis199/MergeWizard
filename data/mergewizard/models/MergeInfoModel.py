from enum import IntEnum, auto
from typing import List
from PyQt5.QtCore import (
    QIdentityProxyModel,
    QModelIndex,
    Qt,
    QObject,
    QSortFilterProxyModel,
)

from mergewizard.domain.plugin.Plugin import Plugin
from mergewizard.domain.plugin.Plugins import Plugins
from mergewizard.models.PluginModelBase import PluginModelBase, Column as PluginColumn


class Column(IntEnum):
    Property = 0
    Value = 1


class Row(IntEnum):
    MergedBy = 0
    MergedPlugins = auto()
    WhenBuild = auto()
    ZEditOptions = auto()


class MergeInfoBaseModel(QIdentityProxyModel):
    def __init__(self, parent: QObject = None):
        super().__init__(parent)


class MergeInfoModel(QSortFilterProxyModel):
    def __init__(self, parent: QObject = None):
        super().__init__(parent)
        super().setSourceModel(MergeInfoBaseModel())

    def setSourceModel(self, model: PluginModelBase):
        self.sourceModel().setSourceModel(model)

