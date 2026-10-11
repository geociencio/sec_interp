"""Static guard: the plugin must stay importable and runnable on Python 3.9.

QGIS bundles its own interpreter, and that is still Python 3.9 well past the
plugin's 3.28 minimum - QGIS 3.42 ships 3.9. The test suite runs on 3.12, so
nothing here is caught at runtime: a PEP 604 union inside isinstance() imports
cleanly on CI and raises TypeError on a real QGIS install. That is exactly how
``isinstance(value, int | float | ...)`` shipped and broke every feature read.
"""

import ast
import os

PLUGIN_DIR = os.path.join(os.path.dirname(__file__), "..", "qgis_mcp_plugin")


def _plugin_sources():
    """Every plugin source file, including the handler subpackage.

    Walks the tree rather than listing one directory: the handlers moved into
    ``qgis_mcp_plugin/handlers/`` and a non-recursive listing skipped them
    silently, which is the worst possible failure for a guard like this - most
    of the command code would have gone unchecked while the tests stayed green.
    """
    for root, dirs, files in os.walk(PLUGIN_DIR):
        dirs[:] = sorted(d for d in dirs if d != "__pycache__")
        for name in sorted(files):
            if name.endswith(".py"):
                path = os.path.join(root, name)
                label = os.path.relpath(path, PLUGIN_DIR).replace(os.sep, "/")
                with open(path, encoding="utf-8") as fh:
                    yield label, fh.read()


def _has_future_annotations(tree):
    return any(
        isinstance(node, ast.ImportFrom)
        and node.module == "__future__"
        and any(a.name == "annotations" for a in node.names)
        for node in tree.body
    )


def test_no_pep604_unions_in_isinstance():
    """`isinstance(x, A | B)` is a TypeError on Python 3.9."""
    offenders = []
    for name, src in _plugin_sources():
        for node in ast.walk(ast.parse(src)):
            if (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Name)
                and node.func.id in ("isinstance", "issubclass")
                and len(node.args) == 2
                and isinstance(node.args[1], ast.BinOp)
                and isinstance(node.args[1].op, ast.BitOr)
            ):
                offenders.append(f"{name}:{node.lineno}")
    assert not offenders, (
        "PEP 604 union inside isinstance/issubclass - raises TypeError on the "
        f"Python 3.9 QGIS bundles. Use the tuple form. Found at: {offenders}"
    )


def test_no_runtime_evaluated_pep604_annotations():
    """Function signatures are evaluated at import; `X | Y` there breaks 3.9.

    Only flagged for modules without ``from __future__ import annotations``,
    which defers evaluation and makes the syntax safe.
    """
    offenders = []
    for name, src in _plugin_sources():
        tree = ast.parse(src)
        if _has_future_annotations(tree):
            continue
        for node in ast.walk(tree):
            if not isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
                continue
            annotations = [a.annotation for a in node.args.args if a.annotation]
            annotations += [a.annotation for a in node.args.kwonlyargs if a.annotation]
            if node.returns is not None:
                annotations.append(node.returns)
            for ann in annotations:
                if isinstance(ann, ast.BinOp) and isinstance(ann.op, ast.BitOr):
                    offenders.append(f"{name}:{node.lineno} ({node.name})")
    assert not offenders, (
        "PEP 604 union in a signature of a module lacking "
        f"`from __future__ import annotations` - fails to import on 3.9: {offenders}"
    )

    # keyword arguments added to builtins after 3.9 -> "takes no keyword arguments"


NEWER_THAN_39_KWARGS = {
    "zip": {"strict"},
}


def test_no_post_39_builtin_keyword_arguments():
    """`zip(a, b, strict=True)` raises TypeError on 3.9.

    Not a syntax error and not an import error - it fails only when that line
    executes, which is why `set_layer_order` and `set_raster_style` shipped
    broken while the suite stayed green on 3.12.
    """
    offenders = []
    for name, src in _plugin_sources():
        for node in ast.walk(ast.parse(src)):
            if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Name):
                continue
            banned = NEWER_THAN_39_KWARGS.get(node.func.id)
            if not banned:
                continue
            for kw in node.keywords:
                if kw.arg in banned:
                    offenders.append(f"{name}:{node.lineno} {node.func.id}({kw.arg}=)")
    assert not offenders, (
        "builtin keyword argument newer than Python 3.9 - TypeError on the "
        f"interpreter QGIS bundles. Found: {offenders}"
    )


def test_plugin_modules_parse_under_py39_grammar():
    """Nothing in the plugin may use syntax newer than 3.9 (e.g. match/case)."""
    for name, src in _plugin_sources():
        tree = ast.parse(src)
        for node in ast.walk(tree):
            assert not isinstance(node, ast.Match), (
                f"{name}: match/case statement requires Python 3.10; QGIS ships 3.9"
            )
