from PySide6 import QtCore
from PySide6 import QtGui


class HighlightRule(object):
    def __init__(
            self,
            pattern: str,
            char_format: QtGui.QTextCharFormat,
            group: int = 0
    ) -> None:
        """
        Args:
            pattern (str): A QRegularExpression pattern string.
            char_format (QtGui.QTextCharFormat): The text format to apply to
                matches.
            group (int): Which capture group to highlight (0 = whole match).
        """
        self.pattern = QtCore.QRegularExpression(pattern)
        self.format = char_format
        self.group = group


class JsonHighlighter(QtGui.QSyntaxHighlighter):
    def __init__(self, parent=None) -> None:
        """Initialize rules with expression pattern and text format."""
        super(JsonHighlighter, self).__init__(parent)

        self.rules = []

        num_fmt = QtGui.QTextCharFormat()
        num_fmt.setForeground(QtGui.QColor('blue'))
        num_fmt.setFontWeight(QtGui.QFont.Weight.Bold)
        numeric_pattern = r'([-0-9.]+)(?!([^"]*"\s*:))'
        self.rules.append(HighlightRule(numeric_pattern, num_fmt, group=1))

        key_fmt = QtGui.QTextCharFormat()
        key_fmt.setFontWeight(QtGui.QFont.Weight.Bold)
        key_pattern = r'("([^"]*)")\s*:'
        self.rules.append(HighlightRule(key_pattern, key_fmt, group=1))

        val_fmt = QtGui.QTextCharFormat()
        val_fmt.setForeground(QtGui.QColor('darkgreen'))
        value_pattern = r':\s*("([^"]*)")'
        self.rules.append(HighlightRule(value_pattern, val_fmt, group=1))

    def highlightBlock(self, text: str) -> None:
        """
        Implement the text block highlighting using QRegularExpression.

        Args:
            text: The text to perform a keyword highlighting check on.
        """
        for rule in self.rules:
            it = rule.pattern.globalMatch(text)
            while it.hasNext():
                m = it.next()
                start = m.capturedStart(rule.group)
                length = m.capturedLength(rule.group)
                if start >= 0 and length > 0:
                    self.setFormat(start, length, rule.format)
