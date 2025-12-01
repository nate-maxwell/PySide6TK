"""
# Status Feedback

* Description:

    A library of application or device usage feedback widgets and helper
    functions.

    Anything from a percent usage bar to ways to get the used memory values
    on windows.
"""


import ctypes
import ctypes.wintypes
import time
import urllib.request
from typing import Optional

from PySide6 import QtCore
from PySide6 import QtGui
from PySide6 import QtWidgets

import PySide6TK.shapes


class _MemoryStatus(ctypes.Structure):
    _fields_ = [
        ('dwLength', ctypes.wintypes.DWORD),
        ('dwMemoryLoad', ctypes.wintypes.DWORD),
        ('ullTotalPhys', ctypes.c_ulonglong),
        ('ullAvailPhys', ctypes.c_ulonglong),
        ('ullTotalPageFile', ctypes.c_ulonglong),
        ('ullAvailPageFile', ctypes.c_ulonglong),
        ('ullTotalVirtual', ctypes.c_ulonglong),
        ('ullAvailVirtual', ctypes.c_ulonglong),
        ('ullAvailExtendedVirtual', ctypes.c_ulonglong),
    ]


class _FileTime(ctypes.Structure):
    _fields_ = [
        ('dwLowDateTime', ctypes.wintypes.DWORD),
        ('dwHighDateTime', ctypes.wintypes.DWORD),
    ]


def get_memory_usage() -> float:
    """Calculate memory usage using Windows API GlobalMemoryStatusEx.
    Returns:
        float: Float value as percentage.
    """
    try:
        mem_status = _MemoryStatus()
        mem_status.dwLength = ctypes.sizeof(_MemoryStatus)

        result = ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(mem_status))

        if result:
            return float(mem_status.dwMemoryLoad)
        else:
            return 0.0

    except AttributeError:
        # Not on Windows API
        return 0.0
    except (OSError, ValueError, TypeError):
        return 0.0


def _filetime_to_int(ft: _FileTime) -> int:
    """Convert FILETIME to integer."""
    return (ft.dwHighDateTime << 32) + ft.dwLowDateTime


class UsageBar(QtWidgets.QWidget):
    """A custom Qt widget that displays a horizontal progress bar with percentage text.

    This widget renders a filled bar that visually represents a percentage value,
    with centered text showing both the label and current percentage. The bar
    includes a colored fill that grows from left to right based on the percentage,
    a gray background, and a light border.

    Args:
        label_text: The text label to display alongside the percentage value.
        color: The QColor to use for the filled portion of the bar.
        height: The minimum height of the widget in pixels. Defaults to 20.
        parent: The parent widget, if any. Defaults to None.

    Attributes:
        label_text (str): The label text displayed in the bar.
        color (QtGui.QColor): The color of the filled portion.
        percentage (float): The current percentage value (0-100).

    Example:
        >>> usage_bar = UsageBar("CPU Usage", QtGui.QColor(0, 255, 0))
        >>> usage_bar.set_percentage(75.5)
    """

    def __init__(
            self,
            label_text: str,
            color: QtGui.QColor,
            height: int = 20,
            parent: QtWidgets.QWidget | None = None
    ) -> None:
        super().__init__(parent)
        self.label_text: str = label_text
        self.color: QtGui.QColor = color
        self.setMinimumHeight(height)
        self.percentage: float = 0

        self.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Fixed
        )

    def paintEvent(self, event: QtGui.QPaintEvent) -> None:
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)

        # Background
        painter.fillRect(self.rect(), QtGui.QColor(100, 100, 100))

        # Filled Portion
        bar_width = int(self.width() * self.percentage / 100)
        painter.fillRect(0, 0, bar_width, self.height(), self.color)

        # Border
        painter.setPen(QtGui.QColor(200, 200, 200))
        painter.drawRect(0, 0, self.width() - 1, self.height() - 1)

        # Text
        painter.setPen(QtCore.Qt.GlobalColor.black)
        font = QtGui.QFont(
            'Arial',
            self.height() * 8 // 20,
            QtGui.QFont.Weight.Bold
        )
        painter.setFont(font)
        text = f'{self.label_text}: {self.percentage:.1f}%'
        painter.drawText(self.rect(), QtCore.Qt.AlignmentFlag.AlignCenter, text)

    def set_percentage(self, percentage: float) -> None:
        self.percentage = max(0, min(100, int(percentage)))
        self.update()


