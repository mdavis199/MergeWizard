from typing import List
from PyQt5.QtCore import pyqtSignal, QModelIndex, QPoint, Qt, qInfo
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import QWidget, QApplication, QMenu, QAction
from mergewizard.models.PluginModel import PluginModel, Column as PluginColumn
from mergewizard.models.MergeInfoModel import MergeInfoModel, Column
from .ui.MergeInfoWidget import Ui_MergeInfoWidget


class MergeInfoWidget(QWidget):
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self.ui = Ui_MergeInfoWidget()
        self.ui.setupUi(self)
        self.ui.infoView.setModel(MergeInfoModel())

    def setPluginModel(self, model: PluginModel):
        self.model().setSourceModel(model)

    def model(self):
        return self.ui.infoView.model()

    def infoModel(self):
        return self.model()

    def rootIndex(self):
        return self.ui.infoView.rootIndex()

    def setRootIndex(self, idx: QModelIndex = QModelIndex()):
        infoIdx = self.infoModel().index(idx.row(), PluginColumn.PluginName)
        self.ui.infoView.setRootIndex(infoIdx)
        title = self.infoModel().data(infoIdx) if idx.isValid() else self.tr("Merge Info")
        self.ui.groupBox.setTitle(title)
