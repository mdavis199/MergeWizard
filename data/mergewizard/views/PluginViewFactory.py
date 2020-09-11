from enum import Enum, auto
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import QHeaderView, QAbstractItemView, QAction
from mergewizard.models.PluginModel import PluginModel
from mergewizard.models.PluginModelBase import Column, isBoolColumn, isPositionColumn
from mergewizard.models.PluginModelCollection import PluginModelCollection
from mergewizard.views.PluginView import PluginView, Action
from mergewizard.widgets.PositionDelegate import PositionDelegate


class ViewType(Enum):
    All = auto()
    Selected = auto()
    SelectedNoEdit = auto()
    Masters = auto()


def _configureColumns(type: ViewType, view: PluginView, excludeMergeColumns: bool):
    if type == ViewType.All:
        view._columns = [
            Column.IsInactive,
            Column.IsMissing,
            Column.IsMaster,
            Column.IsMerge,
            Column.IsMerged,
            Column.IsSelectedAsMaster,
            Column.IsSelected,
            Column.Priority,
            Column.PluginName,
            Column.ModName,
        ]
    elif type == ViewType.Selected:
        view._columns = [
            Column.PluginOrder,
            Column.PluginName,
            Column.IsInactive,
            Column.IsMissing,
            Column.IsMaster,
            Column.IsMerge,
            Column.IsMerged,
            Column.IsSelected,
        ]
    elif type == ViewType.SelectedNoEdit:
        view._columns = [
            Column.PluginOrder,
            Column.PluginName,
            Column.IsInactive,
            Column.IsMissing,
            Column.IsMaster,
            Column.IsMerge,
            Column.IsMerged,
            Column.IsSelected,
        ]
    elif type == ViewType.Masters:
        view._columns = [
            Column.MasterOrder,
            Column.PluginName,
            Column.IsInactive,
            Column.IsMissing,
            Column.IsMaster,
            Column.IsMerge,
            Column.IsMerged,
            Column.IsSelectedAsMaster,
        ]

    if excludeMergeColumns:
        view._columns = [c for c in view._columns if c not in [Column.IsMerge, Column.IsMerged]]


def _configureActions(type: ViewType, view: PluginView):
    if type == ViewType.Selected:
        view._actions = [
            Action.Cut,
            Action.Copy,
            Action.Paste,
            Action.Erase,
            Action.Sep1,
            Action.Select,
            Action.Sep2,
            Action.MoveTop,
            Action.MoveBottom,
            Action.MoveTo,
            Action.Sep3,
            Action.Activate,
            Action.Deactivate,
        ]
    elif type == ViewType.All:
        view._actions = [
            Action.Copy,
            Action.Sep1,
            Action.Select,
            Action.Sep2,
            Action.Add,
            Action.Remove,
            Action.Sep3,
            Action.Activate,
            Action.Deactivate,
        ]
    else:
        view._actions = [
            Action.Copy,
            Action.Sep1,
            Action.Select,
            Action.Sep2,
            Action.Activate,
            Action.Deactivate,
        ]


def _configureModels(type: ViewType, view: PluginView, model: PluginModel):
    models = PluginModelCollection(model)
    if type == ViewType.Selected:
        models.filterModel.showOnlySelected(True)
    elif type == ViewType.SelectedNoEdit:
        models.filterModel.showOnlySelected(True)
        models.styleModel.enableCheckDisplay(False)
        models.styleModel.enableReadonly(True)
    elif type == ViewType.Masters:
        models.filterModel.showOnlyMasters(True)
        models.styleModel.enableCheckDisplay(False)
        models.styleModel.enableReadonly(True)
    models.columnModel.setColumns(view._columns)
    view._models = models
    view.setModel(models.columnModel)


def _configureHeaders(type: ViewType, view: PluginView):
    view.header().setStretchLastSection(type == ViewType.All)
    for i in range(0, len(view._columns)):
        col = view._columns[i]
        if isBoolColumn(col):
            view.header().resizeSection(i, 22)
            view.header().setSectionResizeMode(i, QHeaderView.Fixed)
        elif isPositionColumn(col):
            view.setItemDelegateForColumn(i, PositionDelegate(view))
            view.header().setSectionResizeMode(i, QHeaderView.Interactive)
        elif col == Column.PluginName and type != ViewType.All:
            view.header().setSectionResizeMode(i, QHeaderView.Stretch)

    view.header().setSectionsMovable(False)
    view.header().setMinimumSectionSize(22)
    view.header().setCascadingSectionResizes(True)

    sortColumn = Column.PluginOrder
    if type == ViewType.All:
        sortColumn = Column.Priority
    elif type == ViewType.Masters:
        sortColumn = Column.MasterOrder
    view.sortByColumn(view._columns.index(sortColumn), Qt.AscendingOrder)


def _configureSignals(type: ViewType, view: PluginView):
    # toggle selected when the plugin name is double clicked
    if type == ViewType.All or type == ViewType.Selected:
        view.doubleClicked.connect(view.toggle)
    view.models().pluginModel.modelLoadingCompleted.connect(view.resizeColumns)


