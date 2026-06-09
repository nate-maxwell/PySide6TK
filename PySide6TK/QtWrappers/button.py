"""
Simple wrappers for various buttons, primarily to eliminate boilerplate.
"""


from pathlib import Path
from typing import Optional

from PySide6 import QtWidgets


class ImageButton(QtWidgets.QPushButton):
    """
    A QPushButton with a background image set to the given image path.
    The image is fit to the button size.
    """
    def __init__(
            self,
            image_path: Path,
            parent: Optional[QtWidgets.QWidget] = None
    ) -> None:
        super().__init__('', parent)

        self.setStyleSheet(f"""
            QPushButton {{
                background: url('{image_path.as_posix()}');
                background-position: center;   /* Center the image */
                background-repeat: no-repeat;  /* Prevent tiling */
                background-size: cover;        /* Scale image to fill button */
            }}
        """)
