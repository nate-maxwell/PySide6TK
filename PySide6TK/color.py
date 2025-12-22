"""
# Color Library

* Description:

    A library of color utilities and color picker widgets.
"""


from typing import Optional

from PySide6 import QtWidgets
from PySide6 import QtCore
from PySide6 import QtGui


class RectangularColorPicker(QtWidgets.QWidget):
    """A rectangular color picker with hue/saturation grid and value slider."""

    colorChanged = QtCore.Signal(QtGui.QColor)

    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        self._hue = 0
        self._saturation = 255
        self._value = 255
        self._current_color = QtGui.QColor.fromHsv(
            self._hue,
            self._saturation,
            self._value
        )

        self._rect_width = 360
        self._rect_height = 256
        self._dragging_rect = False

        self._hs_image: Optional[QtGui.QImage] = None
        self._render_hs_gradient()

        self.setMinimumSize(self._rect_width, self._rect_height + 10)

    def _render_hs_gradient(self) -> None:
        """Pre-render the hue/saturation gradient image."""
        self._hs_image = QtGui.QImage(
            self._rect_width,
            self._rect_height,
            QtGui.QImage.Format.Format_RGB32
        )

        for y in range(self._rect_height):
            saturation = 255 - y  # Top = full saturation, bottom = no saturation
            for x in range(self._rect_width):
                hue = x  # Left to right = 0 to 359 degrees
                color = QtGui.QColor.fromHsv(hue, saturation, 255)
                self._hs_image.setPixelColor(x, y, color)

    def _get_rect(self) -> QtCore.QRect:
        """Get the rectangle bounds for the color grid."""
        return QtCore.QRect(0, 0, self._rect_width, self._rect_height)

    def paintEvent(self, event: QtGui.QPaintEvent) -> None:
        """Paint the color rectangle."""
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)

        rect = self._get_rect()
        painter.drawImage(rect, self._hs_image)

        # Value darkening overlay
        if self._value < 255:
            overlay_color = QtGui.QColor(0, 0, 0, 255 - self._value)
            painter.fillRect(rect, overlay_color)

        # Selection indicator
        x = self._hue
        y = 255 - self._saturation

        # White ring
        painter.setPen(QtGui.QPen(QtCore.Qt.GlobalColor.white, 2))
        painter.setBrush(QtCore.Qt.BrushStyle.NoBrush)
        painter.drawEllipse(QtCore.QPointF(x, y), 6, 6)

        # Black ring
        painter.setPen(QtGui.QPen(QtCore.Qt.GlobalColor.black, 1))
        painter.drawEllipse(QtCore.QPointF(x, y), 6, 6)

        # Rectangle border
        painter.setPen(QtGui.QPen(QtCore.Qt.GlobalColor.black, 1))
        painter.setBrush(QtCore.Qt.BrushStyle.NoBrush)
        painter.drawRect(rect)

    def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:
        """Handle mouse press to start color selection."""
        pos = event.position()
        rect = self._get_rect()

        if rect.contains(pos.toPoint()):
            self._dragging_rect = True
            self._update_color_from_pos(pos)

    def mouseMoveEvent(self, event: QtGui.QMouseEvent) -> None:
        """Handle mouse move while dragging."""
        if self._dragging_rect:
            self._update_color_from_pos(event.position())

    def mouseReleaseEvent(self, event: QtGui.QMouseEvent) -> None:
        """Handle mouse release to stop dragging."""
        self._dragging_rect = False

    def _update_color_from_pos(self, pos: QtCore.QPointF) -> None:
        """Update color based on mouse position in rectangle."""
        # Clamp position to rectangle bounds
        x = max(0, min(self._rect_width - 1, int(pos.x())))
        y = max(0, min(self._rect_height - 1, int(pos.y())))

        self._hue = x
        self._saturation = 255 - y

        self._update_color()

    def _update_color(self) -> None:
        """Update the current color and emit signal."""
        self._current_color = QtGui.QColor.fromHsv(
            self._hue,
            self._saturation,
            self._value
        )
        self.update()
        self.colorChanged.emit(self._current_color)

    def set_value(self, value: int) -> None:
        """Set the value component (0-255)."""
        self._value = value
        self._update_color()

    def set_color(self, color: QtGui.QColor) -> None:
        """Set the current color."""
        h, s, v, _ = color.getHsv()
        self._hue = h if h != -1 else 0
        self._saturation = s
        self._value = v
        self._current_color = color
        self.update()

    def get_color(self) -> QtGui.QColor:
        """Get the current color."""
        return self._current_color