def _addActions(view: PluginView):
    for type in view._actions:
        a = QAction(view)
        a.setShortcutContext(Qt.WidgetShortcut)

        # The action's data property holds a boolean to indicate if the
        # action requires a selection for its operation

        if type == Action.Cut:
            a.setText(view.tr("Cut"))
            a.setShortcut(QKeySequence.Cut)
            a.setData(True)
            a.triggered.connect(lambda state, v=view: v.cut(v.selectedIndexes()))
        elif type == Action.Copy:
            a.setText(view.tr("Copy"))
            a.setShortcut(QKeySequence.Copy)
            a.setData(True)
            a.triggered.connect(lambda state, v=view: v.copy(v.selectedIndexes()))
        elif type == Action.Paste:
            a.setText(view.tr("Paste"))
            a.setShortcut(QKeySequence.Paste)
            a.setData(False)
            a.triggered.connect(lambda state, v=view: v.paste())
        elif type == Action.Erase:
            a.setText(view.tr("Remove"))
            a.setShortcut(QKeySequence.Delete)
            a.setData(True)
            a.triggered.connect(lambda state, v=view: v.erase(v.selectedIndexes()))
        elif type == Action.Select:
            a.setText(view.tr("Select All"))
            a.setShortcut(QKeySequence.SelectAll)
            a.setData(False)
            a.triggered.connect(lambda state, v=view: v.selectAll())
        elif type == Action.MoveTop:
            a.setText(view.tr("Move to Top"))
            a.setShortcut(Qt.CTRL + Qt.Key_T)
            a.setData(True)
            a.triggered.connect(lambda state, v=view: v.moveTop(v.selectedIndexes()))
        elif type == Action.MoveBottom:
            a.setText(view.tr("Move to Bottom"))
            a.setShortcut(Qt.CTRL + Qt.Key_B)
            a.setData(True)
            a.triggered.connect(lambda state, v=view: v.moveBottom(v.selectedIndexes()))
        elif type == Action.MoveTo:
            a.setText(view.tr("Move to ..."))
            a.setShortcut(Qt.CTRL + Qt.Key_M)
            a.setData(True)
            a.triggered.connect(lambda state, v=view: v.moveTo(v.selectedIndexes()))
        elif type == Action.Add:
            a.setText(view.tr("Add to Merge"))
            a.setShortcut(Qt.CTRL + Qt.Key_Right)
            a.setData(True)
            a.triggered.connect(lambda state, v=view: v.add(v.selectedIndexes()))
        elif type == Action.Remove:
            a.setText(view.tr("Remove from Merge"))
            a.setShortcut(Qt.CTRL + Qt.Key_Left)
            a.setData(True)
            a.triggered.connect(lambda state, v=view: v.remove(v.selectedIndexes()))
        elif type == Action.Activate:
            a.setText(view.tr("Activate"))
            a.setShortcut(Qt.ALT + Qt.Key_A)
            a.setData(True)
            a.triggered.connect(lambda state, v=view: v.activate(v.selectedIndexes()))
        elif type == Action.Deactivate:
            a.setText(view.tr("Deactivate"))
            a.setShortcut(Qt.ALT + Qt.Key_D)
            a.setData(True)
            a.triggered.connect(lambda state, v=view: v.deactivate(v.selectedIndexes()))
        else:
            a.setSeparator(True)
            a.setData(False)

        view.addAction(a)


class PluginViewFactory:
    excludeMergeColumns = False

    @staticmethod
    def configureView(type: ViewType, view: PluginView, model: PluginModel):
        if view is None:
            view = PluginView()

        view.setUniformRowHeights(True)
        view.setRootIsDecorated(False)
        view.setAllColumnsShowFocus(True)
        view.setSelectionBehavior(QAbstractItemView.SelectRows)
        view.setSelectionMode(QAbstractItemView.ExtendedSelection)
        view.setAlternatingRowColors(True)
        view.setContextMenuPolicy(Qt.DefaultContextMenu)
        view.setAcceptDrops(type == ViewType.Selected)
        view.viewport().setAcceptDrops(type == ViewType.Selected)

        if type == ViewType.All:
            view.setDragEnabled(True)
            view.setDragDropMode(QAbstractItemView.DragOnly)
            view.setDefaultDropAction(Qt.IgnoreAction)
            view.setSortingEnabled(True)
        elif type == ViewType.Selected:
            view.setDragEnabled(True)
            view.setDragDropMode(QAbstractItemView.DragDrop)
            view.setDefaultDropAction(Qt.MoveAction)
            view.setSortingEnabled(False)
        elif type == ViewType.SelectedNoEdit:
            view.setDragEnabled(True)
            view.setDragDropMode(QAbstractItemView.DragOnly)
            view.setDefaultDropAction(Qt.IgnoreAction)
            view.setSortingEnabled(True)
        elif type == ViewType.Masters:
            view.setDragEnabled(True)
            view.setDragDropMode(QAbstractItemView.DragOnly)
            view.setDefaultDropAction(Qt.IgnoreAction)
            view.setSortingEnabled(True)
        else:
            return

        _configureColumns(type, view, PluginViewFactory.excludeMergeColumns)
        _configureModels(type, view, model)
        _configureHeaders(type, view)
        _configureSignals(type, view)
        _configureActions(type, view)
        _addActions(view)
        return view
