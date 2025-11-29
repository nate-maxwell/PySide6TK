import ctypes
import ctypes.wintypes

from PySide6 import QtCore
from PySide6 import QtGui
from PySide6 import QtWidgets


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
    """Calculate memory usage using Windows API GlobalMemoryStatusEx"""
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


def filetime_to_int(ft: _FileTime) -> int:
    """Convert FILETIME to integer."""
    return (ft.dwHighDateTime << 32) + ft.dwLowDateTime


class _UsageBar(QtWidgets.QProgressBar):
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

        self.setRange(0, 100)
        self.setValue(0)
        self.setMinimumHeight(height)
        self.setTextVisible(True)
        self.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        self.setStyleSheet(f'''
            QProgressBar {{
                border: 1px solid rgb(200, 200, 200);
                background-color: rgb(100, 100, 100);
                text-align: center;
                color: black;
                font-family: Arial;
                font-size: 10pt;
                font-weight: bold;
            }}
            QProgressBar::chunk {{
                background-color: rgb({self.color.red()}, {self.color.green()}, {self.color.blue()});
                width: 5px;
            }}
        ''')

    def paintEvent(self, event: QtGui.QPaintEvent) -> None:
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)

        # Background
        painter.fillRect(self.rect(), QtGui.QColor(100, 100, 100))

        # Filled Portion
        bar_width = int(self.width() * self.value() / 100)
        painter.fillRect(0, 0, bar_width, self.height(), self.color)

        # Border
        painter.setPen(QtGui.QColor(200, 200, 200))
        painter.drawRect(0, 0, self.width() - 1, self.height() - 1)

        # Text
        painter.setPen(QtCore.Qt.GlobalColor.black)
        font = QtGui.QFont("Arial", 10, QtGui.QFont.Weight.Bold)
        painter.setFont(font)
        text = f'{self.label_text}: {self.value():.1f}%'
        painter.drawText(self.rect(), QtCore.Qt.AlignmentFlag.AlignCenter, text)

    def set_percentage(self, percentage: float) -> None:
        value = max(0, min(100, int(percentage)))
        self.setValue(value)
        self.setFormat(f'{self.label_text}: {value:.1f}%')


class ResourceMonitor(QtWidgets.QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle('System Monitor')

        self.cpu_bar: _UsageBar
        self.memory_bar: _UsageBar
        self.timer: QtCore.QTimer
        self.last_idle_time: int = 0
        self.last_kernel_time: int = 0
        self.last_user_time: int = 0

        self._create_widgets()
        self._create_layout()
        self._setup_timer()

    def _create_widgets(self) -> None:
        self.layout = QtWidgets.QVBoxLayout()
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setSpacing(10)

        self.cpu_bar = _UsageBar('CPU', QtGui.QColor(52, 152, 219))
        self.memory_bar = _UsageBar('Memory', QtGui.QColor(46, 204, 113))

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

            idle = filetime_to_int(idle_time)
            kernel = filetime_to_int(kernel_time)
            user = filetime_to_int(user_time)

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

    def update_stats(self) -> None:
        cpu_percent = self.get_cpu_usage()
        self.cpu_bar.set_percentage(cpu_percent)

        memory_percent = get_memory_usage()
        self.memory_bar.set_percentage(memory_percent)
