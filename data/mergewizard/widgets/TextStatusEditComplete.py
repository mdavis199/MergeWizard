# -*- coding: utf-8 -*-
from PyQt5.QtCore import Qt, QAbstractItemModel, QPoint
from PyQt5.QtGui import QTextCursor, QKeyEvent, QKeySequence, QIcon, QMouseEvent
from PyQt5.QtWidgets import QCompleter, QWidget, QShortcut

from mergewizard.widgets.TextStatusEdit import TextStatusEdit
from mergewizard.widgets.PluginFinder import PluginFinder


class TextStatusEditComplete(TextStatusEdit):
    """ Adds Completion functions to the base class

    This class extends 'TextStatusEdit' by:

    1.  providing a QCompleter to validate lines for the
        'fixupText' and 'lineChanged' signals
    2.  providing a popup for suggested completions as
        the user is typing
    3.  auto-completing the line when the user selects
        a suggestion.

    The task of auto completion and providing suggestions
    is provided directly by this class.

    The task validating and cleaning up text is provided by
    the PluginFinder.
    """

    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self._dataModel = None
        self._monitorDbChanges = False
        self._enableAutoCompletion = False
        self._completedAndSelected = False
        self._completer = QCompleter(self)

        self._completer.setWidget(self)
        self._completer.setWrapAround(False)
        self._completer.setCompletionMode(QCompleter.PopupCompletion)
        self._completer.setCaseSensitivity(Qt.CaseInsensitive)
        self._completer.setFilterMode(Qt.MatchStartsWith)
        self._completer.setModelSorting(QCompleter.CaseInsensitivelySortedModel)
        self._completer.activated.connect(self.replaceLine)

        self._pluginFinder = PluginFinder(self._completer, self)
        self.fixupText.connect(self._pluginFinder.fixupText)
        self.lineChanged.connect(self._pluginFinder.setRowForLine)

        QShortcut(Qt.CTRL + Qt.Key_E, self, self.toggleAutoCompletion)
        QShortcut(Qt.CTRL + Qt.Key_T, self, self.suggestCompletions)

    # --- Methods related to the completer's underlying data model

    def setModel(self, model: QAbstractItemModel):
        self._completer.setModel(model)

    def _updateModelSignals(self):
        """ We do not need to check for column changes due to
        the way our PluginModel is structured. """

        if self._dataModel is not None:
            self._dataModel.rowsMoved.disconnect(self.resetData)
            self._dataModel.rowsInserted.disconnect(self.resetData)
            self._dataModel.rowsRemoved.disconnect(self.resetData)
            self._dataModel.modelReset.disconnect(self.resetData)
            self._dataModel.dataChanged.disconnect(self.resetData)
            self._dataModel.layoutChanged.disconnect(self.resetData)

        if self._monitorDbChanges:
            self._dataModel = self._completer.model()
            if self._dataModel is not None:
                self._dataModel.rowsMoved.connect(self.resetData)
                self._dataModel.rowsInserted.connect(self.resetData)
                self._dataModel.rowsRemoved.connect(self.resetData)
                self._dataModel.modelReset.connect(self.resetData)
                self._dataModel.dataChanged.connect(self.resetData)
                self._dataModel.layoutChanged.connect(self.resetData)
        else:
            self._dataModel = None

    def monitorDbChanges(self, enable: bool):
        """ Enable invalidating line status when
        the data model changes.

        Depending on the underlying data model, it may
        be unnecessary to monitor these changes, or, a
        higher level class can monitor specific signals
        more efficiently.  So, this is not enabled
        by default.  """

        if self._monitorDbChanges == enable:
            return

        self._monitorDbChanges = enable
        if enable:
            self._dataModel = self._completer.model()
            self._completer.completionModel().sourceModelChanged.connect(self._updateModelSignals)
        else:
            self._completer.completionModel().sourceModelChanged.disconnect(self._updateModelSignals)
        self._updateModelSignals()

    # ---- Methods related to line completion

    def completer(self):
        return self._completer

    def enableAutoCompletion(self, enable: bool):
        self._enableAutoCompletion = enable

    def toggleAutoCompletion(self):
        self.enableAutoCompletion(not self._enableAutoCompletion)

    def _textUnderCursor(self):
        tc = self.textCursor()
        if tc.positionInBlock() == 0 and len(tc.block().text()) > 1:
            tc.movePosition(QTextCursor.NextCharacter)
        tc.movePosition(QTextCursor.StartOfLine, QTextCursor.KeepAnchor)
        return tc.selectedText().lstrip()

    def suggestCompletions(self):
        if self.isLineInvalid(self.textCursor().blockNumber()):
            self._suggestCompletionsForText(self._textUnderCursor())

    def _suggestCompletionsForText(self, prefix: str):
        if not prefix:
            return
        if prefix != self._completer.completionPrefix():
            self._completer.setCompletionPrefix(prefix)
            self._completer.popup().setCurrentIndex(self._completer.completionModel().index(0, 0))
        if self._completer.completionCount() == 1:
            self._insertSuggestion(self._completer.currentCompletion())
        else:
            rect = self.cursorRect()
            rect.moveRight(self.statusAreaWidth())
            rect.setWidth(
                self._completer.popup().sizeHintForColumn(self._completer.completionColumn())
                + self._completer.popup().verticalScrollBar().sizeHint().width()
            )
            self._completer.complete(rect)

    def _insertSuggestion(self, text: str):
        """ Only one suggestion matched, prefill line """

        cursor = self.textCursor()
        # handle when cursor is in middle of line
        if not cursor.atBlockEnd():
            cursor.beginEditBlock()
            cursor.select(QTextCursor.LineUnderCursor)
            cursor.removeSelectedText()
            cursor.insertText(text)
            cursor.movePosition(QTextCursor.StartOfLine)
            cursor.movePosition(QTextCursor.EndOfLine, QTextCursor.KeepAnchor)
            self._completedAndSelected = True
            self.setTextCursor(cursor)
            cursor.endEditBlock()
            return

        # handle when cursor at end of line
        cursor.beginEditBlock()
        numCharsToComplete = len(text) - len(self._completer.completionPrefix())
        insertionPosition = cursor.position()
        cursor.movePosition(QTextCursor.EndOfLine, QTextCursor.KeepAnchor)
        cursor.removeSelectedText()
        cursor.insertText(text[-numCharsToComplete:])
        cursor.setPosition(insertionPosition)
        cursor.movePosition(QTextCursor.EndOfLine, QTextCursor.KeepAnchor)
        self._completedAndSelected = True
        self.setTextCursor(cursor)
        cursor.endEditBlock()

    def keyPressEvent(self, event: QKeyEvent):
        if self._completedAndSelected and self.handledCompletedAndSelected(event):
            return

        self._completedAndSelected = False
        if self._completer.popup().isVisible():
            ignoredKeys = [
                Qt.Key_Up,
                Qt.Key_Down,
                Qt.Key_Enter,
                Qt.Key_Return,
                Qt.Key_Tab,
                Qt.Key_Escape,
            ]
            if event.key() in ignoredKeys:
                event.ignore()
                return
            self._completer.popup().hide()

        super().keyPressEvent(event)
        if not self._enableAutoCompletion:
            return

        ctrlOrShift = (
            event.modifiers() & Qt.ShiftModifier == Qt.ShiftModifier
            or event.modifiers() & Qt.ControlModifier == Qt.ControlModifier
        )

        if ctrlOrShift and not event.text():
            return

        if self.textCursor().atBlockEnd():
            self.suggestCompletions()

    def mousePressEvent(self, event: QMouseEvent):
        if self._completedAndSelected:
            self._completedAndSelected = False
            self.document().undo()
        super().mousePressEvent(event)

    def handledCompletedAndSelected(self, event: QKeyEvent):
        """ The line is prefilled when only one completion matches. The user
        can accept the suggestion by pressing 'Enter'. The user can reject
        the suggestion by pressing 'Esc' or by continuing to type. """

        self._completedAndSelected = False
        cursor = self.textCursor()
        acceptKeys = [Qt.Key_Enter, Qt.Key_Return, Qt.Key_Tab]
        if event.key() in acceptKeys:
            self.replaceLine(self._completer.currentCompletion())
        elif event.key() == Qt.Key_Escape:
            self.document().undo()
        else:
            self.document().undo()
            return False

        self.setTextCursor(cursor)
        event.accept()
        return True

    def replaceLine(self, text: str):
        cursor = self.textCursor()
        cursor.beginEditBlock()
        cursor.select(QTextCursor.LineUnderCursor)
        cursor.removeSelectedText()
        cursor.insertText(text)
        cursor.movePosition(QTextCursor.EndOfLine)
        self.setTextCursor(cursor)
        cursor.endEditBlock()

    # ---- Methods related to Context Menu

    def createStandardContextMenu(self, pos: QPoint):
        menu = super().createStandardContextMenu(pos)
        menu.addSeparator()
        autoCompletionAction = menu.addAction(
            QIcon(), self.tr("Enable Auto Complete"), self.toggleAutoCompletion, QKeySequence(Qt.CTRL + Qt.Key_E),
        )
        autoCompletionAction.setCheckable(True)
        autoCompletionAction.setChecked(self._enableAutoCompletion)

        completionAction = menu.addAction(
            QIcon(), self.tr("Suggest Completions"), self.suggestCompletions, QKeySequence(Qt.CTRL + Qt.Key_T),
        )
        completionAction.setEnabled(self.isLineInvalid(self.textCursor().blockNumber()))
        return menu
