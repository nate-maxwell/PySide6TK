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

        
if __name__ == '__main__':
    QtWrapers.exec_app(Foo, 'Foo')
```

Optionally, these same items can be gotten from like so:
```python
from PySide6TK.groupbox import GroupBox
from PySide6TK.main_window import MainWindow

class Foo(MainWindow):
    def __init__(self) -> None:
        super().__init__('example window')
        self.wid = GroupBox('test box')
        self.setCentralWidget(self.wid)
```

## Wrappers

### Methods
Wrapper methods will always be `snake_case`, i.e. if a widget has methods to
add widgets or layouts, it will be `widget.add_widget(wid)`,
`layout.add_stretch()`, or `widget.add_layout(lay)`, which will be shorthand
for `widget.layout.addWidget(wid)`, etc.

Snake case is chosen to signify wrapper vs native PySide methods.

If those methods are not present, the namespace shorteners do not exist for
that class.

### Getters / Setters
Properties are not used to keep the workflow / coding style similar to actual
PySide. Use `object.value()` or  `object.get_value()` and 
`object.set_value(val)`.

### Constructors
If able, widgets follow the following constructor pattern for standardized organization:
```python
def __init__(self) -> None:
    super().__init__()
    self._create_widgets()
    self._create_layout()
    self._create_connections()
```
Simpler widgets may forgo this pattern, but more component heavy wrappers are
organized this way.

## Resources

`PySide6TK.icons` contains path variables to the stored icons while
`PySide6TK.styles` contains path variables to stored stylesheets. All of which
can also be gotten from `PySide6TK.QtWrappers`.

## Examples

### Code Snippets and Example Windows
PySide6TK._examples is full of example files of code snippets along with
`__name__ == '__main__'` idiom blocks to launch an example window showcasing
the widget.

### Stylesheet Viewer
Run `PSToolkit._example.style_viewer` file itself, to see an example widget
that displays all the collected style sheets.

<img src="https://i.imgur.com/DePm39f.png">
