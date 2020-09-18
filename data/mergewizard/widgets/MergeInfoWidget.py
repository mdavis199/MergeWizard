from typing import List, Union
from PyQt5.QtCore import pyqtSignal, QModelIndex
from PyQt5.QtWidgets import QWidget, QHeaderView
from mergewizard.models.PluginModel import PluginModel
from mergewizard.models.MergeInfoModel import MergeInfoModel, Role, Row
from .ui.MergeInfoWidget import Ui_MergeInfoWidget
import mergewizard.models.ItemId as Id


class MergeInfoWidget(QWidget):
    # When the infoView is double-clicked, this signal is
    # emitted with the name of the plugin that was clicked.
    doubleClicked = pyqtSignal(str)

    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self.ui = Ui_MergeInfoWidget()
        self.ui.setupUi(self)
        self.expandedRows: List[bool] = [True for i in Row]

        self.ui.infoView.setModel(MergeInfoModel())
        self.ui.infoView.header().setSectionResizeMode(QHeaderView.ResizeToContents)

        self.ui.infoView.expanded.connect(self.onExpanded)
        self.ui.infoView.collapsed.connect(self.onCollapsed)
        self.ui.infoView.doubleClicked.connect(self.onViewDoubleClicked)
        self.ui.infoView.setHeaderHidden(True)

    def setPluginModel(self, model: PluginModel):
        self.infoModel().setSourceModel(model)

    def infoModel(self):
        return self.ui.infoView.model()

    def rootIndex(self):
        return self.ui.infoView.rootIndex()

    def setRootIndex(self, idx: QModelIndex = QModelIndex()):
        infoIdx = self.infoModel().index(idx.row(), 0)
        self.ui.infoView.setRootIndex(infoIdx)
        if not infoIdx.isValid():
            self.ui.groupBox.setTitle(self.tr("Merge Info"))
        else:
            title = self.infoModel().data(infoIdx.siblingAtColumn(1), Role.Cell)
            self.ui.groupBox.setTitle(self.tr("Merge Info:  ") + title)
            self.expandRowsFor(infoIdx)

    # ----
    # ---- Related to expanding/collapsing rows
    # ----

    def onExpanded(self, idx: QModelIndex):
        idx = self.infoModel().mapToSource(idx)
        self.expandedRows[idx.row()] = True

    def onCollapsed(self, idx: QModelIndex):
        idx = self.infoModel().mapToSource(idx)
        self.expandedRows[idx.row()] = False

    def expandRowsFor(self, parent: QModelIndex):
        idx = self.infoModel().mapToSource(parent)
        if idx.isValid:
            for row in Row:
                srcChild = self.infoModel().sourceModel().index(row, 0, idx)
                child = self.infoModel().mapFromSource(srcChild)
                if child.isValid():
                    self.ui.infoView.setExpanded(child, self.expandedRows[srcChild.row()])

    def getExpandedStates(self) -> int:
        result = 0
        for row in range(len(self.expandedRows)):
            if self.expandedRows[row]:
                result = result | (1 << row)
        return result

    def setExpandedStates(self, mask: Union[int, None]):
        if mask is not None:
            for row in range(len(self.expandedRows)):
                self.expandedRows[row] = bool(mask & (1 << row))

    # ----
    # ---- Double click handling
    # ----

    def onViewDoubleClicked(self, idx: QModelIndex):
        idx = self.infoModel().mapToSource(idx)
        if Id.depth(idx) == Id.Depth.D2:
            if idx.parent().row() == Row.MergedBy or idx.parent().row() == Row.MergedPlugins:
                name = self.infoModel().sourceModel().data(idx.siblingAtColumn(1))
                if name:
                    self.doubleClicked.emit(name)
