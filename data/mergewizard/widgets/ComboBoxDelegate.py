from PyQt5.QtCore import Qt, QObject, QModelIndex, QAbstractItemModel, qInfo
from PyQt5.QtWidgets import QWidget, QComboBox, QStyleOptionViewItem, QStyledItemDelegate


class ComboBoxDelegate(QStyledItemDelegate):
    def __init__(self, parent: QObject = None):
        super().__init__(parent)

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

    def setEditorData(self, editor: QComboBox, idx: QModelIndex):
        if not editor.count():
            super().setEditorData(editor, idx)
        currentText = idx.data(Qt.EditRole)
        editorIdx = editor.findText(currentText)
        if editorIdx >= 0:
            editor.setCurrentIndex(editorIdx)

    def setModelData(
        self, editor: QComboBox, model: QAbstractItemModel, idx: QModelIndex,
    ):
        if not editor.count():
            super().setModelData(editor, model, idx)
        model.setData(idx, editor.currentText(), Qt.EditRole)
