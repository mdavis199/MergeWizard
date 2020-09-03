# -*- coding: utf-8 -*-
from enum import IntEnum
from PyQt5.QtCore import pyqtSlot, pyqtSignal, qRound, Qt, QSize, QPoint, QRect, QMimeData
from PyQt5.QtGui import (
    QIcon,
    QKeySequence,
    QPaintEvent,
    QPainter,
    QResizeEvent,
    QTextBlockUserData,
    QTextCursor,
    QTextFormat,
)
from PyQt5.QtWidgets import QWidget, QShortcut, QPlainTextEdit, QTextEdit

MARK = u"\u2326"
NOMARK = ""


class TextStatusEdit(QPlainTextEdit):
    """ Adds line status indicator to text edit widget

    Each text block keeps track of which model row it matched with
    so that the number of times it has to lookup a match is minimized.

    A user of this class typically connects to the "lineChanged"
    signal to receive notifications every time a non-empty line changes.
    The user would check some underlying data model and if the line
    is valid, the user would call the 'setLineData' method to store
    the model row that the line is associated with.

    A user also connects to the 'statusChanged' signal to receive
    notifications when the validity of the entire document has
    changed.  A document is valid if it has at least one non-blank
    line and no lines have errors.   The user typically uses this
    signal to enable/disable a button that can process the document
    contents.

    A user connects to the 'fixupText' signal to receive notifications
    that a line has an error and this class would like to know if you
    can clean up the text and validate it. If the user was able to
    massage the text, the user calls the 'fixUpLine' method with the
    new text value and row.

    Note: The 'lineChange' signal is emitted as the document changes
    (by keyboard or pasting text).  The 'fixupText' signal is emitted
    in response to the 'onFixupTextAction' in a context menu or shortcut.
    """

    # signals the row number and text of a line that changed
    lineChanged = pyqtSignal(int, str)

    # signals that the document changed and is or is not valid
    statusChanged = pyqtSignal(bool)

    # signals a request to fixup an invalid line
    fixupText = pyqtSignal(int, str)

    class _State(IntEnum):
        Error = 0
        Blank = 1
        Fixup = 2
        Valid = 3

    class _UserData(QTextBlockUserData):
        def __init__(self, row: int = -1):
            super().__init__()
            self.row = row

    class _StatusArea(QWidget):
        """ Provides the status area to the left of the text edit """

        def __init__(self, parent):
            super().__init__(parent)

        def sizeHint(self):
            return QSize(self.parentWidget().statusAreaWidth(), 0)

        def paintEvent(self, event):
            self.parentWidget().statusAreaPaintEvent(event)

    def __init__(self, parent):
        super().__init__(parent)
        self._statusArea = self._StatusArea(self)
        self._hasValidContent = False
        self._hightlightCurrentLine = False
        self.setLineWrapMode(self.NoWrap)
        self._updateStatusAreaWidth()
        self.setContextMenuPolicy(Qt.CustomContextMenu)

        # signals
        self.updateRequest.connect(self._updateStatusArea)
        self.blockCountChanged.connect(self._updateStatusAreaWidth)
        self.document().contentsChange.connect(self._contentsChanged)

        QShortcut(Qt.CTRL + Qt.Key_F, self, self.onFixupTextAction)

    # ---- Methods related to highlighting current line

    def highlightCurrentLine(self):
        highlightColor = self.palette().alternateBase()
        selection = QTextEdit.ExtraSelection()
        selection.format.setBackground(highlightColor)
        selection.format.setProperty(QTextFormat.FullWidthSelection, True)
        selection.cursor = self.textCursor()
        selection.cursor.clearSelection()
        self.setExtraSelections([selection])

    def enableHighlightCurrentLine(self, enable: bool):
        self._highlightCurrentLine = enable
        if enable:
            self.highlightCurrentLine()
            self.cursorPositionChanged.connect(self.highlightCurrentLine)
        else:
            self.cursorPositionChanged.disconnect(self.highlightCurrentLine)

    # --- Methods related to painting the widgets

    def statusAreaWidth(self):
        return 3 + self.fontMetrics().horizontalAdvance(MARK)

    def _updateStatusAreaWidth(self):
        self.setViewportMargins(self.statusAreaWidth(), 0, 0, 0)

    def _updateStatusArea(self, rect: QRect, dy: int):
        if dy:
            self._statusArea.scroll(0, dy)
        else:
            self._statusArea.update(0, rect.y(), self._statusArea.width(), rect.height())
        if rect.contains(self.viewport().rect()):
            self._updateStatusAreaWidth()

    def resizeEvent(self, event: QResizeEvent):
        super().resizeEvent(event)
        cr = self.contentsRect()
        self._statusArea.setGeometry(QRect(cr.left(), cr.top(), self.statusAreaWidth(), cr.height()))

    def statusAreaPaintEvent(self, event: QPaintEvent):
        painter = QPainter(self._statusArea)
        painter.fillRect(event.rect(), Qt.lightGray)

        block = self.firstVisibleBlock()
        top = qRound(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())
        bottom = top + qRound(self.blockBoundingRect(block).height())

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                painter.setPen(Qt.red)
                painter.drawText(
                    0,
                    top,
                    self._statusArea.width(),
                    self.fontMetrics().height(),
                    Qt.AlignRight,
                    MARK if block.userState() == self._State.Error else NOMARK,
                )
            block = block.next()
            top = bottom
            bottom = top + qRound(self.blockBoundingRect(block).height())

    # --- Methods related to text entry

    def insertFromMimeData(self, source: QMimeData):
        lines = []
        for line in source.text().splitlines():
            line = line.strip()
            if line:
                lines.append(line)
        data = QMimeData()
        data.setText("\n".join(lines))
        super().insertFromMimeData(data)

    def _contentsChanged(self, pos: int, removed: int, added: int):
        block = self.document().findBlock(pos)
        if not block.isValid():
            return
        lastBlock = self.document().findBlock(pos + added + (1 if removed > 0 else 0))
        if not lastBlock.isValid():
            lastBlock = self.document().lastBlock()
        while block.isValid() and block.blockNumber() <= lastBlock.blockNumber():
            if block.length() <= 1 or not block.text().strip():
                block.setUserState(self._State.Blank)
            elif block.userState() == self._State.Fixup:
                block.setUserState(self._State.Valid)
            else:
                block.setUserState(self._State.Error)
                self.lineChanged.emit(block.blockNumber(), block.text())
            block = block.next()
        self.checkStatus()

    def checkStatus(self):
        hasContent = False
        hasError = False
        it = self.document().begin()
        while it != self.document().end():
            if it.isValid():
                if it.userState() == self._State.Error:
                    hasError = True
                    break
                if it.userState() == self._State.Valid:
                    hasContent = True
            it = it.next()
        hasContent = hasContent and not hasError
        if self._hasValidContent != hasContent:
            self._hasValidContent = hasContent
            self.statusChanged.emit(self._hasValidContent)

    def isLineValid(self, row: int):
        block = self.document().findBlockByLineNumber(row)
        return block.isValid() and block.userState() == self._State.Valid

    def isLineInvalid(self, row: int):
        block = self.document().findBlockByLineNumber(row)
        return block.isValid() and block.userState() == self._State.Error

    def hasValidContent(self):
        """ True if there are no errors and at least one non-blank line """
        return self._hasValidContent

    def data(self):
        """ Returns a list of the the stored data for all valid rows.
        The data we're storing are the model rows that matched the text
        in the edit box. """

        result = []
        it = self.document().begin()
        while it != self.document().end():
            if (
                it.isValid()
                and it.userState() != self._State.Error
                and it.userState() != self._State.Blank
                and it.userData() is not None
            ):
                result.append(it.userData().row)
            it = it.next()
        return result

    def setLineData(self, line: int, data: int):
        """ The receiver of the 'lineChanged' signal should invoke this method
        to set the model row that the line matches """

        block = self.document().findBlockByLineNumber(line)
        if block.isValid():
            if block.userData() is None:
                block.setUserData(self._UserData(data))
            else:
                block.userData().row = data
            block.setUserState(self._State.Error if data < 0 else self._State.Valid)

    def fixUpLine(self, line: int, newText: str, data: int):
        """ The receiver of the 'fixupText' signal should invoke this method
        to replace the line with the cleaned text and the model's
        matching row """

        block = self.document().findBlockByLineNumber(line)
        if block.isValid():
            if block.userData() is None:
                block.setUserData(self._UserData(data))
            else:
                block.userData().row = data

            text = newText.strip()
            if not text:
                block.setUserState(self._State.Blank)
            elif data < 0:
                block.setUserState(self._State.Error)
            else:
                block.setUserState(self._State.Fixup)

            cursor = QTextCursor(block)
            cursor.beginEditBlock()
            cursor.movePosition(QTextCursor.StartOfLine)
            cursor.select(QTextCursor.LineUnderCursor)
            cursor.removeSelectedText()
            cursor.insertText(text)
            cursor.endEditBlock()

    def resetData(self):
        """ Invoke this method to emit 'lineChanged' signals for all non-empty
        lines.

        This is used when the underlying data model changed and the
        row numbers are no longer valid"""

        it = self.document().begin()
        while it != self.document().end():
            if it.userState() != self._State.Blank:
                self.lineChanged.emit(it.blockNumber(), it.text())
            it = it.next()

    @pyqtSlot()
    def onFixupTextAction(self):
        """ Initiate fixupText signals on all lines with errors """
        it = self.document().begin()
        while it != self.document().end():
            if it.userState() == self._State.Error:
                self.fixupText.emit(it.blockNumber(), it.text())
            it = it.next()

    # ---- Methods related to Context Menu

    def enableContextMenu(self, enable: bool = True):
        if enable:
            self.customContextMenuRequested.connect(self.showContextMenu)
        else:
            self.customContextMenuRequested.disconnect(self)

    def showContextMenu(self, pos: QPoint):
        menu = self.createStandardContextMenu(pos)
        menu.exec(self.mapToGlobal(pos))

    def createStandardContextMenu(self, pos: QPoint):
        menu = super().createStandardContextMenu(pos)
        menu.addSeparator()
        fixupAction = menu.addAction(
            QIcon(), self.tr("Fixup Text"), self.onFixupTextAction, QKeySequence(Qt.CTRL + Qt.Key_F),
        )
        fixupAction.setDisabled(not self.document().toPlainText().strip() or self.hasValidContent())
        return menu
