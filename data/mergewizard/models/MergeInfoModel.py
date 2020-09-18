from enum import IntEnum, auto
from typing import List, Union, Tuple
from PyQt5.QtCore import QIdentityProxyModel, QModelIndex, Qt, QObject, QSortFilterProxyModel, qInfo
from PyQt5.QtGui import QFont, QColor
import mergewizard.models.ItemId as Id
from mergewizard.domain.plugin.Plugin import Plugin
from mergewizard.domain.plugin.Plugins import Plugins
from mergewizard.models.PluginModelBase import PluginModelBase, Role, Column as PluginColumn


class Column(IntEnum):
    Property = 0
    Value = 1


class Row(IntEnum):
    WhenBuilt = 0
    MergedBy = auto()
    MergedPlugins = auto()
    ZEditOptions = auto()


MERGE_OPTIONS = [
    ("method", "Merge method:"),
    ("archiveAction", "Archive action:"),
    ("buildMergedArchive", "Build merged archive:"),
    ("useGameLoadOrder", "Use game load order:"),
    ("handleFaceData", "Handle face data:"),
    ("handleVoiceData", "Handle voice data:"),
    ("handleBillboards", "Handle billboards:"),
    ("handleStringFiles", "Handle string files:"),
    ("handleTranslations", "Handle translations:"),
    ("handleIniFiles", "Handle ini files:"),
    ("handleDialogViews", "Handle dialog views:"),
    ("copyGeneralAssets", "Copy general assets:"),
]


