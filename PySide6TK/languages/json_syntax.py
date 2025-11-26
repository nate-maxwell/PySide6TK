from dataclasses import dataclass

from PySide6 import QtGui

from PySide6TK.text import HighlightRule
from PySide6TK.text import color_format


@dataclass
class JsonSyntaxColors(object):
    numerical = color_format('orange', 'bold')
    keys = color_format('white', 'bold')
    values = color_format('lightgreen')


_color_scheme = JsonSyntaxColors()


class JsonHighlighter(QtGui.QSyntaxHighlighter):
    def __init__(self, parent=None) -> None:
        """Initialize rules with expression pattern and text format."""
        super(JsonHighlighter, self).__init__(parent)

        self.rules = []

        numeric_pattern = r'([-0-9.]+)(?!([^"]*"\s*:))'
        self.rules.append(
            HighlightRule(numeric_pattern, _color_scheme.numerical, group=1)
        )
        key_pattern = r'("([^"]*)")\s*:'
        self.rules.append(
            HighlightRule(key_pattern, _color_scheme.keys, group=1)
        )
        value_pattern = r':\s*("([^"]*)")'
        self.rules.append(
            HighlightRule(value_pattern, _color_scheme.values, group=1)
        )

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
