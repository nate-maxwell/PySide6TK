import json

from PySide6 import QtCore
from PySide6 import QtGui
from PySide6 import QtWidgets

from PySide6TK import QtWrappers


example_code = """{
    "General": {
        "show_full_name": "str",
        "show_type": [
            "Feature",
            "Episodic"
        ],
        "default_phase": [
            "previs",
            "postvis",
            "techvis"
        ],
        "default_nuke_color_space": [
            "linear",
            "rec709",
            "sRGB",
            "Gamma1.8",
            "Gamma1.8",
            "Gamma2.2",
            "Cineon",
            "Panalog",
            "REDLog",
            "ViperLog",
            "AlexaV3LogC",
            "PLogLin",
            "SLog",
            "Slog1",
            "Slog2",
            "Slog3",
            "CLog",
            "Protune",
            "REDSpace"
        ],
        "framerate": "int",
        "version_padding": "int",
        "frame_padding": "int",
        "focal_length_pack": "list[int]",
        "handles": "list[int]"
    },
    "Previz": {
        "resolution": "list[int]",
        "image_type": [
            "jpg",
            "png"
        ],
        "maya_unit_scale": "float",
        "nuke_codec": [
            "Animation",
            "Apple ProRes",
            "Avid DNxHD",
            "Avid DNxHR",
            "H.246",
            "Motion JPEG A",
            "Motion JPEG B",
            "MPEG-4",
            "Photo - JPEG",
            "PNG",
            "Uncompressed"
        ],
        "nuke_template_name": "str",
        "type_prefix": "str",
        "type_suffix": "str",
        "nuke_name_format": "str",
        "six_pack_resolution": "str"
    },
    "Postviz": {
        "resolution": "list[int]",
        "image_type": [
            "jpg",
            "png"
        ],
        "nuke_codec": [
            "Animation",
            "Apple ProRes",
            "Avid DNxHD",
            "Avid DNxHR",
            "H.246",
            "Motion JPEG A",
            "Motion JPEG B",
            "MPEG-4",
            "Photo - JPEG",
            "PNG",
            "Uncompressed"
        ],
        "nuke_template_name": "str",
        "type_prefix": "str",
        "type_suffix": "str",
        "nuke_name_format": "str"
    },
    "Techviz": {
        "resolution": "list[int]",
        "image_type": [
            "jpg",
            "png"
        ],
        "nuke_codec": [
            "Animation",
            "Apple ProRes",
            "Avid DNxHD",
            "Avid DNxHR",
            "H.246",
            "Motion JPEG A",
            "Motion JPEG B",
            "MPEG-4",
            "Photo - JPEG",
            "PNG",
            "Uncompressed"
        ],
        "nuke_template_name": "str",
        "type_prefix": "str",
        "type_suffix": "str",
        "nuke_name_format": "str"
    },
    "Virprod": {
        "resolution": "list[int]",
        "image_type": [
            "jpg",
            "png"
        ],
        "locations": "list[str]",
        "mocap_slate_server_ip": "str",
        "nuke_codec": [
            "Animation",
            "Apple ProRes",
            "Avid DNxHD",
            "Avid DNxHR",
            "H.246",
            "Motion JPEG A",
            "Motion JPEG B",
            "MPEG-4",
            "Photo - JPEG",
            "PNG",
            "Uncompressed"
        ],
        "nuke_template_name": "str",
        "type_prefix": "str",
        "type_suffix": "str",
        "nuke_name_format": "str"
    }
}
"""


class JsonEditor(QtWrappers.MainWindow):
    def __init__(self) -> None:
        super().__init__('Json Editor', (450, 750))
        self.toolbar = QtWrappers.HelpToolbar(
            parent=self,
            description='Example code editor with dict viewer for viewing json',
            version='1.0.0',
            author='Nate Maxwell',
            repo_url='https://github.com/nate-maxwell/PySide6TK',
            documentation_url='https://github.com/nate-maxwell/PySide6TK'
        )

        self._create_widgets()
        self._create_layout()
        self._create_connections()

    def _create_widgets(self) -> None:
        self.widget_main = QtWidgets.QWidget()
        self.layout_main = QtWidgets.QVBoxLayout()

        font = QtGui.QFont('Courier')
        font.setPointSize(10)

        self.splitter = QtWidgets.QSplitter(QtCore.Qt.Orientation.Horizontal)

        self.sa_output = QtWrappers.ScrollArea()
        self.dict_viewer = QtWrappers.DictViewer('Output', {})

        self.vlayout_editor = QtWidgets.QVBoxLayout()
        self.editor = QtWrappers.CodeEditor(QtWrappers.JsonHighlighter)
        self.editor.setFont(font)
        self.editor.setPlainText(example_code)
        self.btn_run = QtWidgets.QPushButton(
            text='Run',
            icon=self.style().standardIcon(
                QtWidgets.QStyle.StandardPixmap.SP_MediaPlay)
        )

    def _create_layout(self) -> None:
        self.sa_output.add_widget(self.dict_viewer)
        self.splitter.addWidget(self.sa_output)

        self.vlayout_editor.addWidget(self.editor)
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.btn_run)
        self.vlayout_editor.addLayout(button_layout)
        wid = QtWidgets.QWidget()
        wid.setLayout(self.vlayout_editor)
        self.splitter.addWidget(wid)

        self.setCentralWidget(self.widget_main)
        self.widget_main.setLayout(self.layout_main)
        self.layout_main.addWidget(self.splitter)

    def _create_connections(self) -> None:
        self.btn_run.clicked.connect(self.refresh)

    def refresh(self) -> None:
        self.dict_viewer.data = json.loads(self.editor.toPlainText())
        self.dict_viewer.refresh()


if __name__ == '__main__':
    QtWrappers.exec_app(JsonEditor, 'JsonEditor')