class ColorPickerPanel(QtWidgets.QWidget):
    """A color picker widget with hue/saturation rectangle and value slider."""

    colorChanged = QtCore.Signal(QtGui.QColor)

    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)

        self._create_widgets()
        self._create_layout()
        self._create_connections()
        self._update_displays(self.rect_picker.get_color())

    def _create_widgets(self) -> None:
        self.layout_main = QtWidgets.QVBoxLayout()

        self.rect_picker = RectangularColorPicker()
        self.rect_picker.colorChanged.connect(self._on_color_changed)

        # Value slider
        self.hlayout_value = QtWidgets.QHBoxLayout()
        self.slider_value = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
        self.slider_value.setRange(0, 255)
        self.slider_value.setValue(255)

        self.value_label = QtWidgets.QLabel('255')
        self.value_label.setFixedWidth(40)

        # Color info panel
        self.hlayout_preview = QtWidgets.QHBoxLayout()
        self.color_preview = QtWidgets.QLabel()
        self.color_preview.setFixedSize(100, 40)
        self.color_preview.setFrameStyle(
            QtWidgets.QFrame.Shape.Box | QtWidgets.QFrame.Shadow.Sunken
        )

        self.vlayout_values = QtWidgets.QVBoxLayout()

        # RGB Display
        self.hlayout_rgb = QtWidgets.QHBoxLayout()
        self.lbl_rgb = QtWidgets.QLabel('(255, 0, 0)')

        # HSV Display
        self.hlayout_hsv = QtWidgets.QHBoxLayout()
        self.lbl_hsv = QtWidgets.QLabel('(0, 255, 255)')

        # Hex Display
        self.hlayout_hex = QtWidgets.QHBoxLayout()
        self.lbl_hex = QtWidgets.QLabel('#FF0000')

    def _create_layout(self) -> None:
        # Value slider
        self.hlayout_value.addWidget(QtWidgets.QLabel('Value:'))
        self.hlayout_value.addWidget(self.slider_value)
        self.hlayout_value.addWidget(self.value_label)

        # RGB Display
        self.hlayout_rgb.addWidget(QtWidgets.QLabel('RGB:'))
        self.hlayout_rgb.addWidget(self.lbl_rgb)
        self.hlayout_rgb.addStretch()

        # HSV Display
        self.hlayout_hsv.addWidget(QtWidgets.QLabel('HSV:'))
        self.hlayout_hsv.addWidget(self.lbl_hsv)
        self.hlayout_hsv.addStretch()

        # Hex Display
        self.hlayout_hex.addWidget(QtWidgets.QLabel('Hex:'))
        self.hlayout_hex.addWidget(self.lbl_hex)
        self.hlayout_hex.addStretch()

        self.vlayout_values.addLayout(self.hlayout_rgb)
        self.vlayout_values.addLayout(self.hlayout_hsv)
        self.vlayout_values.addLayout(self.hlayout_hex)

        # Color info panel
        self.hlayout_preview.addWidget(QtWidgets.QLabel('Preview:'))
        self.hlayout_preview.addWidget(self.color_preview)
        self.hlayout_preview.addLayout(self.vlayout_values)
        self.hlayout_preview.addStretch()

        # Main
        self.setLayout(self.layout_main)
        self.layout_main.addWidget(self.rect_picker)
        self.layout_main.addLayout(self.hlayout_value)
        self.layout_main.addLayout(self.hlayout_preview)

    def _create_connections(self) -> None:
        self.slider_value.valueChanged.connect(self._on_value_changed)

    def _on_value_changed(self, value: int) -> None:
        """Handle value slider changes."""
        self.value_label.setText(str(value))
        self.rect_picker.set_value(value)

    def _on_color_changed(self, color: QtGui.QColor) -> None:
        """Handle color changes from the rectangular picker."""
        self._update_displays(color)
        self.colorChanged.emit(color)

    def _update_displays(self, color: QtGui.QColor) -> None:
        """Update all color displays."""
        self.color_preview.setStyleSheet(f'background-color: {color.name()};')

        r, g, b = color.red(), color.green(), color.blue()
        self.lbl_rgb.setText(f'({r}, {g}, {b})')

        h, s, v, _ = color.getHsv()
        self.lbl_hsv.setText(f'({h}, {s}, {v})')

        self.lbl_hex.setText(color.name().upper())

    def set_color(self, color: QtGui.QColor) -> None:
        """Set the current color."""
        h, s, v, _ = color.getHsv()

        self.slider_value.blockSignals(True)
        self.slider_value.setValue(v)
        self.slider_value.blockSignals(False)
        self.value_label.setText(str(v))

        self.rect_picker.set_color(color)
        self._update_displays(color)

    def get_color(self) -> QtGui.QColor:
        """Get the current color."""
        return self.rect_picker.get_color()


class ColorButton(QtWidgets.QPushButton):
    colorChanged = QtCore.Signal(QtGui.QColor)

    def __init__(
            self,
            color: str = '#ffffff',
            parent: Optional[QtWidgets.QWidget] = None
    ) -> None:
        super().__init__(parent)
        self._color = QtGui.QColor(color)
        self.setFixedSize(32, 18)
        self._update_style()
        self.clicked.connect(self.choose_color)

    def _update_style(self) -> None:
        self.setStyleSheet(
            f'background-color: {self._color.name()}; border: 1px solid #333;'
        )

    def choose_color(self) -> None:
        color = QtWidgets.QColorDialog.getColor(
            QtGui.QColor('#ffffff'),
            self,
            'Choose Color'
        )
        if color.isValid():
            self._color = color
            self._update_style()
            self.colorChanged.emit(color)

    def color(self) -> QtGui.QColor:
        return self._color
