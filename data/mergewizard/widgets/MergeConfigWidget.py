from PyQt5.QtCore import QItemSelectionModel, QModelIndex, QObject, QEvent
from PyQt5.QtWidgets import QWidget, QHeaderView, QTreeView

from mergewizard.domain.merge.MergeFile import MergeFile, PluginDesc
from mergewizard.models.MergeFileModel import MergeFileModel, OptionRow as Option

from mergewizard.widgets.Splitter import Splitter
from mergewizard.domain.MOLog import moWarn
from .ui.MergeConfigWidget import Ui_MergeConfigWidget

# REFER: https://stackoverflow.com/questions/20064975/how-to-catch-mouse-over-event-of-qtablewidget-item-in-pyqt


class DualEventFilter(QObject):
    def eventFilter(self, obj: QObject, event: QEvent) -> bool:
        pass


class MergeConfigWidget(QWidget):
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self.ui = Ui_MergeConfigWidget
        self.ui.setupUi(self)

        Splitter.decorate(self.ui.splitter)
        self.ui.zMergeView.setModel(MergeFileModel())
        self.ui.zMergeView.header().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.ui.zMergeView.header().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.ui.zMergeView.header().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.ui.zMergeView.header().setVisible(False)
        self.ui.originalView.setModel(MergeFileModel())
        self.ui.originalView.header().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.ui.originalView.header().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.ui.originalView.header().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.ui.originalView.header().setVisible(False)
        self.ui.originalBox.setVisible(False)

    def setMergeFile(self, mf: MergeFile):
        self.ui.zMergeView.model().setMergeFile(mf)

    def setOriginalMergeFile(self, mf: MergeFile):
        self.ui.originalView.model().setMergeFile(mf)

    def showOriginal(self, show):
        self.ui.originalBox.setVisible(show)
