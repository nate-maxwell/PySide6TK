# PySide6TK
A library of PySide6 helpers + stylesheets specifically for Windows development.

# Remember!

When adding to the toolkit, be sure to run `PySide6TK._generate_namespace.py`
to rebuild the `PySide6TK.QtWrappers.py` file before pushing updates.

## Namespaces

Wrapper objects and helper methods can be imported similarly to how PySide
namespaces are usually handled:

```python
from PySide6TK import QtWrappers

class Foo(QtWrappers.MainWindow):
    def __init__(self) -> None:
        super().__init__('example window')
        self.wid = QtWrappers.GroupBox('test box')
        self.setCentralWidget(self.wid)
```

## Wrappers

Wrapper methods will always be snake_case, i.e. if a widget has methods to
add widgets or layouts, it will be `widget.add_widget(wid)`,
`layout.add_stretch()`, or `widget.add_layout(lay)`, which will be shorthand
for `widget.layout.addWidget(wid)`, etc. If those methods are not present, the
wrappers do not exist for that class.

Properties are not used to keep the workflow / coding style similar to actual
PySide. Use `object.value()` or  `object.get_value()` and 
`object.set_value(val)`.

## Resources

`PySide6TK.icons` contains path variables to the stored icons while
`PySide6TK.styles` contains path variables to stored stylesheets. All of which
can also be gotten from `PySide6TK.QtWrappers`.

## Stylesheet Viewer

Run `PSToolkit._example.style_viewer` file itself, to see an example widget
that displays all the collected style sheets.

<img src="https://i.imgur.com/DePm39f.png">
