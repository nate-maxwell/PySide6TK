"""
# Qt Signal

* Descriptions

    Qt Signal Helpers.
"""


import functools
import typing
from typing import Callable

from PySide6 import QtCore


def signal(*types: type) -> QtCore.SignalInstance:
    """A simple wrapper around QtCore.Signal that fixes intellisense and type
    checker issues.
    """
    return typing.cast(QtCore.SignalInstance, typing.cast(object, QtCore.Signal(*types)))


def emit_signal(signal_name: str):
    """Class method decorator for emitting a Qt signal after method execution.

    Examples:
        >>> import PSToolkit.signal
        >>>
        >>> class MyClass(QtCore.QObject):
        >>>     my_signal = PSToolkit.signal.signal()
        >>>
        >>>     @emit_signal('my_signal')
        >>>     def some_method(self, *args):
        >>>         ...
    """
    def signal_decorator(func: Callable):
        @functools.wraps(func)
        def wrapped_method(*args, **kwargs):
            r = func(*args, **kwargs)
            self = args[0]
            signal_ = getattr(self, signal_name)
            signal_.emit()
            return r
        return wrapped_method
    return signal_decorator
