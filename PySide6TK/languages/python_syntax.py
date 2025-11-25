from PySide6 import QtGui
from PySide6 import QtCore


def _color_format(color: str, style: str = '') -> QtGui.QTextCharFormat:
    """
    Return a QTextCharFormat with the given attributes.

    Args:
        color(str): The string name for a QColor to use.
        style(str) 'italic' and/or 'bold'.
    Returns:
        QtGui.QTextCharFormat: The formatted text.
    """
    # TODO: Add brightness control for better color customization
    _color = QtGui.QColor()
    _color.setNamedColor(color)

    _format = QtGui.QTextCharFormat()
    _format.setForeground(_color)
    if 'bold' in style:
        _format.setFontWeight(QtGui.QFont.Weight.Bold)
    if 'italic' in style:
        _format.setFontItalic(True)

    return _format


# Syntax styles that can be shared by all languages
_STYLES = {
    'keyword': _color_format('cyan'),
    'operator': _color_format('white'),
    'brace': _color_format('orange'),
    'defclass': _color_format('lightgreen'),
    'string': _color_format('gray'),
    'string2': _color_format('gray'),
    'comment': _color_format('darkgreen', 'italic'),
    'self': _color_format('orange'),
    'numbers': _color_format('magenta'),
}


class PythonHighlighter(QtGui.QSyntaxHighlighter):
    """Syntax highlighter for the Python language."""
    # Python keywords
    keywords = [
        'and', 'assert', 'break', 'class', 'continue', 'def',
        'del', 'elif', 'else', 'except', 'exec', 'finally',
        'for', 'from', 'global', 'if', 'import', 'in',
        'is', 'lambda', 'not', 'or', 'pass', 'print',
        'raise', 'return', 'try', 'while', 'yield',
        'None', 'True', 'False',
    ]

    # Python operators
    operators = [
        '=',
        # Comparison
        '==', '!=', '<', '<=', '>', '>=',
        # Arithmetic
        '\+', '-', '\*', '/', '//', '\%', '\*\*',
        # In-place
        '\+=', '-=', '\*=', '/=', '\%=',
        # Bitwise
        '\^', '\|', '\&', '\~', '>>', '<<',
    ]

    # Python braces
    braces = [
        '\{', '\}', '\(', '\)', '\[', '\]',
    ]

    def __init__(self, parent: QtGui.QTextDocument = None) -> None:
        super().__init__(parent)

        # Multi-line strings (expression, flag, style)
        self.tri_single = (QtCore.QRegularExpression(r"[']{3}"), 1, _STYLES['string2'])
        self.tri_double = (QtCore.QRegularExpression(r'["]{3}'), 2, _STYLES['string2'])

        rules = []

        # Keyword, operator, and brace rules
        rules += [(r'\b%s\b' % w, 0, _STYLES['keyword']) for w in PythonHighlighter.keywords]
        rules += [(r'%s' % o, 0, _STYLES['operator']) for o in PythonHighlighter.operators]
        rules += [(r'%s' % b, 0, _STYLES['brace']) for b in PythonHighlighter.braces]

        # All other rules
        rules += [
            # 'self'
            (r'\bself\b', 0, _STYLES['self']),

            # 'def' followed by an identifier
            (r'\bdef\b\s*(\w+)', 1, _STYLES['defclass']),
            # 'class' followed by an identifier
            (r'\bclass\b\s*(\w+)', 1, _STYLES['defclass']),

            # Numeric literals
            (r'\b[+-]?[0-9]+[lL]?\b', 0, _STYLES['numbers']),
            (r'\b[+-]?0[xX][0-9A-Fa-f]+[lL]?\b', 0, _STYLES['numbers']),
            (r'\b[+-]?[0-9]+(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?\b', 0, _STYLES['numbers']),

            # Double-quoted string, possibly containing escape sequences
            (r'"[^"\\]*(\\.[^"\\]*)*"', 0, _STYLES['string']),
            # Single-quoted string, possibly containing escape sequences
            (r"'[^'\\]*(\\.[^'\\]*)*'", 0, _STYLES['string']),

            # From '#' until a newline
            (r'#[^\n]*', 0, _STYLES['comment']),
        ]

        # Build a QRegularExpression for each pattern
        self.rules = [
            (QtCore.QRegularExpression(pat), index, fmt)
            for (pat, index, fmt) in rules
        ]

    def highlightBlock(self, text: str) -> None:
        """Apply syntax highlighting to the given block of text."""
        self.tripleQuoutesWithinStrings = []

        # First pass: detect embedded triple quotes inside single-line strings
        string_rule_patterns = {
            r'"[^"\\]*(\\.[^"\\]*)*"',
            r"'[^'\\]*(\\.[^'\\]*)*'"
        }
        for expression, _nth, _fmt in self.rules:
            if expression.pattern() not in string_rule_patterns:
                continue
            it = expression.globalMatch(text, 0)
            while it.hasNext():
                m = it.next()
                start0 = m.capturedStart(0)
                if start0 < 0:
                    continue
                ii = self.tri_single[0].match(text, start0 + 1).capturedStart(0)
                if ii == -1:
                    ii = self.tri_double[0].match(text, start0 + 1).capturedStart(0)
                if ii != -1:
                    # mark the three chars so we can skip them later
                    self.tripleQuoutesWithinStrings.extend((ii, ii + 1, ii + 2))

        # Second pass: apply all rules with QRegularExpressionMatch
        for expression, nth, fmt in self.rules:
            it = expression.globalMatch(text, 0)
            while it.hasNext():
                m = it.next()

                start = m.capturedStart(nth)
                length = m.capturedLength(nth)

                # Fallback to whole match if nth capture missing
                if start < 0 or length <= 0:
                    start = m.capturedStart(0)
                    length = m.capturedLength(0)

                if start < 0 or length <= 0:
                    continue

                # Skip embedded triple-quote characters inside string tokens
                if start in self.tripleQuoutesWithinStrings:
                    continue

                self.setFormat(start, length, fmt)

        self.setCurrentBlockState(0)

        # Multi-line strings
        in_multiline = self.match_multiline(text, *self.tri_single)
        if not in_multiline:
            self.match_multiline(text, *self.tri_double)

    def match_multiline(
            self,
            text: str,
            delimiter: QtCore.QRegularExpression,
            in_state: int,
            style: QtGui.QTextCharFormat
    ) -> bool:
        """Do highlight of multi-line strings.

        Args:
            text (str): The text to perform the highlight matching on.
            delimiter (QtCore.QRegularExpression): A QRegularExpression for
                triple-single/double-quotes.
            in_state (int): Unique integer representing the state when inside
                strings.
            style (QtGui.QTextCharFormat): The color to apply to multiline text.
        Returns:
            True if we're still inside a multi-line string when finished.
        """
        fmt = style

        # If inside triple-single/double quotes, start at 0
        if self.previousBlockState() == in_state:
            start = 0
            add = 0
        else:
            first_match = delimiter.match(text)
            start = first_match.capturedStart() if first_match.hasMatch() else -1
            # skipping triple quotes within strings
            if start in getattr(self, 'tripleQuoutesWithinStrings', set()):
                return False
            add = first_match.capturedLength() if first_match.hasMatch() else 0

        # As long as there's a delimiter match on this line...
        while start >= 0:
            # Look for the ending delimiter
            end_match = delimiter.match(text, start + add)
            end = end_match.capturedStart() if end_match.hasMatch() else -1

            if end >= add:
                length = end - start + add + (
                    end_match.capturedLength() if end_match.hasMatch() else 0
                )
                self.setCurrentBlockState(0)
            else:
                self.setCurrentBlockState(in_state)
                length = len(text) - start + add

            # Apply formatting
            self.setFormat(start, length, fmt)

            # Look for the next match
            next_match = delimiter.match(text, start + length)
            start = next_match.capturedStart() if next_match.hasMatch() else -1
            add = next_match.capturedLength() if next_match.hasMatch() else 0

        # Return True if still inside a multi-line string, False otherwise
        return self.currentBlockState() == in_state
