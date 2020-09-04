from PyQt5.QtCore import Qt, QSize
from PyQt5.QtWidgets import QWidget, QHeaderView

from mergewizard.models.PluginModel import PluginModel
from mergewizard.models.ActionModel import ActionModel
from mergewizard.models.LogModel import LogModel, LogFilterModel
from mergewizard.widgets.Splitter import Splitter
from mergewizard.widgets.CheckableHeader import CheckableHeader
from .ui.ActionWidget import Ui_ActionWidget


class ActionWidget(QWidget):
    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.ui = Ui_ActionWidget()
        self.ui.setupUi(self)
        Splitter.decorate(self.ui.splitter)

        logModel = LogModel()
        logFilterModel = LogFilterModel()
        logFilterModel.setSourceModel(logModel)
        self.ui.logView.setModel(logFilterModel)
        self.ui.logView.resizeColumnToContents(0)
        self.ui.logView.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)

        actionModel = ActionModel()
        actionModel.log.connect(logModel.log)
        self.ui.actionView.setModel(actionModel)

        actionHeader = CheckableHeader(parent=self)
        actionHeader.clicked.connect(actionModel.toggleAll)
        actionModel.headerDataChanged.connect(
            lambda: actionHeader.setCheckState(actionModel.headerData(0, Qt.Horizontal, Qt.CheckStateRole))
        )
        actionModel.headerDataChanged.connect(lambda: self.ui.applyButton.setEnabled(not actionModel.isNoneEnabled()))
        self.ui.actionView.setHorizontalHeader(actionHeader)
        actionHeader.setStretchLastSection(True)
        self.ui.actionView.resizeColumnToContents(0)

        self.setActionViewSize()  # set the view height to fit all the rows

        self.ui.applyButton.setEnabled(not actionModel.isNoneEnabled())
        self.ui.applyButton.clicked.connect(lambda x: self.applyActions())

    def setActionViewSize(self):
        h = self.ui.actionView.horizontalHeader().height() + 4
        for i in range(self.ui.actionView.model().rowCount()):
            h = h + self.ui.actionView.rowHeight(i)
        h = h + (self.ui.actionView.rowHeight(0) / 2)
        self.ui.actionView.setMinimumSize(QSize(0, h))

    def logModel(self):
        return self.ui.logView.model().sourceModel()

    def actionModel(self):
        self.logModel().clear()
        return self.ui.actionView.model()

    def showDebugMessages(self, show: bool):
        self.ui.logView.model().showDebugMessages(show)

    def setPluginModel(self, pluginModel: PluginModel):
        pluginModel.log.connect(self.logModel().log)
        self.actionModel().setPluginModel(pluginModel)
        pass

    def applyActions(self):
        self.ui.logView.model().sourceModel().clear()
        self.ui.actionView.model().applyActions()

    def createLogContextMenu(self):
        pass
