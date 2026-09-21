#!/usr/bin/env python3
"""Report documentation translation coverage per language.

Counts translated vs total ``msgstr`` entries in ``docs/locales/*/LC_MESSAGES/*.po``.

Usage:
    uv run python scripts/docs_i18n_status.py
    uv run python scripts/docs_i18n_status.py --min 80   # exit 1 if any lang < 80%
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LOCALES_DIR = ROOT / "docs" / "locales"

_MSGSTR = re.compile(r'^msgstr\s+"(.*)"', re.M)


def language_coverage(lang_dir: Path) -> tuple[int, int, int]:
    """Return (translated, total, files) for a language directory."""
    translated = total = files = 0
    for po_file in sorted((lang_dir / "LC_MESSAGES").glob("*.po")):
        files += 1
        for match in _MSGSTR.finditer(po_file.read_text(encoding="utf-8", errors="ignore")):
            total += 1
            if match.group(1):
                translated += 1
    return translated, total, files


def main() -> int:
    """Print the coverage table and optionally enforce a minimum."""
    min_pct = None
    if "--min" in sys.argv:
        try:
            min_pct = float(sys.argv[sys.argv.index("--min") + 1])
        except (IndexError, ValueError):
            print("Usage: docs_i18n_status.py [--min PERCENT]")
            return 2

    if not LOCALES_DIR.is_dir():
        print(f"❌ {LOCALES_DIR.relative_to(ROOT)} not found.")
        return 1

    print(f"{'lang':<8}{'translated':>12}{'total':>8}{'coverage':>10}{'files':>7}")
    below: list[str] = []
    for lang_dir in sorted(p for p in LOCALES_DIR.iterdir() if p.is_dir()):
        translated, total, files = language_coverage(lang_dir)
        pct = (translated / total * 100) if total else 0.0
        flag = ""
        if min_pct is not None and pct < min_pct:
            flag = "  ⚠️"
            below.append(lang_dir.name)
        print(f"{lang_dir.name:<8}{translated:>12}{total:>8}{pct:>9.1f}%{files:>7}{flag}")

    if min_pct is not None and below:
        print(f"\n❌ Languages below {min_pct:.0f}%: {', '.join(below)}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
