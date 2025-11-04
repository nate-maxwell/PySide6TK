"""
# Test Playground

* Description:

    Sandbox file for testing - DO NOT CHECK IN!
"""

from PySide6TK import QtWrappers

data = {
    "parameters": {
        "address": "192.168.1.238",
        "port": 5000,
        "verbosity": 2,
        "log-output": 0,
        "print-tree": True,
        "xform-timeout": "45s",
        "consolidate": True,
        "persistent-connections": True,
        "security-tokens": [
            "lockheed",
            "martin"
        ]
    },
    "route": {
        "name": "default",
        "channel": {
            "name": "inmem",
            "strategy": "pub-sub",
            "transformers": {
                "address1": "127.0.0.1:7010",
                "address2": "10.0.0.52:8008"
            },
            "subscribers": {
                "address1": "127.0.0.1:1234",
                "address2": "16.70.18.1:9999"
            }
        }
    }
}


class TestWindow(QtWrappers.MainWindow):
    def __init__(self) -> None:
        super().__init__('Example Dict Viewer',
                         (0, 0), (0, 0))
        self.widget = QtWrappers.DictViewer('Test Data', data)
        self.setCentralWidget(self.widget)


if __name__ == '__main__':
    QtWrappers.exec_app(TestWindow, 'ExampleDictViewer')