class MergeInfoBaseModel(QIdentityProxyModel):
    def __init__(self, parent: QObject = None):
        super().__init__(parent)

    def sourcePlugin(self, row: int) -> Union[Plugin, None]:
        return self.sourceModel().data(self.sourceModel().index(row, 0), Role.Data)

    def mergeAssociations(self, row: int) -> Union[Tuple, None]:
        return self.sourceModel().data(self.sourceModel().index(row, 0), Role.MergeAssociations)

    # ----------------------------------------------------
    # --- Abstract model overrides
    # ----------------------------------------------------

    def rowCount(self, parent: QModelIndex = QModelIndex()):
        if not self.sourceModel():
            return 0
        depth = Id.depth(parent)

        if depth == Id.Depth.Invalid:
            return self.sourceModel().rowCount()
        if parent.column() != 0:
            return 0
        if depth == Id.Depth.D0:
            return len(Row)
        if depth == Id.Depth.D1:
            plugin = self.sourcePlugin(Id.row(parent.internalId()))
            if not plugin.isMerge and not plugin.isMerged:
                return 0
            plugins, merges = self.mergeAssociations(Id.row(parent.internalId()))
            if parent.row() == Row.MergedPlugins:
                return len(plugins)
            if parent.row() == Row.MergedBy:
                return len(merges)
            if plugin.mergeFile and parent.row() == Row.ZEditOptions:
                return len(MERGE_OPTIONS)
        return 0

    def columnCount(self, parent: QModelIndex = QModelIndex()):
        return 3

    def index(self, row: int, col: int, parent: QModelIndex = QModelIndex()):
        if self.hasIndex(row, col, parent):
            return self.createIndex(row, col, Id.idForIndex(parent))
        return QModelIndex()

    def parent(self, child: QModelIndex):
        if not child.isValid():
            return QModelIndex()
        parentId = child.internalId()
        if not Id.isValid(parentId):
            return QModelIndex()
        return self.createIndex(Id.row(parentId), Id.column(parentId), Id.parentId(parentId))

    def hasChildren(self, parent: QModelIndex = QModelIndex()):
        return self.rowCount(parent) > 0

    def mapToSource(self, proxyIdx: QModelIndex = QModelIndex()):
        depth = Id.depth(proxyIdx)
        if depth == Id.Depth.Invalid:
            return QModelIndex()
        if depth == Id.Depth.D0:
            return self.sourceModel().index(proxyIdx.row(), PluginColumn.PluginName)
        return QModelIndex()

    def mapFromSource(self, sourceIdx: QModelIndex = QModelIndex()):
        if not sourceIdx.isValid():
            return QModelIndex()
        return self.index(sourceIdx.row(), Column.Value)

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.DisplayRole):
        if orientation == Qt.Vertical:
            return None
        if role == Qt.DisplayRole:
            if section == Column.Property:
                return self.tr("Property")
            if section == Column.Value:
                return self.tr("Value")

    def flags(self, idx: QModelIndex):
        DEFAULT_FLAGS = Qt.ItemIsEnabled
        if not idx.isValid():
            return Qt.NoItemFlags
        depth = Id.depth(idx)
        if idx.column() == 0:
            if depth == Id.Depth.D0:
                return DEFAULT_FLAGS
            if depth == Id.Depth.D1:
                if idx.row() == Row.MergedBy or idx.row() == Row.MergedPlugins or idx.row() == Row.ZEditOptions:
                    return DEFAULT_FLAGS
        return DEFAULT_FLAGS | Qt.ItemNeverHasChildren

    def data(self, idx: QModelIndex, role: int = Qt.DisplayRole):
        depth = Id.depth(idx)
        if depth == Id.Depth.Invalid:
            return

        if role == Role.Data:
            # return the top level plugin
            if depth == Id.Depth.D0:
                return self.sourcePlugin(idx.row())
            if depth == Id.Depth.D1:
                return self.sourcePlugin(Id.row(idx.internalId()))
            if depth == Id.Depth.D2:
                return self.sourcePlugin(Id.row(Id.parentId(idx.internalId())))

        if role == Role.MergeAssociations:
            if depth == Id.Depth.D0:
                return self.mergeAssociations(idx.row())
            if depth == Id.Depth.D1:
                return self.mergeAssociations(Id.row(idx.internalId()))
            if depth == Id.Depth.D2:
                return self.mergeAssociations(Id.row(Id.parentId(idx.internalId())))

        if role == Role.Cell:
            return self._display_data(idx)
        if not idx.parent().isValid():
            return
        if role == Qt.DisplayRole:
            return self._display_data(idx)
        return self._style_data(idx, role)

    def _display_data(self, idx: QModelIndex):
        depth = Id.depth(idx)

        if depth == Id.Depth.D0:
            if idx.column() == Column.Property:
                return self.tr("Plugin Name: ")
            if idx.column() == Column.Value:
                return self.data(idx, Role.Data).pluginName

        if depth == Id.Depth.D1:
            if idx.column() == Column.Property:
                if idx.row() == Row.MergedBy:
                    return self.tr("Merged By: ")
                if idx.row() == Row.MergedPlugins:
                    return self.tr("Merged Plugins: ")
                if idx.row() == Row.WhenBuilt:
                    return self.tr("Built On: ")
                if idx.row() == Row.ZEditOptions:
                    return self.tr("zMerge Options: ")

            if idx.column() == Column.Value:
                plugin = self.data(idx, Role.Data)
                plugins, merges = self.data(idx, Role.MergeAssociations)
                if idx.row() == Row.MergedBy and merges:
                    return self.tr("({})").format(len(merges))
                if idx.row() == Row.MergedPlugins and plugins:
                    return self.tr("({})").format(len(plugins))
                if idx.row() == Row.ZEditOptions and plugin.isMerge:
                    return self.tr("({})").format(len(MERGE_OPTIONS))
                if idx.row() == Row.WhenBuilt and plugin.isMerge and plugin.mergeFile:
                    return plugin.mergeFile.dateBuilt

        if depth == Id.Depth.D2:
            if idx.parent().row() == Row.MergedBy:
                if idx.column() == 0:
                    return "{}".format(idx.row() + 1)
                if idx.column() == 1:
                    plugins, merges = self.data(idx, Role.MergeAssociations)
                    return merges[idx.row()].pluginName
            if idx.parent().row() == Row.MergedPlugins:
                if idx.column() == 0:
                    return "{}".format(idx.row() + 1)
                if idx.column() == 1:
                    plugins, merges = self.data(idx, Role.MergeAssociations)
                    return plugins[idx.row()].pluginName
            if idx.parent().row() == Row.ZEditOptions:
                if idx.column() == 0:
                    return MERGE_OPTIONS[idx.row()][1]
                if idx.column() == 1:
                    plugin = self.data(idx, Role.Data)
                    return getattr(plugin.mergeFile, MERGE_OPTIONS[idx.row()][0], None)

    def _style_data(self, idx: QModelIndex, role: int):
        if role == Qt.FontRole:
            if idx.column() == 0 and Id.depth(idx) == Id.Depth.D1:
                font = QFont()
                font.setBold(True)
                return font
            return

        if role == Qt.ForegroundRole:
            if idx.column() == 1 and Id.depth(idx) == Id.Depth.D1:
                if idx.row() == Row.MergedPlugins or idx.row() == Row.MergedBy or idx.row() == Row.ZEditOptions:
                    return QColor(Qt.lightGray)
            if idx.column() == 0 and Id.depth(idx) == Id.Depth.D2:
                if idx.parent().row() == Row.MergedPlugins or idx.parent().row() == Row.MergedBy:
                    return QColor(Qt.lightGray)

        if role == Qt.TextAlignmentRole:
            if idx.column() == 0 and Id.depth(idx) == Id.Depth.D2:
                if idx.parent().row() == Row.MergedPlugins:
                    return Qt.AlignRight


class MergeInfoModel(QSortFilterProxyModel):
    def __init__(self, parent: QObject = None):
        super().__init__(parent)
        super().setSourceModel(MergeInfoBaseModel())

    def setSourceModel(self, model: PluginModelBase):
        self.sourceModel().setSourceModel(model)

    def filterAcceptsRow(self, srcRow: int, srcParent: QModelIndex) -> bool:
        if Id.depth(srcParent) == Id.Depth.D0:
            idx = self.sourceModel().index(srcRow, 1, srcParent)
            if not self.sourceModel().data(idx):
                return False
        return True

