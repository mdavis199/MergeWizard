from PyQt5.QtCore import QItemSelectionModel, QModelIndex, Qt, qInfo
from PyQt5.QtWidgets import QWidget, QHeaderView

from mergewizard.models.MergeModel import MergeSortModel, MergeModel, Column
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
        self.ui.mergeView.header().resizeSection(Column.Active, 43)
        # self.ui.mergeView.header().setSectionResizeMode(Column.Active, QHeaderView.ResizeToContents)
        self.ui.mergeView.header().setSectionResizeMode(Column.Name, QHeaderView.ResizeToContents)
        self.ui.mergeView.clicked.connect(self.itemClicked)
        self.ui.mergeView.selectionModel().selectionChanged.connect(lambda: self.selectionChanged())
        self.ui.sortByPriority.clicked.connect(mergeSortModel.sortByPriority)
        self.ui.selectMergeButton.setEnabled(False)

    def getSelectedMergeName(self):
        return self.ui.selectedMerge.text()

    def selectMergeByName(self, name):
        if name:
            model = self.ui.mergeView.model()
            idx = model.indexForMergeName(name)
            if idx.isValid():
                self.ui.mergeView.selectionModel().setCurrentIndex(
                    idx, QItemSelectionModel.ClearAndSelect | QItemSelectionModel.Rows
                )

    def selectionChanged(self):
        indexes = self.ui.mergeView.selectionModel().selectedRows(Column.Name)
        self.selectIndex(indexes[0] if indexes else QModelIndex())

    def selectIndex(self, idx: QModelIndex = QModelIndex()):
        name = self.ui.mergeView.model().data(idx.siblingAtColumn(Column.Name))
        self.ui.selectedMerge.setText(name if name else "")
        self.ui.selectMergeButton.setEnabled(bool(name))
        self.ui.mergeView.model().setSelectedMerge(idx)

    def itemClicked(self, idx: QModelIndex):
        if idx.parent().isValid():
            self.ui.mergeView.selectionModel().select(
                idx.parent(), QItemSelectionModel.ClearAndSelect | QItemSelectionModel.Rows
            )
            self.selectIndex(idx.parent())
