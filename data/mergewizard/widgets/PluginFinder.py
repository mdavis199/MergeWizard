import re
from PyQt5.QtWidgets import QCompleter, QWidget
from mergewizard.widgets.TextStatusEdit import TextStatusEdit


class PluginFinder(QWidget):
    """ Provides the connections between a TextStatusEdit
    and a QCompleter

    This class defines how user-entered text can be cleaned up
    so that it might match a plugin name """

    def __init__(self, completer: QCompleter, widget: TextStatusEdit):
        super().__init__()
        self._completer = completer
        self._widget = widget
        self._experimental = True

    def setRowForLine(self, line: int, text: str):
        self._widget.setLineData(line, self._matchingRow(text.strip()))

    def fixupText(self, line: int, text: str):
        # TODO: I think we can take this part out; I don't
        # see how this method could be called if the unchanged
        # text already matches
        """
        row = self._matchingRow(text)
        if row >= 0:
            self._widget.setLineData(line, row)
            return
        """
        oldtext = text
        text = text.replace('"', "")

        # Instead of a name, maybe a path was given

        text = text.replace("\\", "/")
        idx = text.rfind("/") + 1
        if idx > 0 and idx < len(text):
            text = text[idx:]

        extensions = [".esp", ".esl", ".esm"]  # Are there other extensions?
        for ext in extensions:
            idx = text.rfind(ext)
            if idx >= 0:
                text = text[: idx + 4]
                break

        text = text.strip()
        if text != oldtext:
            if self._tryFixup(line, text):
                return

        if not self._experimental:
            if oldtext != text:
                self._widget.fixUpLine(line, text, -1)
            return

        # maybe illegal characters are separting the name
        # from extraneous info.  Try splitting it in sections.
        # We do not want to get carried away so just try 2 sections
        # on either end.

        # This can be problem.
        # What if the text is:   | mod name | plugin name |
        # If modname has the same name as some other plugin
        # it could pick up the wrong match.

        sections = re.split("[<>:|*?]+", text)
        count = len(sections)
        if count == 0 or oldtext == sections[0]:
            self._widget.fixUpLine(line, text, -1)
            return

        for i in range(0, count):
            if self._tryFixup(line, sections[i].strip()):
                return
            if i >= 1:
                break

        for i in range(count - 1, 1, -1):
            if self._tryFixup(line, sections[i].strip()):
                return
            if i <= count - 2:
                break

        self._widget.fixUpLine(line, text, -1)

    def _tryFixup(self, line: int, text: str):
        row = self._matchingRow(text)
        if row >= 0:
            self._widget.fixUpLine(line, text, row)
            return True
        return False

    def _matchingRow(self, text: str):
        """ Returns row that matches the given text.
        -1 is returned if no match is found. """
        if not text:
            return -1
        if text != self._completer.completionPrefix():
            self._completer.setCompletionPrefix(text)
        if not self._completer.setCurrentRow(0):
            return -1
        if not text == self._completer.currentCompletion():
            return -1
        return self._completer.completionModel().mapToSource(self._completer.currentIndex()).row()
