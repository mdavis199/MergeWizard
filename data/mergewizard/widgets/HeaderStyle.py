from PyQt5.QtCore import QRect, Qt, qInfo
from PyQt5.QtGui import QPainter
from PyQt5.QtWidgets import QWidget, QProxyStyle, QStyle, QStyleOption

# CRASHES IN PYQT


class HeaderStyle(QProxyStyle):
    ICON_WIDTH = 16
    ICON_HEIGHT = 16

    def drawControl(
        self, element: QStyle.ControlElement, option: QStyleOption, painter: QPainter, widget: QWidget = None
    ) -> None:

        super().drawControl(element, option, painter, widget)


"""
class HeaderStyle(QProxyStyle):
    ICON_WIDTH = 16
    ICON_HEIGHT = 16

    def drawControl(
        self, element: QStyle.ControlElement, option: QStyleOption, painter: QPainter, widget: QWidget = None
    ) -> None:

        if element == QStyle.CE_HeaderLabel:
            if option.icon and not option.text:
                pixmap = option.icon.pixmap(self.ICON_WIDTH, self.ICON_HEIGHT)
                if option.textAlignment == Qt.AlignCenter or option.textAlignment == Qt.AlignHCenter:
                    rect = QRect(
                        option.rect.left + self.ICON_WIDTH / 2,
                        option.rect.top + self.ICON_HEIGHT / 2,
                        self.ICON_WIDTH,
                        self.ICON_HEIGHT,
                    )
                    painter.drawPixmap(rect, pixmap)
                    return
                elif option.textAlignment == Qt.AlignRight:
                    rect = QRect(
                        option.rect.right - self.ICON_WIDTH,
                        option.rect.top + self.ICON_HEIGHT / 2,
                        self.ICON_WIDTH,
                        self.ICON_HEIGHT,
                    )
                    painter.drawPixmap(rect, pixmap)
                    return
                elif option.textAlignment == Qt.AlignLeft:
                    rect = QRect(
                        option.rect.left, option.rect.top + self.ICON_HEIGHT / 2, self.ICON_WIDTH, self.ICON_HEIGHT,
                    )
                    painter.drawPixmap(rect, pixmap)
                    return
        super().drawControl(element, option, painter, widget)


"""

