from typing import Union, List
from PyQt5.QtCore import QObject, QEvent, pyqtSignal
from PyQt5.QtWidgets import QWidget


class VisibilityWatcher(QObject):
    # Emits true if any object is visible, false otherwise
    visibilityChanged = pyqtSignal(bool)

    def __init__(self, parent: QObject = None):
        super().__init__(parent)
        self._watchedWidgets: List[QWidget] = []
        self._visible = False

    def add(self, widget: Union[QWidget, List[QWidget]]):
        if isinstance(widget, list):
            for w in widget:
                if w not in self._watchedWidgets:
                    self._watchedWidgets.append(w)
                    w.installEventFilter(self)
        elif widget not in self._watchedWidgets:
            self._watchedWidgets.append(widget)
            w.installEventFilter(self)
        self.checkAllWidgets()

    def remove(self, widget: Union[QWidget, List[QWidget]]):
        if isinstance(widget, list):
            for w in widget:
                if w in self._watchedWidgets:
                    self._watchedWidgets.remove(w)
                    w.removeEventFilter(self)
        elif widget in self._watchedWidgets:
            self._watchedWidgets.remove(widget)
            widget.removeEventFilter(self)
        self.checkAllWidgets()

    def eventFilter(self, widget: QObject, event: QEvent):
        if event.type() == QEvent.ShowToParent and not self._visible:
            self._visible = True
            self.visibilityChanged.emit(True)
        elif event.type() == QEvent.HideToParent and self._visible:
            self.checkAllWidgets()
        return super().eventFilter(widget, event)

    def checkAllWidgets(self):
        anyVisible = False
        for widget in self._watchedWidgets:
            anyVisible = anyVisible or widget.isVisibleTo(widget.parent())
        if self._visible != anyVisible:
            self._visible = anyVisible
            self.visibilityChanged.emit(anyVisible)

