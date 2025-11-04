import sys

from PySide6 import QtCore
from PySide6 import QtWidgets

from PySide6TK import QtWrappers


def demo() -> None:
    """Run a quick demo showing both dialogs."""
    _ = QtWidgets.QApplication(sys.argv)

    regex = QtCore.QRegularExpression(r'^[A-Za-z0-9_]{3,24}$')
    single = QtWrappers.SingleLineTextDialog(
        title='Create Username',
        label='Choose a username (3–24 word chars):',
        initial_text='user_01',
        placeholder='my_username',
        regex_validator=regex,
        allow_empty=False,
    )
    if single.exec() == QtWidgets.QDialog.DialogCode.Accepted:
        QtWidgets.QMessageBox.information(None, 'Username', f'You chose: {single.text()}')

    multi = QtWrappers.MultiLineTextDialog(
        title='Add Notes',
        label='Enter notes:',
        placeholder='Type your notes here...',
        allow_empty=True,
    )
    if multi.exec() == QtWidgets.QDialog.DialogCode.Accepted:
        QtWidgets.QMessageBox.information(None, 'Notes', f'Notes length: {len(multi.text())} chars')


if __name__ == '__main__':
    demo()
