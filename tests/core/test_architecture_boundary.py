"""Architecture boundary gate: enforce Extract-then-Compute in ``core/``.

This test is the executable enforcement of ``core/AGENTS.md`` absolute
constraints. It scans ``sec_interp/core/`` for forbidden QGIS coupling and
fails if the coupling is not explicitly allowlisted (a regression), or if an
allowlist entry is now clean (forcing the list to shrink as files are
migrated).

Forbidden patterns
------------------
- ``qgis.core``    -> real geometry/layer/project coupling (violation)
- ``qgis.gui``     -> GUI coupling (never allowed in core)
- ``qgis.PyQt``    -> Qt shim (gray area: ``tr()`` / enum compat)
- ``QgsProject.instance()`` -> singleton global state (violation)

How to shrink the allowlist
---------------------------
When a file is migrated to be QGIS-agnostic, remove its entry (or the offending
pattern) from :data:`CORE_VIOLATIONS`. The stale-entry test will guide you: it
fails when an allowlist entry no longer matches the file, so the entry must be
removed. The forbidden-imports test fails when a file acquires a new violation
not present in the allowlist, so regressions are caught immediately.

The target is an empty ``CORE_VIOLATIONS`` mapping.
"""

from __future__ import annotations

import re
from pathlib import Path

from tests.base_test import BaseTestCase

# Repo root is two levels above this file (tests/core/ -> repo root).
_CORE_DIR = Path(__file__).resolve().parents[2] / "core"

_FORBIDDEN_PATTERNS: dict[str, re.Pattern[str]] = {
    "qgis.core": re.compile(r"\b(?:from|import)\s+qgis\.core\b"),
    "qgis.gui": re.compile(r"\b(?:from|import)\s+qgis\.gui\b"),
    "qgis.PyQt": re.compile(r"\b(?:from|import)\s+qgis\.PyQt\b"),
    "QgsProject.instance()": re.compile(r"QgsProject\.instance\(\)"),
}

# Allowlist of current violations: relative path -> frozenset of patterns.
# Each entry MUST be removed once the file is migrated to be QGIS-agnostic.
CORE_VIOLATIONS: dict[str, frozenset[str]] = {
    "config.py": frozenset({"qgis.core", "qgis.PyQt"}),
    "data_cache.py": frozenset({"qgis.PyQt"}),
    "services/access_control_service.py": frozenset({"qgis.core"}),
    "services/export_service.py": frozenset({"qgis.core", "qgis.PyQt"}),
    "utils/i18n.py": frozenset({"qgis.PyQt"}),
    "utils/io.py": frozenset({"qgis.core", "QgsProject.instance()"}),
}


def _scan_core() -> dict[str, frozenset[str]]:
    """Return actual forbidden-pattern violations per core file."""
    violations: dict[str, frozenset[str]] = {}
    for file_path in sorted(_CORE_DIR.rglob("*.py")):
        rel = file_path.relative_to(_CORE_DIR).as_posix()
        text = file_path.read_text(encoding="utf-8")
        hits = frozenset(
            name for name, pattern in _FORBIDDEN_PATTERNS.items() if pattern.search(text)
        )
        if hits:
            violations[rel] = hits
    return violations


class TestArchitectureBoundary(BaseTestCase):
    """Enforce the core layer's QGIS-agnostic boundary."""

    def test_forbidden_imports_are_allowlisted(self) -> None:
        """No core file may have a QGIS coupling outside the allowlist."""
        actual = _scan_core()
        new_violations: list[str] = []
        for rel, patterns in actual.items():
            unexpected = patterns - CORE_VIOLATIONS.get(rel, frozenset())
            if unexpected:
                new_violations.append(f"{rel}: {sorted(unexpected)} (not allowlisted)")
        self.assertEqual(
            [],
            new_violations,
            "Core files acquired forbidden QGIS coupling not in the allowlist. "
            "Either revert the change or migrate the file to be QGIS-agnostic.",
        )

    def test_allowlist_has_no_stale_entries(self) -> None:
        """Allowlist entries must be removed once a file is migrated."""
        actual = _scan_core()
        stale: list[str] = []
        for rel, patterns in CORE_VIOLATIONS.items():
            remaining = patterns - actual.get(rel, frozenset())
            if remaining:
                stale.append(f"{rel}: {sorted(remaining)} (now clean, remove entry)")
        self.assertEqual(
            [],
            stale,
            "Allowlist entries no longer match the file; remove them to shrink "
            "the allowlist toward an empty mapping.",
        )

    def test_core_dir_exists(self) -> None:
        """Sanity check that the scanner targets the real core directory."""
        self.assertTrue(_CORE_DIR.is_dir())
        self.assertGreater(len(list(_CORE_DIR.rglob("*.py"))), 0)
