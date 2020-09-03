from PyQt5.QtCore import Qt, QObject, QModelIndex, QLocale, QAbstractItemModel, QSize
from PyQt5.QtWidgets import QWidget, QSpinBox, QStyleOptionViewItem, QStyledItemDelegate


class PositionDelegate(QStyledItemDelegate):
    def __init__(self, parent: QObject = None):
        super().__init__(parent)

    def createEditor(
        self, parent: QWidget, option: QStyleOptionViewItem, idx: QModelIndex,
    ):
        editor = QSpinBox(parent)
        editor.setframe(False)
        editor.setMinimum(1)
        editor.setMaximumWidth(idx.model().rowCount())
        editor.setAlignment(Qt.AlignRight)
        return editor

    def displayText(self, value, locale: QLocale):
        return super().displayText(value + 1, locale)

    def setEditorData(self, editor: QSpinBox, idx: QModelIndex):
        value = idx.model().data(idx, Qt.EditRole) + 1
        editor.setValue(value)

    def setModelData(
        self, editor: QSpinBox, model: QAbstractItemModel, idx: QModelIndex,
    ):
        editor.interpretText()
        currentValue = idx.model().data(idx, Qt.EditRole)
        newValue = editor.value() - 1
        if newValue == currentValue:
            return
        if newValue > currentValue:
            newValue = newValue + 1
        model.setData(idx, newValue, Qt.EditRole)

    def updateEditorGeometry(
        self, editor: QSpinBox, option: QStyleOptionViewItem, idx: QModelIndex,
    ):
        editor.setGeometry(option.rect)

    def sizeHint(self, option: QStyleOptionViewItem, idx: QModelIndex):
        textWidth = option.fontMetrics.width("999")
        textHeight = option.fontMetrics.height()
        return QSize(textWidth + 3, textHeight)  # allow for the slider
