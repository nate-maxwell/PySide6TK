"""
# Example Toolbar

* Description:

    A toolbar that looks like the one we had in maya.
"""


from PySide6 import QtWidgets

from PySide6TK import QtWrappers


class TestToolbar(QtWrappers.Toolbar):
    def __init__(self) -> None:
        super().__init__('Example Toolbar')

    def build(self) -> None:
        self._add_show_button()
        self.add_toolbar_separator()
        self._file_io_section()
        self.add_toolbar_separator()
        self._shot_section()
        self.add_toolbar_separator()
        self._shader_section()
        self.add_toolbar_separator()
        self._rig_section()
        self.add_toolbar_separator()
        self._plugins_section()
        self.add_toolbar_separator()
        self._anim_script_section()
        self.add_toolbar_separator()
        self._asset_scripts_section()
        self.add_toolbar_separator()
        self._measure_section()
        self._rename_script_section()

    def _add_show_button(self) -> None:
        show_button = QtWidgets.QPushButton(f'Show: [  SOMEVIZ  ]\t')
        show_button.setStyleSheet("background-color: black;")
        show_button.setFixedWidth(200)
        show_button.setFixedHeight(25)
        self.addWidget(show_button)

    def _file_io_section(self) -> None:
        self.add_toolbar_command('Save\nVersn', image_path=QtWrappers.BUTTON_ORANGE_40X40)
        self.add_toolbar_separator()
        self.add_toolbar_command('Asset\nBrowsr', image_path=QtWrappers.BUTTON_BLUE_40X40)
        self.add_toolbar_command('Ast Wrk\nBrowsr', image_path=QtWrappers.BUTTON_BLUE_40X40)
        self.add_toolbar_command('Butter\nBrowsr', image_path=QtWrappers.BUTTON_BLUE_40X40)
        self.add_toolbar_command('Asset\nPub', image_path=QtWrappers.BUTTON_BLUE_40X40)
        self.add_toolbar_separator()
        self.add_toolbar_command('Shot\nBrowsr', image_path=QtWrappers.BUTTON_BLUE_40X40)
        self.add_toolbar_command('Shot\nPub', image_path=QtWrappers.BUTTON_BLUE_40X40)

    def _shot_section(self) -> None:
        self.add_toolbar_command('ShotX', image_path=QtWrappers.BUTTON_YELLOW_40X40)
        self.add_toolbar_command('Render', image_path=QtWrappers.BUTTON_YELLOW_40X40)

    def _shader_section(self) -> None:
        submenu = self.add_toolbar_submenu('Shader', image_path=QtWrappers.BUTTON_CYAN_40X40)
        self.add_submenu_command(submenu, 'Shader Browser')
        self.add_submenu_command(submenu, 'Shader Publisher')
        self.add_submenu_command(submenu, 'Random Lambert')
        self.add_submenu_command(submenu, 'KF Material Assign')

    def _rig_section(self) -> None:
        self.add_toolbar_command('Rig Re\nName', image_path=QtWrappers.BUTTON_BLACK_40X40)

        submenu = self.add_toolbar_submenu('Rig', image_path=QtWrappers.BUTTON_BLACK_40X40)
        self.add_submenu_command(submenu, 'Attribute Man')
        self.add_submenu_command(submenu, 'Export Realtime Rig')
        self.add_submenu_command(submenu, 'Zoo Weight Save')
        self.add_submenu_command(submenu, 'rig101writeControllers')

    def _plugins_section(self) -> None:
        self.add_toolbar_command('Anim\nBot', image_path=QtWrappers.BUTTON_GREEN_40X40)
        self.add_toolbar_command('Studio\nLib', image_path=QtWrappers.BUTTON_GREEN_40X40)

        submenu = self.add_toolbar_submenu('Adv\nSkel', image_path=QtWrappers.BUTTON_GREEN_40X40)
        self.add_submenu_command(submenu, 'Main Menu')
        self.add_submenu_command(submenu, 'Biped Selector')
        self.add_submenu_command(submenu, 'Face Selector')
        self.add_submenu_command(submenu, 'Picker')

    def _anim_script_section(self) -> None:
        anim_submenu = self.add_toolbar_submenu('Anim', image_path=QtWrappers.BUTTON_ORANGE_40X40)
        self.add_submenu_command(anim_submenu, 'SPconstMaker')
        self.add_submenu_command(anim_submenu, 'KF Key Tools')
        self.add_submenu_command(anim_submenu, 'KF Attract Disperse')
        self.add_submenu_command(anim_submenu, 'KF Stream Animation')
        self.add_submenu_command(anim_submenu, 'KF Wheel Rotation')
        self.add_submenu_command(anim_submenu, 'KW Bake Keys')
        self.add_submenu_command(anim_submenu, 'KW Anim helper')
        self.add_submenu_command(anim_submenu, 'The Sato Selector')
        self.add_submenu_command(anim_submenu, 'Replace Motion Path')

        xform_submenu = self.add_toolbar_submenu('XForm', image_path=QtWrappers.BUTTON_ORANGE_40X40)
        self.add_submenu_command(xform_submenu, 'Create Placer Locator')
        self.add_submenu_command(xform_submenu, 'Random Motion')
        self.add_submenu_command(xform_submenu, 'Scatter')
        self.add_submenu_command(xform_submenu, 'Shaker')

        snappers_submenu = self.add_toolbar_submenu('Snappr', image_path=QtWrappers.BUTTON_ORANGE_40X40)
        self.add_submenu_command(snappers_submenu, 'Translate and Rotate')
        self.add_submenu_command(snappers_submenu, 'Translate Only')
        self.add_submenu_command(snappers_submenu, 'Rotate Only')
        self.add_submenu_command(snappers_submenu, 'Point and Orient Constraint')
        self.add_submenu_command(snappers_submenu, 'Point Constraint')
        self.add_submenu_command(snappers_submenu, 'Parent Constraint')
        self.add_submenu_command(snappers_submenu, 'Create Locator')
        self.add_submenu_command(snappers_submenu, 'Constraint Finder')
        self.add_submenu_command(snappers_submenu, 'Move to Pivot')
        self.add_submenu_command(snappers_submenu, 'Snap Transform to Mesh')

        motion_path_submenu = self.add_toolbar_submenu('Motn\nPath', image_path=QtWrappers.BUTTON_ORANGE_40X40)
        self.add_submenu_command(motion_path_submenu, 'Motion Path Extender')

        timer_submenu = self.add_toolbar_submenu('Time', image_path=QtWrappers.BUTTON_ORANGE_40X40)
        self.add_submenu_command(timer_submenu, 'Time Warp Tool')
        self.add_submenu_command(timer_submenu, 'Offset Animation Window')
        self.add_submenu_command(timer_submenu, 'Time Offsetter Pro Window')
        self.add_submenu_command(timer_submenu, 'KW Timer')
        self.add_submenu_command(timer_submenu, 'Set Range From Selection')

        self.add_toolbar_command('Select', image_path=QtWrappers.BUTTON_ORANGE_40X40)

    def _asset_scripts_section(self) -> None:
        model_submenu = self.add_toolbar_submenu('Anim\nScripts', QtWrappers.BUTTON_PURPLE_40X40)
        self.add_submenu_command(model_submenu, 'Poly Wireframe')
        self.add_submenu_command(model_submenu, 'Extract Face')
        self.add_submenu_command(model_submenu, 'Component Scaler')
        self.add_submenu_command(model_submenu, 'Zero Pivots')
        self.add_submenu_command(model_submenu, 'Detach Separate')
        self.add_submenu_command(model_submenu, 'Center X')
        self.add_submenu_command(model_submenu, 'Center Y')
        self.add_submenu_command(model_submenu, 'Center Z')
        self.add_submenu_command(model_submenu, 'Floor')
        self.add_submenu_command(model_submenu, 'Mirror Helper')

        texture_submenu = self.add_toolbar_submenu('Texture', QtWrappers.BUTTON_PURPLE_40X40)
        self.add_submenu_command(texture_submenu, 'Make Zoetrope')
        self.add_submenu_command(texture_submenu, 'File Texture Manager')
        self.add_submenu_command(texture_submenu, 'Gradient Card')
        self.add_submenu_command(texture_submenu, 'Edit Texture Size')

        effects_submenu = self.add_toolbar_submenu('Effects', QtWrappers.BUTTON_PURPLE_40X40)
        self.add_submenu_command(effects_submenu, 'KF Lightning Tools')
        self.add_submenu_command(effects_submenu, 'KF Tracer Emitter')
        self.add_submenu_command(effects_submenu, 'KF Sword Swipe')
        self.add_submenu_command(effects_submenu, 'SAG Instance To Geo')
        self.add_submenu_command(effects_submenu, 'Light Ribbon Window')
        self.add_submenu_command(effects_submenu, 'Disc Ribbon Window')
        self.add_submenu_command(effects_submenu, 'Ninja Fracture')

    def _measure_section(self) -> None:
        measure_submenu = self.add_toolbar_submenu('Measure', QtWrappers.BUTTON_RED_40X40)
        self.add_submenu_command(measure_submenu, 'Measure Tool')
        self.add_submenu_command(measure_submenu, 'Import Scale Model')
        self.add_submenu_command(measure_submenu, 'Speed Locator New')

    def _rename_script_section(self) -> None:
        submenu = self.add_toolbar_submenu('Rename', QtWrappers.BUTTON_RED_40X40)
        self.add_submenu_command(submenu, 'Comet Renamer')
        self.add_submenu_command(submenu,'Name Shader Networks From Selected Materials')


class TestWindow(QtWrappers.MainWindow):
    def __init__(self) -> None:
        super().__init__('Style Library Viewer',
                         (0, 0), (0, 0))
        self.toolbar = TestToolbar()
        self.setCentralWidget(self.toolbar)
        self.resize(1350, 50)


if __name__ == '__main__':
    QtWrappers.exec_app(TestWindow, 'ExampleToolbar')
