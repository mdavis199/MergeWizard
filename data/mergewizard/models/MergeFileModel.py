from enum import IntEnum, auto
from PyQt5.QtCore import QAbstractItemModel, QModelIndex, Qt, QObject
from PyQt5.QtGui import QFont, QColor
import mergewizard.models.ItemId as Id
from mergewizard.domain.merge.MergeFile import MergeFile


class Role(IntEnum):
    Cell = Qt.UserRole
    Data = Qt.UserRole + 1
    PossibleValues = Qt.UserRole + 10  # return options for combo box.


class Column(IntEnum):
    Property = 0
    Value = 1


# Depth: D0
class Row(IntEnum):
    ModName = 0
    PluginName = auto()
    WhenBuilt = auto()
    ZEditOptions = auto()
    LoadOrder = auto()
    MergedPlugins = auto()


# Depth: D1, parentRow = Row.ZEditOptions
class OptionRow(IntEnum):
    Method = 0
    ArchiveAction = auto()
    BuildArchive = auto()
    UseGameLoadOrder = auto()
    HandleFaceData = auto()
    HandleVoiceData = auto()
    HandleBillboards = auto()
    HandleStringFiles = auto()
    HandleTranslations = auto()
    HandleIniFiles = auto()
    HandleDialogViews = auto()
    CopyGeneralAssets = auto()


# For Depth D1 only
# Maps MergeFile attributes to their display text
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


# For Depth D1 only for merge options
def isBoolOption(rowId: OptionRow):
    return rowId != OptionRow.Method and rowId != OptionRow.ArchiveAction


def isArchiveActionCell(idx: QModelIndex):
    return Id.depth(idx) == Id.Depth.D1 and idx.column() == 1 and idx.row() == OptionRow.ArchiveAction


def isMethodCell(idx: QModelIndex):
    return Id.depth(idx) == Id.Depth.D1 and idx.column() == 1 and idx.row() == OptionRow.Method


