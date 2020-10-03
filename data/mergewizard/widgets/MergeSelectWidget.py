from PyQt5.QtCore import QItemSelectionModel, QModelIndex
from PyQt5.QtWidgets import QWidget, QHeaderView

from mergewizard.domain.MOLog import moWarn
from mergewizard.models.MergeModel import MergeSortModel, MergeModel, Column
from .ui.MergeSelectWidget import Ui_MergeSelectWidget


"""
Behaviors:
- User clicks on a pluginRow, it's the parent(Mod Name) that is selected.
- The selectedMerge text box, reflects the merge name selected in the view, not
  necessarily the current merge in the MergeModel.
- The MergeModel's current merge is changed only when:
  - the user clicks the Select Plugins button, or
  - the method selectMergeByName is called by another class

After this class notifies the MergeModel to select the merge,
the MergeModel emits a signal other classes can monitor for merge selection changes.

"""


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
        self.ui.selectMergeButton.setEnabled(False)

        # signals
        self.ui.selectMergeButton.clicked.connect(self._setCurrentMerge)
        self.ui.mergeView.clicked.connect(self._itemClicked)
        self.ui.mergeView.selectionModel().selectionChanged.connect(lambda: self._selectionChanged())
        self.ui.sortByPriority.clicked.connect(mergeSortModel.sortByPriority)

    def selectMergeByName(self, name):
        """ This will select the merge in the view, causing the text box to also update, and
        will update the MergeModel's current merge.  This is one of this class's two ways
        of updating the MergeModel.
        The view emits a selectionChanged signal
        """
        flags = QItemSelectionModel.Clear | QItemSelectionModel.SelectCurrent | QItemSelectionModel.Rows
        model = self.ui.mergeView.model()
        idx = model.index(0, Column.Name)
        if name:
            idxForName = model.indexForMergeName(name)
            if not idxForName.isValid():
                moWarn("Failed to load merge: {}".format(name))
            else:
                idx = idxForName
        self.ui.mergeView.selectionModel().select(idx, flags)
        # update the current merge in the MergeModel
        self._setCurrentMerge(idx)

    def _setCurrentMerge(self, idx=None):
        """ This method notifies the MergeModel of the merge selection. """
        if not idx:
            indexes = self.ui.mergeView.selectionModel().selectedRows(Column.Name)
            idx = indexes[0] if indexes else QModelIndex()
        self.ui.mergeView.model().setCurrentMerge(idx)

    # ------------------------------------------------------------------------

    def _selectionChanged(self):
        """ Called when the selection in the view changes. We update the text box, and button """
        indexes = self.ui.mergeView.selectionModel().selectedRows(Column.Name)
        idx = indexes[0] if indexes else QModelIndex()
        name = self.ui.mergeView.model().data(idx.siblingAtColumn(Column.Name))
        self.ui.selectedMerge.setText(name if name else "")
        self.ui.selectMergeButton.setEnabled(bool(name))

    def _itemClicked(self, idx: QModelIndex):
        """ If the user clicks on the plugin, we choose its parent Merge.
        The view emits a selectionChanged signal. """
        if idx.parent().isValid():
            self.ui.mergeView.selectionModel().select(
                idx.parent(), QItemSelectionModel.ClearAndSelect | QItemSelectionModel.Rows
            )
