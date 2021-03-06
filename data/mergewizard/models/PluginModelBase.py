from enum import IntEnum, auto
from typing import List, Set
import copy

from PyQt5.QtCore import (
    pyqtSignal,
    Qt,
    QDataStream,
    QIODevice,
    QObject,
    QMimeData,
    QModelIndex,
    QAbstractItemModel,
)

from mergewizard.domain.plugin import Plugin, Plugins
from mergewizard.domain.MOLog import moWarn


DEFAULT_MIME_FORMAT = "application/x-qabstractitemmodeldatalist"


class Role(IntEnum):
    Cell = Qt.UserRole  # value represented by column
    Data = Qt.UserRole + 1  # plugin represented by row
    Associations = Qt.UserRole + 2  # used by the info model
    MergeAssociations = Qt.UserRole + 3


# The columns are ordered to reduce the number of emits.
# Check for side-effects before changing the column order here.


class Column(IntEnum):
    PluginName = 0
    ModName = auto()
    ModPath = auto()
    IsMOPlugin = auto()  # a plugin MO knows about, not one we added
    IsMaster = auto()  # data from MO2
    #
    IsMerge = auto()  # Created by a merge
    IsMerged = auto()  # Consumed by one or more merges
    #
    Priority = auto()  # determined by MO2
    IsHidden = auto()
    IsMissing = auto()
    IsInactive = auto()
    #
    PluginOrder = auto()  # position of selected plugins
    IsSelected = auto()  # calculated value
    #
    MasterOrder = auto()  # position of selected plugins' required plugins
    IsSelectedAsMaster = auto()  # calculated value


def isBoolColumn(col: Column):
    return col in [
        Column.IsSelectedAsMaster,
        Column.IsSelected,
        Column.IsMOPlugin,
        Column.IsMissing,
        Column.IsHidden,
        Column.IsInactive,
        Column.IsMaster,
        Column.IsMerge,
        Column.IsMerged,
    ]


# A position column displays the value as 'value + 1'
def isPositionColumn(col: Column):
    return col in [Column.PluginOrder, Column.MasterOrder]