class MergeFileModel(QAbstractItemModel):
    def __init__(self, parent: QObject = None):
        super().__init__(parent)
        self._mergeFile = MergeFile()
        self._isEditable = True
        self._showTooltipsOnPlugins = True

    @property
    def mergeFile(self):
        return self._mergeFile

    @mergeFile.setter
    def mergeFile(self, value):
        self.layoutAboutToBeChanged.emit()
        if value is None:
            self.mergeFile = MergeFile()
        else:
            self._mergeFile = value
        self.layoutChanged.emit()

    @property
    def isEditable(self):
        return self._isEditable

    @isEditable.setter
    def isEditable(self, value: bool):
        self._isEditable = value

    @property
    def showPluginTooltips(self):
        return self._showTooltipsOnPlugins

    @showPluginTooltips.setter
    def showPluginTooltips(self, value: bool):
        self._showTooltipsOnPlugins = value

    # ----------------------------------------------------
    # --- Abstract model overrides
    # ----------------------------------------------------

    def rowCount(self, parent: QModelIndex = QModelIndex()):
        parentDepth = Id.depth(parent)
        if parentDepth == Id.Depth.Invalid:
            return len(Row)
        elif parent.column() != 0:
            return 0
        elif parentDepth == Id.Depth.D0:
            if parent.row() == Row.LoadOrder:
                return len(self.mergeFile.loadOrder)
            elif parent.row() == Row.MergedPlugins:
                return len(self.mergeFile.plugins)
            elif parent.row() == Row.ZEditOptions:
                return len(MERGE_OPTIONS)
        return 0

    def columnCount(self, parent: QModelIndex = QModelIndex()):
        return len(Column) + 1

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

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.DisplayRole):
        if orientation == Qt.Vertical:
            return None
        if role == Qt.DisplayRole:
            if section == Column.Property:
                return self.tr("Property")
            if section == Column.Value:
                return self.tr("Value")

    def flags(self, idx: QModelIndex):
        DEFAULT_FLAGS = Qt.ItemIsEnabled | Qt.ItemIsSelectable  # May have children and not editable
        if not idx.isValid():
            return Qt.NoItemFlags
        depth = Id.depth(idx)
        if idx.column() == 0 and depth == Id.Depth.D0:
            if idx.row() == Row.LoadOrder or idx.row() == Row.MergedPlugins or idx.row() == Row.ZEditOptions:
                return DEFAULT_FLAGS  # These may have children
            elif self.isEditable and (idx.row() == Row.ModName or idx.row() == Row.PluginName):
                return DEFAULT_FLAGS | Qt.ItemIsEditable
        if idx.column() == 1 and depth == Id.Depth.D1:
            if idx.parent().row() == Row.ZEditOptions and self.isEditable:
                if isBoolOption(idx.row()):
                    return DEFAULT_FLAGS | Qt.ItemNeverHasChildren | Qt.ItemIsUserCheckable
                else:
                    return DEFAULT_FLAGS | Qt.ItemNeverHasChildren | Qt.ItemIsEditable
        return DEFAULT_FLAGS | Qt.ItemNeverHasChildren

    def data(self, idx: QModelIndex, role: int = Qt.DisplayRole):
        if not idx.isValid():
            return
        if role == Role.Data:
            return self.mergeFile
        if role == Role.PossibleValues:
            if isArchiveActionCell(idx):
                return MergeFile.ARCHIVEACTION_VALUES
            elif isMethodCell(idx):
                return MergeFile.METHOD_VALUES
        if role == Qt.CheckStateRole:
            return self._checkstate_data(idx)
        if role == Qt.DisplayRole or role == Role.Cell:
            return self._display_data(idx)
        if role == Qt.ToolTipRole:
            return self._tooltip_data(idx)
        return self._style_data(idx, role)

    def _checkstate_data(self, idx: QModelIndex):
        depth = Id.depth(idx)
        if (
            depth == Id.Depth.D1
            and idx.column() == 1
            and idx.parent().row() == Row.ZEditOptions
            and isBoolOption(idx.row())
        ):
            if getattr(self.mergeFile, MERGE_OPTIONS[idx.row()][0], False):
                return Qt.Checked
            else:
                return Qt.Unchecked

    def _display_data(self, idx: QModelIndex):
        depth = Id.depth(idx)

        if depth == Id.Depth.D0:
            if idx.column() == Column.Property:
                if idx.row() == Row.ModName:
                    return self.tr("Mod Name: ")
                if idx.row() == Row.PluginName:
                    return self.tr("Plugin Name: ")
                if idx.row() == Row.WhenBuilt:
                    return self.tr("Built On: ")
                if idx.row() == Row.ZEditOptions:
                    return self.tr("zMerge Options: ")
                if idx.row() == Row.LoadOrder:
                    return self.tr("Load Order: ")
                if idx.row() == Row.MergedPlugins:
                    return self.tr("Merged Plugins: ")

            elif idx.column() == Column.Value:
                if idx.row() == Row.ModName:
                    return self.mergeFile.name
                if idx.row() == Row.PluginName:
                    return self.mergeFile.filename
                if idx.row() == Row.WhenBuilt:
                    return self.mergeFile.dateBuilt
                if idx.row() == Row.ZEditOptions:
                    return self.tr("({})").format(len(MERGE_OPTIONS))
                if idx.row() == Row.LoadOrder:
                    return self.tr("({})").format(len(self.mergeFile.loadOrder))
                if idx.row() == Row.MergedPlugins:
                    return self.tr("({})").format(len(self.mergeFile.plugins))

        elif depth == Id.Depth.D1:
            parentRow = idx.parent().row()
            if parentRow == Row.LoadOrder:
                if idx.column() == 0:
                    return "{}".format(idx.row() + 1)
                elif idx.column() == 1:
                    return self.mergeFile.loadOrder[idx.row()]
            elif parentRow == Row.MergedPlugins:
                if idx.column() == 0:
                    return "{}".format(idx.row() + 1)
                elif idx.column() == 1:
                    return self.mergeFile.plugins[idx.row()].filename
            if idx.parent().row() == Row.ZEditOptions:
                if idx.column() == 0:
                    return MERGE_OPTIONS[idx.row()][1]
                elif idx.column() == 1:
                    value = getattr(self.mergeFile, MERGE_OPTIONS[idx.row()][0], None)
                    if isinstance(value, bool):
                        return "true" if value else "false"
                    return value

    def _tooltip_data(self, idx: QModelIndex):
        depth = Id.depth(idx)
        if depth == Id.Depth.D1 and idx.parent().row() == Row.MergedPlugins:
            dataFolder = self.mergeFile.plugins[idx.row()].dataFolder
            hash = getattr(self.mergeFile.plugins[idx.row()], "hash", "")
            return "<html><head/><body><p>folder: " + dataFolder + "</p><p>hash: " + hash + "</p></body></html>"

    def _style_data(self, idx: QModelIndex, role: int):
        if role == Qt.FontRole:
            if idx.column() == 0 and Id.depth(idx) == Id.Depth.D0:
                font = QFont()
                font.setBold(True)
                return font
            return

        if role == Qt.ForegroundRole:
            if idx.column() == 1 and Id.depth(idx) == Id.Depth.D0:
                if idx.row() == Row.MergedPlugins or idx.row() == Row.LoadOrder or idx.row() == Row.ZEditOptions:
                    return QColor(Qt.lightGray)
            if idx.column() == 0 and Id.depth(idx) == Id.Depth.D1:
                if idx.parent().row() == Row.MergedPlugins or idx.parent().row() == Row.LoadOrder:
                    return QColor(Qt.lightGray)

        if role == Qt.TextAlignmentRole:
            if idx.column() == 0 and Id.depth(idx) == Id.Depth.D2:
                if idx.parent().row() == Row.MergedPlugins:
                    return Qt.AlignRight

    def setData(self, idx: QModelIndex, value, role: int = Qt.EditRole):
        if not idx.isValid() or idx.column() != 1:
            return False

        if role == Qt.CheckStateRole:
            if Id.depth(idx) == Id.Depth.D1 and idx.parent().row() == Row.ZEditOptions and isBoolOption(idx.row()):
                setattr(self.mergeFile, MERGE_OPTIONS[idx.row()][0], value == Qt.Checked)
                self.dataChanged.emit(idx, idx, [role])
                return True

        elif role == Qt.EditRole:
            if Id.depth(idx) == Id.Depth.D0:
                if idx.row() == Row.ModName:
                    self.mergeFile.name = value if value is not None else ""
                    self.dataChanged.emit(idx, idx, [role])
                    return True
                elif idx.row() == Row.PluginName:
                    self.mergeFile.pluginName = value if value is not None else ""
                    self.dataChanged.emit(idx, idx, [role])
                    return True
            elif Id.depth(idx) == Id.Depth.D1 and idx.parent().row() == Row.ZEditOptions:
                if idx.row() == OptionRow.Method:
                    if value in MergeFile.METHOD_VALUES:
                        self.mergeFile.method = value
                        self.dataChanged.emit(idx, idx, [role])
                        return True
                elif idx.row() == OptionRow.ArchiveAction:
                    if value in MergeFile.ARCHIVEACTION_VALUES:
                        self.mergeFile.archiveAction = value
                        self.dataChanged.emit(idx, idx, [role])
                        return True
        return False

