# PSToolkit
A library of PySide helpers + stylesheets.

Currently, PySide 6 compatible.

### Stylesheet Viewer

Run `QtToolkit.stylesheets._example_viewer.main()`, or the file itself, to see
an example widget that displays all the collected style sheets.

<img src="https://i.imgur.com/DePm39f.png">

### Wrappers

Wrapper methods will always be snake_case, i.e. if a widget has methods to
add widgets or layouts, it will be `widget.add_widget(wid)`,
`layout.add_stretch()`, or `widget.add_layout(lay)`, which will be shorthand
for `widget.layout.addWidget(wid)`, etc. If those methods are not present, the
wrappers do not exist for that class.

### Resources

`QtToolkit.gui` contains path variables to the stored icons and stylesheets.
