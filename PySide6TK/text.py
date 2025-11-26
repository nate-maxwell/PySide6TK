"""
# Qt Text Formatting

* Description:

    Library of text formatters / colorers / helpers.
"""


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
            pattern (str): A regex pattern string.
            char_format (QtGui.QTextCharFormat): The text format to apply to
                matches.
            group (int): Which capture group to highlight (0 = whole match).
        """
        self.pattern = QtCore.QRegularExpression(pattern)
        self.format = char_format
        self.group = group


def color_format(color: str, style: str = '') -> QtGui.QTextCharFormat:
    """Return a QTextCharFormat with the given attributes.

    Args:
        color: The string name for a QColor to use.
        style: 'italic' and/or 'bold'.
    Returns:
        QtGui.QTextCharFormat: The formatted text.
    """
    _color = QtGui.QColor()
    _color.setNamedColor(color)

    _format = QtGui.QTextCharFormat()
    _format.setForeground(_color)
    if 'bold' in style:
        _format.setFontWeight(QtGui.QFont.Weight.Bold)
    if 'italic' in style:
        _format.setFontItalic(True)

    return _format
