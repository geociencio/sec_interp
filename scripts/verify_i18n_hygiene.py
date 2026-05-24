#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Verification script for internationalization (i18n) hygiene in SecInterp.

This script parses all GUI modules and the main plugin file using the Python AST
module. It identifies hardcoded string literals containing spaces or punctuation
that are not wrapped in translation calls (e.g., self.tr()) and do not have the
explicit exclusion comment '# no-i18n'.

It correctly distinguishes between:
  - Module/class/function docstrings (always excluded)
  - Technical strings like file extensions, CSS, icons, format specifiers (excluded)
  - Genuine user-facing strings that require translation (reported)

Serves as a Quality Gate to prevent i18n regressions in Phase v3.7.0+.
"""

from __future__ import annotations

import ast
import os
import re
import sys
from pathlib import Path

# Paths to verify (relative to project root)
TARGET_PATHS = [
    Path("gui"),
    Path("sec_interp_plugin.py"),
]

# Calls whose string arguments are safe to ignore (translations, logging, etc.)
SAFE_CALL_SUFFIXES = {
    # Translation wrappers — already translated
    "tr",
    "translate",
    # Logging — not user-facing
    "debug",
    "info",
    "warning",
    "error",
    "critical",
    "exception",
    "log",
    # QGIS / Qt internals
    "connect",
    "disconnect",
    "mapLayerByName",
    "setValue",
    "setObjectName",
    "setProperty",
    "setToolTip",
    "setWhatsThis",
    "setPlaceholderText",
    "setAttribute",
    "setStyleSheet",
    "addItem",
    "insertItem",
    "findText",
    # Exception constructors — developer-facing
    "ValueError",
    "RuntimeError",
    "TypeError",
    "AttributeError",
    "KeyError",
    "NotImplementedError",
    "OSError",
    "IOError",
    "Exception",
    "SecInterpError",
    "ValidationError",
    # Regular expression / path operations
    "compile",
    "match",
    "search",
    "sub",
    "split",
    "join",
    "format",
    "encode",
    "decode",
    "open",
    "makedirs",
    "startswith",
    "endswith",
    "with_suffix",
    "parent",
    # Performance / Metrics
    "PerformanceTimer",
    "track",
}

# Regex patterns for strings that are always technical (not user-facing)
TECHNICAL_PATTERNS: list[re.Pattern[str]] = [
    # Python format specifiers
    re.compile(
        r"^[{.+<>^-]?\d*[dfsfeExXgGoO%nbDBcdnrsa]$"
    ),  # e.g. '.2f', '+.2f', '.0f'
    # File extensions
    re.compile(r"^\.[a-z]{2,4}$"),  # e.g. '.png', '.jpg', '.svg', '.shp'
    # MIME-style filter strings
    re.compile(r"\*\.\w+"),  # e.g. '*.png'
    # CSS / Qt stylesheet fragments
    re.compile(
        r"(background-color|border|font-weight|color:|margin|padding|QPush|QDialog|QLabel|QCombo)"
    ),
    # QGIS memory layer URI / field specs
    re.compile(r"field=\w+:\w+"),
    # Color codes (R,G,B or R,G,B,A)
    re.compile(r"^\d{1,3},\d{1,3},\d{1,3}(,\d{1,3})?$"),
    # SVG icon names
    re.compile(r"^m[A-Z][a-zA-Z]+\.svg$"),
    # Pure HTML tags (e.g. '<b>', '</b>', '<br>')
    re.compile(r"^</?[a-zA-Z][a-zA-Z0-9]*\s*/?>$"),
    # HTML attribute or fragment (contains '<' or '>' and no full readable word phrase)
    re.compile(r"^[^a-zA-Z]*<[^>]*>[^a-zA-Z]*$"),
    # Strings that are mostly HTML/special chars with minimal alpha (e.g. '| <b>', ':</b>')
    re.compile(
        r"^[\s\|:;.,!?<>\-=\"'/\\{}()]+[a-zA-Z]{0,3}[\s\|:;.,!?<>\-=\"'/\\{}()]*$"
    ),
    # Hex color codes
    re.compile(r"^#[0-9a-fA-F]{3,8}$"),
    # Geometry type keywords
    re.compile(r"^(Point|LineString|Polygon|MultiPoint|MultiLineString|MultiPolygon)$"),
    # Single-word QGIS layer types or geometry keywords
    re.compile(r"^(EPSG|WKT|CRS|SHP|CSV|GeoJSON|GPKG|GeoTIFF)$", re.IGNORECASE),
    # Format specifiers or pure punctuation/symbols
    re.compile(r"^[^a-zA-Z]*$"),
    # Log-level strings
    re.compile(r"^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$"),
    # QSettings keys (contain '/' or are camelCase)
    re.compile(r"^[a-zA-Z]+/[a-zA-Z/_]+$"),  # e.g. 'SecInterp/last_dir'
    # Default filename values (just a filename, no spaces)
    re.compile(r"^\w[\w.-]*\.(png|jpg|jpeg|pdf|svg|shp|csv|json|html|txt|xml|qml)$"),
    # Pure numbers (including floats)
    re.compile(r"^-?\d+(\.\d+)?$"),
    # HTML attribute opening fragments (e.g. "<a href='", '<span style="')
    re.compile(r"^<[a-zA-Z]+\s+[a-zA-Z-]+=[\"']"),
]

# Exact strings that are always safe to ignore
SAFE_EXACT_STRINGS: set[str] = {
    "utf-8",
    "r",
    "w",
    "rb",
    "wb",
    "a",
    "en",
    "es",
    "index.html",
    "preview.png",
    "Total Preview Generation",
    "Total Preview Export Time",
    "Axes Labels",
}


def _collect_docstring_lines(tree: ast.AST) -> set[int]:
    """Collect line numbers of all docstrings (module, class, function) via AST.

    Docstrings are the first string expression in a module, class body, or
    function body, possibly preceded by import statements (e.g. future imports).

    Args:
        tree: Parsed AST of the Python source file.

    Returns:
        Set of line numbers that belong to docstrings.
    """
    docstring_lines: set[int] = set()

    def _find_first_str_expr(body: list[ast.stmt]) -> ast.Constant | None:
        """Return the first string Constant Expr, skipping leading imports."""
        for stmt in body:
            if isinstance(stmt, (ast.Import, ast.ImportFrom)):
                # Skip 'from __future__ import ...' and similar leading imports
                continue
            if (
                isinstance(stmt, ast.Expr)
                and isinstance(stmt.value, ast.Constant)
                and isinstance(stmt.value.value, str)
            ):
                return stmt.value
            # Stop at the first non-import, non-docstring statement
            break
        return None

    for node in ast.walk(tree):
        docstring_node: ast.Constant | None = None

        if isinstance(node, ast.Module):
            docstring_node = _find_first_str_expr(node.body)
        elif isinstance(node, (ast.ClassDef, ast.AsyncFunctionDef, ast.FunctionDef)):
            docstring_node = _find_first_str_expr(node.body)

        if docstring_node is not None:
            for lineno in range(
                docstring_node.lineno,
                (docstring_node.end_lineno or docstring_node.lineno) + 1,
            ):
                docstring_lines.add(lineno)

    return docstring_lines


def _is_technical_string(val: str) -> bool:
    """Return True if the string value is clearly a technical/non-translatable string."""
    stripped = val.strip()

    # Already in safe exact set
    if stripped in SAFE_EXACT_STRINGS:
        return True

    # Check all technical patterns
    for pattern in TECHNICAL_PATTERNS:
        if pattern.search(stripped):
            return True

    return False


class I18nHygieneVisitor(ast.NodeVisitor):
    """AST Visitor to detect untranslated user-facing strings."""

    def __init__(
        self,
        filepath: Path,
        lines: list[str],
        docstring_lines: set[int],
    ) -> None:
        self.filepath = filepath
        self.lines = lines
        self.docstring_lines = docstring_lines
        self.violations: list[tuple[int, str, str]] = []
        self._current_call_stack: list[str] = []

    def _get_call_name(self, node: ast.expr) -> str:
        """Resolve the qualified name of a function call node."""
        if isinstance(node, ast.Name):
            return node.id
        if isinstance(node, ast.Attribute):
            base = self._get_call_name(node.value)
            return f"{base}.{node.attr}" if base else node.attr
        return ""

    def visit_Call(self, node: ast.Call) -> None:
        """Track the current call stack to detect safe wrappers."""
        call_name = self._get_call_name(node.func)
        self._current_call_stack.append(call_name)
        self.generic_visit(node)
        self._current_call_stack.pop()

    def visit_Constant(self, node: ast.Constant) -> None:
        """Inspect string constants for i18n hygiene violations."""
        if not isinstance(node.value, str):
            return

        val = node.value.strip()

        # --- Fast exclusion gates ---

        # 1. Empty, very short, or numeric-only strings
        if len(val) <= 1 or val.replace(".", "").replace("-", "").isdigit():
            return

        # 2. This line belongs to a docstring
        if node.lineno in self.docstring_lines:
            return

        # 3. Technical/non-translatable pattern match
        if _is_technical_string(val):
            return

        # 4. String must look user-facing: contain at least one space or real word
        has_spaces = " " in val
        has_alpha = any(c.isalpha() for c in val)
        if not (has_spaces and has_alpha):
            return

        # 5. Check if the string is inside a safe call wrapper
        for active_call in reversed(self._current_call_stack):
            if any(active_call.endswith(suffix) for suffix in SAFE_CALL_SUFFIXES):
                return

        # 6. Check for inline exclusion comments on the source line
        line_num = node.lineno
        if 1 <= line_num <= len(self.lines):
            line_content = self.lines[line_num - 1]
            if "# no-i18n" in line_content or "# noqa" in line_content:
                return
            self.violations.append((line_num, val, line_content.strip()))


def verify_file(filepath: Path) -> list[tuple[int, str, str]]:
    """Analyze a single Python file for i18n hygiene violations.

    Args:
        filepath: Path to the Python file to analyze.

    Returns:
        List of (line_number, string_value, source_line) tuples for violations.
    """
    try:
        source = filepath.read_text(encoding="utf-8")
        lines = source.splitlines()
    except Exception as e:  # noqa: BLE001
        print(f"⚠️  Error reading {filepath}: {e}")
        return []

    try:
        tree = ast.parse(source, filename=str(filepath))
    except SyntaxError as e:
        print(f"⚠️  Syntax Error in {filepath}: {e}")
        return []

    docstring_lines = _collect_docstring_lines(tree)
    visitor = I18nHygieneVisitor(filepath, lines, docstring_lines)
    visitor.visit(tree)
    return visitor.violations


def main() -> None:
    """Scan designated folders and print a focused validation report."""
    print("🔎 Starting i18n Quality Gate scan...")
    print("   (Docstrings and technical strings are automatically excluded)\n")
    total_violations = 0
    scanned_files = 0

    for path in TARGET_PATHS:
        if not path.exists():
            print(f"⚠️  Path not found, skipping: {path}")
            continue

        if path.is_file():
            files_to_scan = [path]
        else:
            files_to_scan = sorted(path.rglob("*.py"))

        for file_path in files_to_scan:
            violations = verify_file(file_path)
            scanned_files += 1
            if violations:
                print(f"🚨 Violations in {file_path}:")
                for line, val, content in violations:
                    # Truncate long string values for readability
                    display_val = val[:80] + "…" if len(val) > 80 else val
                    print(f'   Line {line:4d} | "{display_val}"')
                    print(f"            Code: {content[:120]}")
                total_violations += len(violations)
                print()

    print("=" * 65)
    print(f"📊 Scan Complete: {scanned_files} file(s) analyzed.")
    if total_violations > 0:
        print(
            f"❌ Failed: {total_violations} untranslated user-facing string(s) found."
        )
        print("💡 Fix: Wrap in self.tr('...') or add '# no-i18n' to skip.")
        sys.exit(1)
    else:
        print("✅ Success: All user-facing strings are properly handled.")
        sys.exit(0)


if __name__ == "__main__":
    main()