class CPUUsageBar(UsageBar):
    """
    A UsageBar widget that displays the current percentage of CPU usage through
    the use of the Windows API.


    Args:
          height (int): How tall to draw the bar. Defaults to 20.
          parent (QtWidgets.QWidget): Optional parent. Defaults to None.

    Methods:
        refresh() : Will update the bar.

    Attributes:
        last_idle_time (int): Previous idle time value for CPU calculation.
        last_kernel_time (int): Previous kernel time value for CPU calculation.
        last_user_time (int): Previous user time value for CPU calculation.
    """

    def __init__(
            self,
            height: int = 20,
            parent: Optional[QtWidgets.QWidget] = None
    ) -> None:
        super().__init__(
            'CPU',
            QtGui.QColor(52, 152, 219),
            height,
            parent
        )
        self.last_idle_time: int = 0
        self.last_kernel_time: int = 0
        self.last_user_time: int = 0

    def refresh(self) -> None:
        self.set_percentage(self.get_cpu_usage())

    def get_cpu_usage(self) -> float:
        """Calculate CPU usage using Windows API GetSystemTimes"""
        try:
            idle_time = _FileTime()
            kernel_time = _FileTime()
            user_time = _FileTime()

            # Get system times
            result = ctypes.windll.kernel32.GetSystemTimes(
                ctypes.byref(idle_time),
                ctypes.byref(kernel_time),
                ctypes.byref(user_time)
            )

            if not result:
                return 0.0

            idle = _filetime_to_int(idle_time)
            kernel = _filetime_to_int(kernel_time)
            user = _filetime_to_int(user_time)

            if self.last_idle_time != 0:
                idle_delta = idle - self.last_idle_time
                kernel_delta = kernel - self.last_kernel_time
                user_delta = user - self.last_user_time
                total_delta = kernel_delta + user_delta

                if total_delta > 0:
                    cpu_percent = ((total_delta - idle_delta) / total_delta) * 100
                else:
                    cpu_percent = 0.0
            else:
                cpu_percent = 0.0

            self.last_idle_time = idle
            self.last_kernel_time = kernel
            self.last_user_time = user

            return cpu_percent

        except (OSError, AttributeError, ctypes.ArgumentError):
            return 0.0


class MemoryUsageBar(UsageBar):
    """
    A UsageBar widget that displays the current percentage of mem usage through
    the use of the Windows API.

    Args:
          height (int): How tall to draw the bar. Defaults to 20.
          parent (QtWidgets.QWidget): Optional parent. Defaults to None.

    Methods:
        refresh() : Will update the bar.
    """
    def __init__(
            self,
            height: int = 20,
            parent: Optional[QtWidgets.QWidget] = None
    ) -> None:
        super().__init__(
            'Memory',
            QtGui.QColor(46, 204, 113),
            height,
            parent
        )

    def refresh(self) -> None:
        self.set_percentage(get_memory_usage())


class ResourceMonitor(QtWidgets.QWidget):
    """A Qt widget that monitors and displays real-time system resource usage.

    This widget provides a visual display of CPU and memory usage through
    colored progress bars that update every second. It uses Windows API calls
    to retrieve accurate CPU usage statistics and displays both CPU and memory
    usage as percentage values.

    The widget creates a window titled 'System Monitor' with two horizontal
    usage bars: one for CPU (blue) and one for memory (green). The bars
    automatically update at 1-second intervals.

    Attributes:
        cpu_bar (UsageBar): The progress bar widget displaying CPU usage.
        memory_bar (UsageBar): The progress bar widget displaying memory usage.
        timer (QtCore.QTimer): Timer that triggers periodic updates.

    Note:
        This class uses Windows-specific API calls (GetSystemTimes) for CPU
        monitoring and is designed to run on Windows systems only.

    Example:
        >>> app = QtWidgets.QApplication(sys.argv)
        >>> monitor = ResourceMonitor()
        >>> monitor.show()
        >>> sys.exit(app.exec())
    """

    def __init__(self, bar_height: int = 20, horizontal: bool = True) -> None:
        super().__init__()
        self.setWindowTitle('System Monitor')
        self.setMinimumHeight(bar_height+2)
        self.bar_height = bar_height
        self.horizontal = horizontal

        self._create_widgets()
        self._create_layout()
        self._setup_timer()

    def _create_widgets(self) -> None:
        if self.horizontal:
            self.layout = QtWidgets.QHBoxLayout()
        else:
            self.layout = QtWidgets.QVBoxLayout()

        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(10)

        self.cpu_bar = CPUUsageBar(self.bar_height, self)
        self.memory_bar = MemoryUsageBar(self.bar_height, self)

    def _create_layout(self) -> None:
        self.layout.addWidget(self.cpu_bar)
        self.layout.addWidget(self.memory_bar)
        self.setLayout(self.layout)

    def _setup_timer(self) -> None:
        # Update every second
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_stats)
        self.timer.start(1000)

        # Initial update
        self.update_stats()

    def update_stats(self) -> None:
        self.cpu_bar.refresh()
        self.memory_bar.refresh()


