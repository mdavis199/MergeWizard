from PyQt5.QtCore import pyqtSignal, Qt, QRect
from PyQt5.QtGui import QPainter, QMouseEvent
from PyQt5.QtWidgets import QHeaderView, QWidget, QStyleOptionButton, QStyle


class CheckableHeader(QHeaderView):
    clicked = pyqtSignal()

    def __init__(self, orientation: Qt.Orientation = Qt.Horizontal, parent: QWidget = None):
        super().__init__(orientation, parent)
        self.checkState: Qt.CheckState = Qt.Unchecked
        self.rect = QRect(3, 1, 16, 16)

    def paintSection(self, painter: QPainter, rect: QRect, logicalIndex: int) -> None:
        painter.save()
        super().paintSection(painter, rect, logicalIndex)
        painter.restore()
        if logicalIndex == 0:
            option = QStyleOptionButton()
            option.rect = self.rect
            option.state = QStyle.State_Active
            if self.isEnabled():
                option.state |= QStyle.State_Enabled
            option.state |= self.checkStateToStyle()
            self.style().drawControl(QStyle.CE_CheckBox, option, painter)

    def mousePressEvent(self, event: QMouseEvent):
        if self.rect.contains(event.x(), event.y()):
            self.clicked.emit()
        super().mousePressEvent(event)

    def setCheckState(self, state: Qt.CheckState):
        self.checkState = state
        self.update()

    def checkStateToStyle(self):
        if self.checkState == Qt.Checked:
            return QStyle.State_On
        if self.checkState == Qt.Unchecked:
            return QStyle.State_Off
        return QStyle.State_NoChange
