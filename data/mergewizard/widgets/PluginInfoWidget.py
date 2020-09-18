from typing import List
from PyQt5.QtCore import pyqtSignal, QModelIndex, QPoint, Qt
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import QWidget, QApplication, QMenu, QAction
from mergewizard.models.PluginModel import PluginModel
from mergewizard.models.PluginInfoModel import PluginInfoModel, Column
from .ui.PluginInfoWidget import Ui_PluginInfoWidget


class PluginInfoWidget(QWidget):
    # When the infoView is double-clicked, this signal is
    # emitted with the name of the plugin that was clicked.
    doubleClicked = pyqtSignal(str)

    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self.ui = Ui_PluginInfoWidget()
        self.ui.setupUi(self)

    def setPluginModel(self, model: PluginModel):
        if self.ui.infoView.model():
            raise RuntimeError("Replacing plugin model is not supported")
        infoModel = PluginInfoModel(model)
        infoModel.includeIndirect(self.ui.indirectCheckBox.isChecked())
        infoModel.sortByPriority(self.ui.sortCheckBox.isChecked())
        self.ui.infoView.setModel(infoModel)
        self.ui.infoView.setContextMenuPolicy(Qt.CustomContextMenu)
        self.ui.infoView.customContextMenuRequested.connect(self.showContextMenu)
        self.ui.infoView.doubleClicked.connect(self.onViewDoubleClicked)
        self.ui.sortCheckBox.clicked.connect(lambda: self.infoModel().sortByPriority(self.ui.sortCheckBox.isChecked()))
        self.ui.indirectCheckBox.clicked.connect(
            lambda: self.infoModel().includeIndirect(self.ui.indirectCheckBox.isChecked())
        )
        self.addInfoViewActions()

    def model(self):
        return self.ui.infoView.model()

    def infoModel(self):
        return self.model()

    def pluginModel(self):
        return self.infoModel().sourceModel()

    def rootIndex(self):
        return self.ui.infoView.rootIndex()

    # There is a one-to-one mapping between the (top) rows of the info model
    # and the plugin model.
    # The index here may be from either model, as only the row is used.
    def setRootIndex(self, idx: QModelIndex = QModelIndex()):
        infoIdx = self.infoModel().index(idx.row(), Column.PluginName)
        self.ui.infoView.setRootIndex(infoIdx)
        title = self.infoModel().data(infoIdx) if idx.isValid() else self.tr("Plugin Info")
        self.ui.groupBox.setTitle(title)

    def onViewDoubleClicked(self, idx: QModelIndex):
        name = self.model().data(idx)
        if name:
            self.doubleClicked.emit(name)

    def copy(self, indexes: List[QModelIndex]):
        if indexes:
            QApplication.clipboard().setMimeData(self.ui.infoView.model().mimeData(indexes))

    def addInfoViewActions(self):
        a = QAction(self.tr("Copy"), self.ui.infoView)
        a.setShortcut(QKeySequence.Copy)
        a.setShortcutContext(Qt.WidgetShortcut)
        a.setData(True)
        a.triggered.connect(lambda: self.copy(self.ui.infoView.selectedIndexes()))
        self.ui.infoView.addAction(a)

        a = QAction(self.tr("Select All"), self.ui.infoView)
        a.setShortcut(QKeySequence.SelectAll)
        a.setShortcutContext(Qt.WidgetShortcut)
        a.setData(True)
        a.triggered.connect(lambda: self.copy(self.ui.infoView.selectAll()))
        self.ui.infoView.addAction(a)

    def showContextMenu(self, pos: QPoint):
        menu = QMenu()
        menu.addActions(self.ui.infoView.actions())
        menu.exec(self.mapToGlobal(pos))
