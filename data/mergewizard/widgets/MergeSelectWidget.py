from PyQt5.QtCore import QItemSelectionModel, QModelIndex
from PyQt5.QtWidgets import QWidget, QHeaderView

from mergewizard.models.MergeModel import MergeSortModel, MergeModel
from .ui.MergeSelectWidget import Ui_MergeSelectWidget


class MergeSelectWidget(QWidget):
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self.ui = Ui_MergeSelectWidget()
        self.ui.setupUi(self)

    def setMergeModel(self, mergeModel: MergeModel):
        mergeSortModel = MergeSortModel()
        mergeSortModel.setSourceModel(mergeModel)
        self.ui.mergeView.setModel(mergeSortModel)
        self.ui.mergeView.header().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.ui.mergeView.clicked.connect(self.itemClicked)
        self.ui.mergeView.selectionModel().selectionChanged.connect(lambda: self.selectionChanged())
        self.ui.sortByPriority.clicked.connect(mergeSortModel.sortByPriority)
        self.ui.selectMergeButton.setEnabled(False)

    def getSelectedMergeName(self):
        return self.ui.selectedMerge.text()

    def selectionChanged(self):
        indexes = self.ui.mergeView.selectionModel().selectedRows(0)
        self.selectIndex(indexes[0] if indexes else QModelIndex())

    def selectIndex(self, idx: QModelIndex = QModelIndex()):
        name = self.ui.mergeView.model().data(idx)
        self.ui.selectedMerge.setText(name if name else "")
        self.ui.selectMergeButton.setEnabled(bool(name))
        self.ui.mergeView.model().setSelectedMerge(idx)

    def itemClicked(self, idx: QModelIndex):
        if idx.parent().isValid():
            self.ui.mergeView.selectionModel().select(
                idx.parent(), QItemSelectionModel.ClearAndSelect | QItemSelectionModel.Rows
            )
            self.selectIndex(idx.parent())

