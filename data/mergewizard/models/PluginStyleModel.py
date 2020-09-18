from PyQt5.QtCore import Qt, QObject, QIdentityProxyModel, QModelIndex
from PyQt5.QtGui import QIcon, QColor, QFont

from mergewizard.models.PluginModelBase import Column, Role, isBoolColumn
from mergewizard.constants import Icon


class PluginStyleModel(QIdentityProxyModel):
    def __init__(self, parent: QObject = None):
        super().__init__(parent)
        self._readonly = False
        self._displayCheckbox = True

    def isIconOnlyColumn(self, col: int):
        return isBoolColumn(col)

    def enableReadonly(self, enable: bool):
        self._readonly = enable

    def enableCheckDisplay(self, enable: bool):
        self._displayCheckbox = enable

    def data(self, idx: QModelIndex, role: int = Qt.DisplayRole):
        if role == Qt.DisplayRole:
            if self.isIconOnlyColumn(idx.column()):
                return None
            if idx.column() == Column.Priority:
                sourceIdx = self.sourceModel().index(idx.row(), idx.column())
                if self.sourceModel().data(sourceIdx) == -1:
                    return None
        elif role == Qt.DecorationRole:
            if not self.isIconOnlyColumn(idx.column()):
                return None
            v = super().data(idx, Role.Cell)
            if idx.column() == Column.IsSelectedAsMaster:
                return QIcon(Icon.SELECTED_AS_MASTER) if v else None
            if idx.column() == Column.IsSelected:
                return QIcon(Icon.SELECTED) if v else None
            if idx.column() == Column.IsMissing:
                return QIcon(Icon.MISSING) if v else None
            if idx.column() == Column.IsInactive:
                return QIcon(Icon.INACTIVE) if v else None
            if idx.column() == Column.IsMaster:
                return QIcon(Icon.MASTER) if v else None
            if idx.column() == Column.IsMerge:
                return QIcon(Icon.MERGE) if v else None
            if idx.column() == Column.IsMerged:
                return QIcon(Icon.MERGED) if v else None
            return None
        elif role == Qt.ForegroundRole:
            missing = super().data(idx.siblingAtColumn(Column.IsMissing), Role.Cell)
            inactive = super().data(idx.siblingAtColumn(Column.IsInactive), Role.Cell)
            if missing or inactive:
                return QColor(Qt.lightGray).darker()
        elif role == Qt.FontRole:
            if super().data(idx.siblingAtColumn(Column.IsMissing), Role.Cell):
                font = QFont()
                font.setItalic(True)
                return font
        elif role == Qt.TextAlignmentRole:
            if idx.column() in [
                Column.PluginOrder,
                Column.MasterOrder,
                Column.Priority,
            ]:
                return Qt.AlignCenter
        elif role == Qt.CheckStateRole and self._displayCheckbox:
            if idx.column() == Column.PluginName:
                return Qt.Checked if super().data(idx.siblingAtColumn(Column.IsSelected), Role.Cell) else Qt.Unchecked
        return super().data(idx, role)

    def setData(self, idx: QModelIndex, value, role: int = Qt.EditRole):
        if self._readonly:
            return False
        if role == Qt.CheckStateRole and self._displayCheckbox:
            if idx.column() == Column.PluginName:
                return super().setData(idx.siblingAtColumn(Column.IsSelected), value == Qt.Checked, Qt.EditRole,)
        return super().setData(idx, value, role)

    def headerData(
        self, section: int, orientation: Qt.Orientation, role: int = Qt.DisplayRole,
    ):
        if orientation == Qt.Vertical:
            return None
        if role == Qt.DisplayRole:
            if section == Column.PluginName:
                return self.tr("Plugin Name")
            if section == Column.ModName:
                return self.tr("Mod Name")
            if section == Column.ModPath:
                return self.tr("Mod Path")
            if section == Column.Priority:
                return self.tr("Priority")
            if section == Column.PluginOrder:
                return self.tr("Position")
            if section == Column.MasterOrder:
                return self.tr("Position")
            return None
        if role == Qt.DecorationRole:
            if self.isIconOnlyColumn(section):
                if section == Column.IsSelectedAsMaster:
                    return QIcon(Icon.SELECTED_AS_MASTER)
                if section == Column.IsSelected:
                    return QIcon(Icon.SELECTED)
                if section == Column.IsMissing:
                    return QIcon(Icon.MISSING)
                if section == Column.IsInactive:
                    return QIcon(Icon.INACTIVE)
                if section == Column.IsMaster:
                    return QIcon(Icon.MASTER)
                if section == Column.IsMerge:
                    return QIcon(Icon.MERGE)
                if section == Column.IsMerged:
                    return QIcon(Icon.MERGED)
            return None
        if role == Qt.ToolTipRole:
            if section == Column.IsSelectedAsMaster:
                return self.tr("Plugins required by the selected plugins")
            if section == Column.IsSelected:
                return self.tr("Plugins selected for the merge")
            if section == Column.IsMissing:
                return self.tr("Plugins which were not found")
            if section == Column.IsInactive:
                return self.tr("Plugins not activated in MO2 profile")
            if section == Column.IsMaster:
                return self.tr("Plugin tagged as a master library")
            if section == Column.IsMerge:
                return self.tr("Plugins that were created by a merge")
            if section == Column.IsMerged:
                return self.tr("Plugins that were consumed by a merge")
        return super().headerData(section, orientation, role)

    def flags(self, idx: QModelIndex):
        if self._displayCheckbox and idx.isValid() and not idx.parent().isValid():
            sourceIdx = self.mapToSource(idx)
            flags = self.sourceModel().flags(sourceIdx)
            if sourceIdx.column() == Column.PluginName:
                return flags | Qt.ItemIsUserCheckable
        if self._readonly:
            return super().flags(idx) & ~Qt.ItemIsEditable
        return super().flags(idx)
