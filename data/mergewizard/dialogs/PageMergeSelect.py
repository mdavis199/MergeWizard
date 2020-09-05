from PyQt5.QtCore import QItemSelectionModel, QModelIndex, qInfo
from PyQt5.QtWidgets import QWidget, QHeaderView
from mergewizard.dialogs.WizardPage import WizardPage
from mergewizard.domain.Context import Context
from mergewizard.models.MergeModel import MergeSortModel

from .ui.PageMergeSelect import Ui_PageMergeSelect


class PageMergeSelect(WizardPage):

    PROGRESS_OFFSET = 10

    def __init__(self, context: Context, parent: QWidget = None):
        super().__init__(parent)
        self.ui = Ui_PageMergeSelect()
        self.ui.setupUi(self)
        self.context = context
        self.registerField("selectedMerge*", self.ui.selectedMerge)

        mergeSortModel = MergeSortModel()
        mergeSortModel.setSourceModel(context.mergeModel())
        self.ui.mergeView.setModel(mergeSortModel)
        self.ui.mergeView.header().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.ui.mergeView.clicked.connect(self.itemClicked)
        self.ui.mergeView.selectionModel().selectionChanged.connect(lambda: self.selectionChanged())
        self.ui.sortByPriority.clicked.connect(mergeSortModel.sortByPriority)
        self.ui.progressBar.setRange(0, 100 + self.PROGRESS_OFFSET)
        context.mergeModel().modelLoadingStarted.connect(self.modelLoadingStarted)
        context.mergeModel().modelLoadingProgress.connect(self.modelLoadingProgress)
        context.mergeModel().modelLoadingCompleted.connect(self.modelLoadingCompleted)

    def initializePage(self):
        self.context.mergeModel().loadMerges()
        pass

    def deinitializePage(self) -> None:
        pass

    def getSelectedMergeName(self):
        return self.ui.selectedMerge.text()

    def selectionChanged(self):
        indexes = self.ui.mergeView.selectionModel().selectedRows(0)
        self.selectIndex(indexes[0] if indexes else QModelIndex())

    def selectIndex(self, idx: QModelIndex = QModelIndex()):
        name = self.ui.mergeView.model().data(idx)
        self.ui.selectedMerge.setText(name if name else "")
        self.ui.mergeView.model().setSelectedMerge(idx)

    def itemClicked(self, idx: QModelIndex):
        if idx.parent().isValid():
            self.ui.mergeView.selectionModel().select(
                idx.parent(), QItemSelectionModel.ClearAndSelect | QItemSelectionModel.Rows
            )
            self.selectIndex(idx.parent())

    def modelLoadingStarted(self):
        self.ui.progressBar.setVisible(True)
        self.ui.progressBar.setValue(self.PROGRESS_OFFSET)

    def modelLoadingCompleted(self):
        self.ui.progressFrame.setVisible(False)
        self.ui.mergeView.selectionModel().select(
            self.ui.mergeView.model().index(0, 0), QItemSelectionModel.Select | QItemSelectionModel.Rows
        )

    def modelLoadingProgress(self, value):
        self.ui.progressBar.setValue(value + self.PROGRESS_OFFSET)
