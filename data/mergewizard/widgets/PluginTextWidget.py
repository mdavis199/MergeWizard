from PyQt5.QtWidgets import QWidget

from mergewizard.models.PluginModel import PluginModel
from .ui.PluginTextWidget import Ui_PluginTextWidget


class PluginTextWidget(QWidget):
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self.ui = Ui_PluginTextWidget()
        self.ui.setupUi(self)

        self.ui.edit.enableHighlightCurrentLine(True)
        self.ui.edit.enableAutoCompletion(True)
        self.ui.edit.enableContextMenu(True)
        self.ui.button.setEnabled(False)
        self.ui.button.clicked.connect(self.onButtonClicked)
        self.ui.edit.statusChanged.connect(self.ui.button.setEnabled)

    def setPluginModel(self, model: PluginModel):
        self.ui.edit.completer().setModel(model)

    def clear(self):
        self.ui.edit.clear()

    def onButtonClicked(self):
        model = self.ui.edit.completer().model()
        model.selectPlugins([model.index(row, 0) for row in self.ui.edit.data()], True)
        self.ui.edit.clear()

