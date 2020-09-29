from PyQt5.QtCore import Qt, QObject, QModelIndex, QAbstractItemModel, QSize
from PyQt5.QtWidgets import QWidget, QComboBox, QStyleOptionViewItem, QStyledItemDelegate


class ComboBoxDelegate(QStyledItemDelegate):
    def __init__(self, parent: QObject = None):
        super().__init__(parent)
        self._maxChars = 0

    def createEditor(
        self, parent: QWidget, option: QStyleOptionViewItem, idx: QModelIndex,
    ):
        values = idx.model().data(idx, Qt.UserRole + 10)  # TODO:Need to change this to not be hard-coded.
        if values is None:
            return super().createEditor(parent, option, idx)
        cb = QComboBox(parent)
        cb.addItems(values)
        currentText = idx.model().data(idx, Qt.DisplayRole)
        editorIdx = cb.findText(currentText)
        cb.setCurrentIndex(editorIdx)
        return cb

    def setEditorData(self, editor, idx: QModelIndex):
        if not isinstance(editor, QComboBox):
            return super().setEditorData(editor, idx)
        currentText = idx.data(Qt.EditRole)
        editorIdx = editor.findText(currentText)
        if editorIdx >= 0:
            editor.setCurrentIndex(editorIdx)

    def setModelData(
        self, editor, model: QAbstractItemModel, idx: QModelIndex,
    ):
        if not isinstance(editor, QComboBox):
            return super().setModelData(editor, model, idx)
        model.setData(idx, editor.currentText(), Qt.EditRole)

    def sizeHint(self, option: QStyleOptionViewItem, idx: QModelIndex):
        if self._maxChars == 0:
            return super().sizeHint(option, idx)
        textWidth = option.fontMetrics.width("W" * self._maxChars)
        textHeight = option.fontMetrics.height()
        return QSize(textWidth, textHeight)

