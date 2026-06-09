"""
# __init__.py Generator

* Description:

    Traverses all subdirectories in the same folder as this script and
    generates an __init__.py for each one, importing all public classes,
    functions, and constants from that subdirectory's Python files.

    Can be run at any time by a developer to regenerate namespace files.
"""

import ast
import sys
from pathlib import Path
from typing import Iterable

import PySide6TK


package_name = PySide6TK.MODULE_NAME


def _is_private(name: str) -> bool:
    return name.startswith("_")


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


def generate_imports_from_directory(directory_: str | Path, base_path: Path) -> str:
    """Generate 'from <module> import <item>' statements for all public symbols.

    Args:
        directory_ (str | Path): Path to the subdirectory to scan.
        base_path (Path): The root package path used to build module names.

    Returns:
        str: A newline-separated string of import statements.
    """
    scan_path = Path(directory_).resolve()
    import_lines: list[str] = []
    seen: set[str] = set()

    for py_file in scan_path.rglob("*.py"):
        if py_file.name in ("__init__.py", "_generate_namespace.py"):
            continue

        rel_path = py_file.relative_to(base_path)
        if "_examples" in rel_path.as_posix():
            continue

        module_name = ".".join(rel_path.with_suffix("").parts)

        try:
            source = py_file.read_text(encoding="utf-8")
            tree = ast.parse(source, filename=str(py_file))
        except (OSError, SyntaxError):
            continue

        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                name = node.name
                if not _is_private(name):
                    line = f"from {package_name}.{module_name} import {name}"
                    if line not in seen:
                        seen.add(line)
                        import_lines.append(line)

        for node in tree.body:
            if isinstance(node, ast.Assign):
                for tgt in node.targets:
                    for name in _extract_assigned_names(tgt):
                        if _is_constant(name):
                            line = f"from {package_name}.{module_name} import {name}"
                            if line not in seen:
                                seen.add(line)
                                import_lines.append(line)

            elif isinstance(node, ast.AnnAssign):
                if isinstance(node.target, ast.Name):
                    name = node.target.id
                    if _is_constant(name):
                        line = f"from {package_name}.{module_name} import {name}"
                        if line not in seen:
                            seen.add(line)
                            import_lines.append(line)

    import_lines.sort(key=lambda s: s.lower())
    return "\n".join(import_lines)


def main() -> int:
    script_dir = Path(__file__).resolve().parent

    subdirs = [
        p for p in script_dir.iterdir() if p.is_dir() and not p.name.startswith("_")
    ]

    for subdir in subdirs:
        imports = generate_imports_from_directory(subdir, script_dir)
        if not imports:
            continue

        init_file = subdir / "__init__.py"
        with init_file.open("w", encoding="utf-8") as f:
            f.write(imports)
            f.write("\n")

        print(f"Generated: {init_file.relative_to(script_dir)}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
