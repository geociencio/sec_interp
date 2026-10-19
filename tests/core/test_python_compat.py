"""Static Python 3.9 compatibility gate for the plugin runtime.

QGIS 3.28 (our declared minimum) ships Python 3.9 on Windows/OSGeo4W. The
plugin must not use syntax or runtime constructs introduced in 3.10+:

- ``match`` statements (3.10)
- ``isinstance(x, int | float)`` (PEP 604 at runtime, 3.10)
- ``zip(..., strict=...)`` (3.10)
- ``typing.Self`` / ``TypeAlias`` / ``TypeGuard`` (3.10/3.11)
- PEP 604 annotations without ``from __future__ import annotations``
"""

import ast
import unittest
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
_PLUGIN_DIRS = ("core", "gui", "exporters", "plugin")
_ROOT_MODULES = ("sec_interp_plugin.py", "logger_config.py", "__init__.py")


def _plugin_files() -> list[Path]:
    files: list[Path] = []
    for directory in _PLUGIN_DIRS:
        files.extend(sorted((_ROOT / directory).rglob("*.py")))
    files.extend(_ROOT / name for name in _ROOT_MODULES if (_ROOT / name).exists())
    return files


def _has_future_annotations(tree: ast.Module) -> bool:
    for node in tree.body:
        if isinstance(node, ast.ImportFrom) and node.module == "__future__":
            if any(alias.name == "annotations" for alias in node.names):
                return True
    return False


def _contains_bit_or(node: ast.AST) -> bool:
    return any(
        isinstance(child, ast.BinOp) and isinstance(child.op, ast.BitOr)
        for child in ast.walk(node)
    )


def _annotations(tree: ast.Module):
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.returns is not None:
                yield node.returns
            args = [*node.args.posonlyargs, *node.args.args, *node.args.kwonlyargs]
            args += [arg for arg in (node.args.vararg, node.args.kwarg) if arg]
            for arg in args:
                if arg.annotation is not None:
                    yield arg.annotation
        elif isinstance(node, ast.AnnAssign):
            yield node.annotation


class TestPython39Compatibility(unittest.TestCase):
    """The plugin package must remain importable on Python 3.9."""

    def test_no_match_statements(self):
        offenders = []
        for path in _plugin_files():
            tree = ast.parse(path.read_text(encoding="utf-8"))
            if any(isinstance(node, ast.Match) for node in ast.walk(tree)):
                offenders.append(str(path.relative_to(_ROOT)))
        self.assertEqual(offenders, [], f"match statements require Python 3.10: {offenders}")

    def test_isinstance_uses_tuples(self):
        offenders = []
        for path in _plugin_files():
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if not isinstance(node, ast.Call):
                    continue
                if not (isinstance(node.func, ast.Name) and node.func.id == "isinstance"):
                    continue
                if len(node.args) >= 2 and _contains_bit_or(node.args[1]):
                    offenders.append(f"{path.relative_to(_ROOT)}:{node.lineno}")
        self.assertEqual(
            offenders,
            [],
            f"isinstance(x, A | B) requires Python 3.10: {offenders}",
        )

    def test_zip_has_no_strict_keyword(self):
        offenders = []
        for path in _plugin_files():
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if not isinstance(node, ast.Call):
                    continue
                if not (isinstance(node.func, ast.Name) and node.func.id == "zip"):
                    continue
                if any(keyword.arg == "strict" for keyword in node.keywords):
                    offenders.append(f"{path.relative_to(_ROOT)}:{node.lineno}")
        self.assertEqual(
            offenders,
            [],
            f"zip(strict=...) requires Python 3.10: {offenders}",
        )

    def test_union_annotations_have_future_import(self):
        offenders = []
        for path in _plugin_files():
            tree = ast.parse(path.read_text(encoding="utf-8"))
            if _has_future_annotations(tree):
                continue
            if any(_contains_bit_or(annotation) for annotation in _annotations(tree)):
                offenders.append(str(path.relative_to(_ROOT)))
        self.assertEqual(
            offenders,
            [],
            f"PEP 604 annotations need 'from __future__ import annotations': {offenders}",
        )

    def test_no_typing_310_imports(self):
        forbidden = {"Self", "TypeAlias", "TypeGuard", "ParamSpec", "Required", "NotRequired"}
        offenders = []
        for path in _plugin_files():
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom) and node.module == "typing":
                    names = {alias.name for alias in node.names} & forbidden
                    if names:
                        offenders.append(f"{path.relative_to(_ROOT)}:{node.lineno} {sorted(names)}")
        self.assertEqual(offenders, [], f"Python 3.10+ typing imports: {offenders}")


if __name__ == "__main__":
    unittest.main()
