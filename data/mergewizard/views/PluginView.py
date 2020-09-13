from enum import Enum, auto
from typing import List
from PyQt5.QtCore import pyqtSignal, Qt, QModelIndex
from PyQt5.QtGui import QContextMenuEvent
from PyQt5.QtWidgets import (
    QWidget,
    QTreeView,
    QDialogButtonBox,
    QDialog,
    QMenu,
    QFormLayout,
    QApplication,
    QSpinBox,
)

from mergewizard.models.PluginModelBase import Column, DEFAULT_MIME_FORMAT
from mergewizard.models.PluginFilterModel import Filter
from mergewizard.models.PluginModelCollection import PluginModelCollection


class Action(Enum):
    Cut = auto()
    Copy = auto()
    Paste = auto()
    Erase = auto()
    Sep1 = auto()
    Select = auto()
    Sep2 = auto()
    MoveTop = auto()
    MoveBottom = auto()
    MoveTo = auto()
    Add = auto()
    Remove = auto()
    Sep3 = auto()
    Activate = auto()
    Deactivate = auto()


class PluginView(QTreeView):

    filterChanged = pyqtSignal()

    ColumnFilters = [
        Filter.Inactive,
        Filter.Missing,
        Filter.Masters,
        Filter.Merges,
        Filter.Merged,
        Filter.SelectedAsMaster,
        Filter.Selected,
    ]

    def __init__(self, parent: QWidget):
        QTreeView.__init__(self, parent)
        self._columns: List[Column] = []
        self._actions: List[Action] = []
        self._models: PluginModelCollection = None

    def models(self):
        return self._models

    def resizeColumns(self):
        for i in range(len(self._columns)):
            self.resizeColumnToContents(i)

    def sectionForColumn(self, column: Column):
        return next((i for i in range(len(self._columns)) if self._columns[i] == column), -1)

    # ---- Methods related to filters

    def sectionForFilter(self, filtr: Filter) -> int:
        if filtr == Filter.Inactive:
            return self.sectionForColumn(Column.IsInactive)
        if filtr == Filter.Missing:
            return self.sectionForColumn(Column.IsMissing)
        if filtr == Filter.Masters:
            return self.sectionForColumn(Column.IsMaster)
        if filtr == Filter.Merges:
            return self.sectionForColumn(Column.IsMerge)
        if filtr == Filter.Merged:
            return self.sectionForColumn(Column.IsMerged)
        if filtr == Filter.SelectedAsMaster:
            return self.sectionForColumn(Column.IsSelectedAsMaster)
        if filtr == Filter.Selected:
            return self.sectionForColumn(Column.IsSelected)
        return -1

    def setFilter(self, filtr: Filter, enabled: bool):
        self._models.filterModel.setFilter(filtr, enabled)
        filters = self._models.filterModel.filters()

        for f in self.ColumnFilters:
            self.setColumnHidden(self.sectionForFilter(f), bool(filters & f))

    def setNameFilter(self, text: str):
        self._models.filterModel.setNameFilter(text)
        self.filterChanged.emit()

    # ---- Methods related to Actions

    def enableActions(self, force: bool):
        """
        This disables / re-enables actions so that only "actionable" actions are
        enabled when the context menu is shown.   When a context menu is closed, the
        actions are forced to enabled so that they can be invoked with their shortcut
        keys.

        The PluginViewFactory sets the action's data property to true if a selection
        is required for it's operation.
        """
        enable = True if force else self.selectionModel().hasSelection()
        for i in range(0, len(self._actions)):
            if self._actions[i] == Action.Paste:
                self.actions()[i].setEnabled(
                    True if force else QApplication.clipboard().mimeData().hasFormat(DEFAULT_MIME_FORMAT)
                )
            elif self.actions()[i].data():
                self.actions()[i].setEnabled(enable)

    def contextMenuEvent(self, event: QContextMenuEvent):
        menu = QMenu(self)
        menu.addActions(self.actions())
        self.enableActions(False)
        menu.exec(event.globalPos())
        self.enableActions(True)

    def cut(self, indexes: List[QModelIndex]):
        self.copy(indexes)
        self.erase(indexes)

    def erase(self, indexes: List[QModelIndex]):
        if len(indexes):
            self._models.pluginModel.selectPlugins(
                self._models.indexesForModel(indexes, self._models.pluginModel), False
            )

    def copy(self, indexes: List[QModelIndex]):
        if len(indexes):
            QApplication.clipboard().setMimeData(self.model().mimeData(self.selectedIndexes()))

    def paste(self):
        if QApplication.clipboard().mimeData().hasFormat(DEFAULT_MIME_FORMAT):
            self.model().dropMimeData(
                QApplication.clipboard().mimeData(), Qt.MoveAction, self.currentIndex().row(), -1, QModelIndex(),
            )

    def moveTop(self, indexes: List[QModelIndex]):
        if len(indexes):
            self._models.pluginModel.setPluginsOrder(self._models.indexesForModel(indexes, self._models.pluginModel), 0)

    def moveBottom(self, indexes: List[QModelIndex]):
        if len(indexes):
            self._models.pluginModel.setPluginsOrder(
                self._models.indexesForModel(indexes, self._models.pluginModel), self.model().rowCount(),
            )

    def moveTo(self, indexes: List[QModelIndex]):
        if len(indexes) == 0:
            return
        dlg = QDialog()
        dlg.setWindowTitle(self.tr("Insert Plugins"))
        layout = QFormLayout(dlg)
        spinBox = QSpinBox()
        spinBox.setRange(1, self.model().rowCount())
        spinBox.setAccelerated(True)
        spinBox.setMaximumWidth(100)
        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttonBox.accepted.connect(dlg.accept)
        buttonBox.rejected.connect(dlg.reject)
        layout.addRow(self.tr("Position:"), spinBox)
        layout.addWidget(buttonBox)

        if dlg.exec() == QDialog.Accepted:
            idx = indexes[0]
            currentValue = idx.model().data(idx.siblingAtColumn(0), Qt.EditRole)
            newValue = spinBox.value() - 1
            if newValue == currentValue:
                return
            if newValue > currentValue:
                newValue = newValue + 1
            self._models.pluginModel.setPluginsOrder(
                self._models.indexesForModel(indexes, self._models.pluginModel), newValue,
            )

    def add(self, indexes: List[QModelIndex]):
        if len(indexes):
            self._models.pluginModel.selectPlugins(
                self._models.indexesForModel(indexes, self._models.pluginModel), True
            )

    def remove(self, indexes: List[QModelIndex]):
        if len(indexes):
            self._models.pluginModel.selectPlugins(
                self._models.indexesForModel(indexes, self._models.pluginModel), False
            )

    def toggle(self, idx: QModelIndex):
        self._models.filterModel.toggleSelected(self._models.indexForModel(idx, self._models.filterModel))

    def activate(self, indexes: List[QModelIndex]):
        if len(indexes):
            self._models.pluginModel.activatePlugins(self._models.indexesForModel(indexes, self._models.pluginModel))

    def deactivate(self, indexes: List[QModelIndex]):
        if len(indexes):
            self._models.pluginModel.deactivatePlugins(self._models.indexesForModel(indexes, self._models.pluginModel))