def check_connection(
        url: str = 'https://www.google.com',
        great: int = 100,
        good: int = 300,
        fair: int = 600
) -> int:
    """Check actual network connection strength based on latency.

    Pings the given url and checks the response time.
    Returns int:
        < great MS = 4
        > great but < good = 3
        > good but < fair = 2
        > fair = 1
        timeout or exception = 0
    """
    try:
        start_time = time.time()
        response = urllib.request.urlopen(url, timeout=5)
        latency = (time.time() - start_time) * 1000
        response.close()

        if latency < great:
            return 4
        elif latency < good:
            return 3
        elif latency < fair:
            return 2
        else:
            return 1

    except Exception:
        return 0


class ConnectionStrengthWidget(QtWidgets.QWidget):
    """
    A widget that displays network connection strength as a series of vertical
    bars.

    The widget shows 4 bars of increasing height, with the number of filled
    bars indicating the connection strength (0-4). Bars are color-coded based
    on strength:
    - Gray: No connection (strength 0)
    - Orange: Weak connection (strength 1-2)
    - Green: Strong connection (strength 3-4)

    The widget automatically checks connection strength every 5 seconds using a
    timer.

    Attributes:
        strength (int): Current connection strength level (0-4)
        timer (QTimer): Timer for periodic connection strength updates
    """

    def __init__(self, parent: Optional[QtWidgets.QWidget] = None) -> None:
        super().__init__(parent)
        self.strength: int = 0  # 0-4 (0 = no connection, 4 = excellent)
        self.setMinimumSize(24, 16)

        self._init_timer()

    def _init_timer(self) -> None:
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self._update_connection_strength)
        self.timer.start(5000)

    def _update_connection_strength(self) -> None:
        strength = check_connection()
        self.setStrength(strength)

    def paintEvent(self, event: QtGui.QPaintEvent) -> None:
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)

        bar_width: int = 3
        bar_spacing: int = 2
        num_bars: int = 4

        color_no_conn = QtGui.QColor(150, 150, 150)
        color_weak = QtGui.QColor(255, 150, 0)
        color_strong = QtGui.QColor(0, 200, 0)
        color_inactive = QtGui.QColor(200, 200, 200)

        if self.strength == 0:
            color = color_no_conn
        elif self.strength <= 2:
            color = color_weak
        else:
            color = color_strong

        for i in range(num_bars):
            x: int = i * (bar_width + bar_spacing)
            bar_height: int = (i + 1) * 3
            y: int = self.height() - bar_height

            if i < self.strength:
                painter.setBrush(color)
            else:
                painter.setBrush(color_inactive)

            painter.setPen(QtCore.Qt.PenStyle.NoPen)
            painter.drawRect(x, y, bar_width, bar_height)

    def setStrength(self, strength: int) -> None:
        """Set connection strength (0-4)"""
        self.strength = max(0, min(4, strength))
        self.update()

    def getStrength(self) -> int:
        return self.strength

    def sizeHint(self) -> QtCore.QSize:
        return QtCore.QSize(24, 16)


class BasicStatusBar(QtWidgets.QStatusBar):
    def __init__(self, parent: Optional[QtWidgets.QWidget] = None) -> None:
        super().__init__(parent)
        self.addPermanentWidget(PySide6TK.shapes.HorizontalSpacer(0))
        self.addPermanentWidget(ResourceMonitor())
        self.addPermanentWidget(ConnectionStrengthWidget(self))

        self.setStyleSheet("""
            QStatusBar::item {
                border: none;
            }
        """)
