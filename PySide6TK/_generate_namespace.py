"""
# QtWrappers.py File Generator

* Description:

    This generates the namespace file QtWrappers.py - It can be run at any time
    by a developer to create the PySide like namespaces.
"""


import ast
import sys
from pathlib import Path
from typing import Iterable

import PySide6TK


module_doc = '''"""
!! Remember to run PySide6TK._generate_namespace.py to create this regenerate
this file before pushing updates!!

# QtWrappers

* Description:

    A similar namespace to PySide6 allowing more natural usage along the
    PySide6 framework.

    Example:
        >>> from PySide6TK import QtWrappers
        >>>
        >>> class Foo(QtWrappers.MainWindow):
        >>>     ...
"""
'''
package_name = PySide6TK.MODULE_NAME


def _is_private(name: str) -> bool:
    return name.startswith('_')


def _is_constant(name: str) -> bool:
    return name.isupper() and not _is_private(name)


def _extract_assigned_names(target: ast.AST) -> Iterable[str]:
    """Yield variable names from assignment targets
    (supports a, b = ... and [a, b] = ...).
    """
    if isinstance(target, ast.Name):
        yield target.id
    elif isinstance(target, (ast.Tuple, ast.List)):
        for elt in target.elts:
            yield from _extract_assigned_names(elt)


def generate_imports_from_directory(directory_: str | Path) -> str:
    """Generate 'from <module> import <item>' statements for all functions and classes.

    Args:
        directory_: Path to a directory containing Python files.

    Returns:
        A newline-separated string of import statements.
    """
    base_path = Path(directory_).resolve()
    import_lines: list[str] = []
    seen: set[str] = set()

    for py_file in base_path.rglob('*.py'):
        blocked = ['__init__.py', 'QtWrappers.py', '_generate_namespace.py']
        if py_file.name in blocked:
            continue

        rel_path = py_file.relative_to(base_path)
        if '_examples' in rel_path.as_posix():
            continue
        module_name = '.'.join(rel_path.with_suffix('').parts)

        try:
            source = py_file.read_text(encoding='utf-8')
            tree = ast.parse(source, filename=str(py_file))
        except (OSError, SyntaxError):
            continue

        # --- classes & functions ---
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef,
                                 ast.ClassDef)):
                name = node.name
                if not _is_private(name):
                    line = f'from {package_name}.{module_name} import {name}'
                    if line not in seen:
                        seen.add(line)
                        import_lines.append(line)

        # --- constants / module variables (top-level assigns) ---
        for node in tree.body:
            # Simple assignment: X = 1, A, B = (1, 2)
            if isinstance(node, ast.Assign):
                for tgt in node.targets:
                    for name in _extract_assigned_names(tgt):
                        if _is_constant(name):
                            line = f'from {package_name}.{module_name} import {name}'
                            if line not in seen:
                                seen.add(line)
                                import_lines.append(line)

            # Annotated assignment: X: int = 1  or  X: int
            elif isinstance(node, ast.AnnAssign):
                # Only handle simple `Name` targets at top-level
                if isinstance(node.target, ast.Name):
                    name = node.target.id
                    if _is_constant(name):
                        line = f'from {package_name}.{module_name} import {name}'
                        if line not in seen:
                            seen.add(line)
                            import_lines.append(line)

    import_lines.sort(key=lambda s: s.lower())
    return '\n'.join(import_lines)


def main() -> int:
    p = Path(__file__).parent

    contents = module_doc
    contents += '\n'
    contents += '\n'
    contents += generate_imports_from_directory(p)
    contents += '\n'

    with Path(p, 'QtWrappers.py').open('w', encoding='utf-8') as f:
        f.write(contents)

    return 0


if __name__ == '__main__':
    sys.exit(main())