class PluginModelBase(QAbstractItemModel):
    """ A fully functional Plugin model for QAbstractItemViews.

    It has no direct interactions with MO interfaces.  (Those are provided by
    the PluginModel subclass.)

    Formatting, sorting and filtering are performed by proxy classes.
    """

    # When selected plugins change, we update the selected masters
    _selectedPluginsChanged = pyqtSignal()

    # When the plugins are completely reset, we emit this after loading is completed
    modelLoadingCompleted = pyqtSignal()

    def __init__(self, parent: QObject = None):
        super().__init__(parent)
        self._plugins: Plugins = Plugins()
        self._selected: List[int] = []  # ordered list of selected plugins (user sets order)
        self._masters: List[int] = []  # ordered list of required plugins for all selected plugins (priority order)
        self._selectedPluginsChanged.connect(self.selectMasters)

    # ------------------------------------------------
    # ---- Methods related to initializing model data
    # ------------------------------------------------

    def setPlugins(self, plugins: Plugins) -> None:
        if len(self._plugins) > 1:
            self.beginRemoveRows(QModelIndex(), 0, len(self._plugins) - 1)
            self._plugins.clear()
            self.endRemoveRows()
        self._selected.clear()
        self._masters.clear()
        if plugins:
            self.beginInsertRows(QModelIndex(), 0, len(plugins) - 1)
            self._plugins = plugins
            self.endInsertRows()
        self.modelLoadingCompleted.emit()

    # ------------------------------------------------
    # --- Get names of selected plugins
    # ------------------------------------------------

    def selectedPluginNames(self):
        return [self._plugins[row].pluginName for row in self._selected]

    def selectedPluginPaths(self):
        return [self._plugins[row].modPath for row in self._selected]

    def selectedMastersNames(self):
        return [self._plugins[row].pluginName for row in self._masters]

    def loadOrderNames(self):
        return [p.pluginName for p in sorted(self._plugins.values(), key=Plugin.priority_sort) if not p.isMissing]

    # ------------------------------------------------
    # --- Find index for plugin name
    # ------------------------------------------------
    def indexForPluginName(self, name: str) -> QModelIndex:
        key = name.lower()
        row = next((i for i in range(len(self._plugins)) if self._plugins[i].key == key), -1)
        return self.index(row, Column.PluginName)

    # -------------------------------------------------
    # --- General queries -- used primarily by the ActionModel
    # --- and ActionWidget
    # -------------------------------------------------

    def missingPluginsAreSelected(self) -> bool:
        for row in self._selected:
            if self._plugins[row].isMissing:
                return True
        for row in self._masters:
            if self._plugins[row].isMissing:
                return True
        return False

    def selectedCount(self) -> int:
        return len(self._selected)

    def mastersCount(self) -> int:
        return len(self._masters)

    def selectedRows(self) -> List[int]:
        return copy.copy(self._selected)

    def selectedMasters(self) -> List[int]:
        """ Returns list of rows selected as masters but not selected to merge.
        This exists only because it makes for a better log message. """
        return [m for m in self._masters if not self._plugins[m].isSelected]

    def maxPriority(self):
        if not self._plugins:
            return -1
        return max(plugin.priority for plugin in self._plugins.values())

    # ------------------------------------------------
    # ---- Methods related to plugin order and selection
    # ------------------------------------------------

    def selectPluginsByName(self, names: List[str]):
        if not names:
            return
        indexes = []
        startIndex = self.index(0, Column.PluginName)
        for n in names:
            matches = self.match(startIndex, Qt.DisplayRole, n, 1, Qt.MatchExactly)
            if matches:
                indexes.append(matches[0])
            else:
                moWarn(self.tr("Failed to select plugin: {}").format(n))
        if indexes:
            self.selectPlugins(indexes, True)

    def resetPluginSelection(self):
        indexes = [self.index(self._selected[row], 0) for row in range(len(self._selected))]
        self.selectPlugins(indexes, False)

    def selectPluginAtRow(self, row: int, select: bool):
        self.selectPlugin(self.index(row, 0), select)

    def selectPlugin(self, idx: QModelIndex, select: bool):
        if self._plugins[idx.row()].pluginOrder == Plugin.NOT_SELECTED:
            if select:
                self.setPluginsOrder([idx], len(self._plugins))
        else:
            if not select:
                self.setPluginsOrder([idx], Plugin.NOT_SELECTED)

    def selectPlugins(self, indexes: List[QModelIndex], select: bool):
        self.setPluginsOrder(indexes, len(self._plugins) if select else Plugin.NOT_SELECTED)

    def setPluginOrder(self, idx: QModelIndex, position: int):
        self.setPluginsOrder([idx.siblingAtColumn(0)], position)

    def setPluginsOrder(self, indexes: List[QModelIndex], position: int):
        if position == Plugin.NOT_SELECTED:
            for idx in indexes:
                row = idx.row()
                if self._plugins[row].pluginOrder != Plugin.NOT_SELECTED:
                    self._selected[self._plugins[row].pluginOrder] = Plugin.NOT_SELECTED
                    self._plugins[row].pluginOrder = Plugin.NOT_SELECTED
                    self.dataChanged.emit(self.index(row, Column.PluginOrder), self.index(row, Column.IsSelected))
        else:
            if position > len(self._selected):
                position = len(self._selected)

            inserts = 0
            for i in range(len(indexes) - 1, -1, -1):
                idx = indexes[i]
                row = idx.row()
                oldPosition = self._plugins[row].pluginOrder

                if oldPosition != position and (position == len(self._selected) or self._selected[position] != row):
                    self._selected.insert(position, row)
                    inserts = inserts + 1

                if oldPosition != Plugin.NOT_SELECTED:
                    offset = 0 if oldPosition < position else inserts
                    self._selected[oldPosition + offset] = Plugin.NOT_SELECTED

        self._selected = list(filter(lambda a: a != Plugin.NOT_SELECTED, self._selected))
        for i in range(len(self._selected)):
            if self._plugins[self._selected[i]].pluginOrder != i:
                self._plugins[self._selected[i]].pluginOrder = i
                idx = self.index(self._selected[i], Column.PluginOrder)
                self.dataChanged.emit(
                    self.index(self._selected[i], Column.IsSelected), self.index(self._selected[i], Column.IsSelected)
                )

        # Selected plugins changed, so the selected masters must change
        # Emit a signal to start the process of updating the list of selected masters
        self._selectedPluginsChanged.emit()

    # ------------------------------------------------
    # --- Methods related to adding the masters of selected plugins
    # ------------------------------------------------

    def selectMasters(self):
        # Each plugin stores a recursive list of its required plugins, so we do not have to
        # recurse through the "masters of the masters" here. Instead, we combine the masters
        # of all selected plugins and remove the duplicates.

        requiredPlugins = set()
        for row in self._selected:
            for req in self._plugins.requirements(self._plugins[row]):
                requiredPlugins.add(req.plugin)
        sortedRequired = sorted(requiredPlugins, key=Plugin.priority_sort)
        requiredRows = [self._plugins.index(p.key) for p in sortedRequired]

        changed: Set[int] = set()
        for i in range(min(len(self._masters), len(requiredRows))):
            if self._masters[i] != requiredRows[i]:
                changed.update([self._masters[i], requiredRows[i]])
        if len(self._masters) > len(requiredRows):
            changed.update(self._masters[len(requiredRows) :])
        elif len(requiredRows) > len(self._masters):
            changed.update(requiredRows[len(self._masters) :])

        for row in changed:
            if row not in requiredRows:
                self._plugins[row].masterOrder = Plugin.NOT_SELECTED
            else:
                self._plugins[row].masterOrder = requiredRows.index(row)
            self.dataChanged.emit(self.index(row, Column.MasterOrder), self.index(row, Column.IsSelectedAsMaster))
        self._masters = requiredRows

    # ------------------------------------------------
    # --- AbstractItemModel overrides
    # ------------------------------------------------

    def rowCount(self, parent: QModelIndex = QModelIndex()):
        if not parent.isValid():
            return len(self._plugins)
        return 0

    def columnCount(self, parent: QModelIndex = QModelIndex()):
        if not parent.isValid():
            return len(Column)
        return 0

    def index(self, row: int, col: int, parent: QModelIndex = QModelIndex()):
        if self.hasIndex(row, col, parent):
            return self.createIndex(row, col, 0)
        return QModelIndex()

    def parent(self, idx: QModelIndex):
        return QModelIndex()

    def data(self, idx: QModelIndex, role: int = Qt.DisplayRole):
        if not idx.isValid():
            return None
        if role == Qt.DisplayRole or role == Qt.EditRole or role == Role.Cell:
            col = idx.column()
            if col == Column.PluginName:
                return self._plugins[idx.row()].pluginName
            if col == Column.ModName:
                return self._plugins[idx.row()].modName
            if col == Column.ModPath:
                return self._plugins[idx.row()].modPath
            if col == Column.Priority:
                return self._plugins[idx.row()].priority
            if col == Column.PluginOrder:
                return self._plugins[idx.row()].pluginOrder
            if col == Column.MasterOrder:
                return self._plugins[idx.row()].masterOrder
            if col == Column.IsMOPlugin:
                return self._plugins[idx.row()].isMOPlugin
            if col == Column.IsMissing:
                return self._plugins[idx.row()].isMissing
            if col == Column.IsHidden:
                return self._plugins[idx.row()].isHidden
            if col == Column.IsInactive:
                return self._plugins[idx.row()].isInactive
            if col == Column.IsMaster:
                return self._plugins[idx.row()].isMaster
            if col == Column.IsMerge:
                return self._plugins[idx.row()].isMerge
            if col == Column.IsMerged:
                return self._plugins[idx.row()].isMerged
            if col == Column.IsSelectedAsMaster:
                return self._plugins[idx.row()].isSelectedAsMaster
            if col == Column.IsSelected:
                return self._plugins[idx.row()].isSelected
        elif role == Role.Data:
            return self._plugins[idx.row()]
        elif role == Role.Associations:
            return self._plugins.associations(self._plugins[idx.row()])
        elif role == Role.MergeAssociations:
            return self._plugins.mergeAssociations(self._plugins[idx.row()])

    # TODO: add setting master from here maybe
    def setData(self, idx: QModelIndex, value, role: int = Qt.EditRole):
        if not idx.isValid() or role != Qt.EditRole:
            return False
        if idx.column() == Column.Priority:
            self._plugins[idx.row()].Priority = value
            self.dataChanged.emit(idx, idx, [role])
            return True
        if idx.column() == Column.PluginOrder:
            self.setPluginOrder(idx, int(value))
            return True
        if idx.column() == Column.IsMOPlugin:
            self._plugins[idx.row()].isMOPlugin = value
            self.dataChanged.emit(idx, idx, [role])
            return True
        if idx.column() == Column.IsMissing:
            self._plugins[idx.row()].isMissing = value
            self.dataChanged.emit(idx, idx, [role])
            return True
        if idx.column() == Column.IsHidden:
            self._plugins[idx.row()].isMissing = value
            self.dataChanged.emit(idx, idx, [role])
            return True
        if idx.column() == Column.IsInactive:
            self._plugins[idx.row()].isInactive = value
            self.dataChanged.emit(idx, idx, [role])
            return True
        if idx.column() == Column.IsMaster:
            self._plugins[idx.row()].isMaster = value
            self.dataChanged.emit(idx, idx, [role])
            return True
        if idx.column() == Column.IsMerge:
            self._plugins[idx.row()].isMerge = value
            self.dataChanged.emit(idx, idx, [role])
            return True
        if idx.column() == Column.IsMerged:
            self._plugins[idx.row()].isMerged = value
            self.dataChanged.emit(idx, idx, [role])
            return True
        if idx.column() == Column.IsSelected:
            self.selectPlugin(idx, bool(value))
            return True
        return False

    def flags(self, idx: QModelIndex):
        DEFAULT_FLAGS = Qt.ItemIsEnabled | Qt.ItemNeverHasChildren | Qt.ItemIsSelectable
        if not idx.isValid() or idx.parent().isValid():
            return Qt.ItemIsDropEnabled
        if idx.column() == Column.PluginName:
            return DEFAULT_FLAGS | Qt.ItemIsDragEnabled
        if idx.column() == Column.PluginOrder or idx.column() == Column.IsSelected:
            return DEFAULT_FLAGS | Qt.ItemIsEditable
        return DEFAULT_FLAGS

    # ------------------------------------------------
    # ---- Drag & Drop Methods
    # ------------------------------------------------

    def supportDropActions(self):
        return Qt.MoveAction

    def mimeTypes(self):
        return [DEFAULT_MIME_FORMAT, "text/plain"]

    def mimeData(self, indexes: List[QModelIndex]):
        if not indexes or not self.mimeTypes():
            return

        rows = []
        textList = []
        for idx in indexes:
            if idx.isValid() and not idx.row() in rows:
                rows.append(idx.row())
                textValue = self._plugins[idx.row()].pluginName
                if self._plugins[idx.row()].modName:
                    textValue = textValue + " | " + self._plugins[idx.row()].modName + " |"
                textList.append(textValue)

        newIndexes = []
        for row in rows:
            newIndexes.append(self.index(row, Column.PluginName))

        data = super().mimeData(newIndexes)
        data.setText("\n".join(textList))
        return data

    def dropMimeData(
        self, data: QMimeData, action: Qt.DropAction, row: int = -1, col: int = -1, parent: QModelIndex = QModelIndex(),
    ):
        if action == Qt.IgnoreAction or not data or not data.hasFormat(DEFAULT_MIME_FORMAT):
            return True

        if row < 0 or row > len(self._selected):
            position = len(self._selected)
        else:
            position = self._plugins[row].pluginOrder

        encoded = data.data(DEFAULT_MIME_FORMAT)
        stream = QDataStream(encoded, QIODevice.ReadOnly)

        indexes = []
        while not stream.atEnd():
            srcRow = stream.readInt32()
            stream.readInt32()  # src column
            mapItems = stream.readInt32()  # role data map
            for i in range(mapItems):
                stream.readInt32()  # map role ID
                stream.readQVariant()  # map role value
            indexes.append(self.index(srcRow, 0))

        self.setPluginsOrder(indexes, position)
        return False
