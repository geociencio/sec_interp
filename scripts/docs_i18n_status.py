#!/usr/bin/env python3
"""Report documentation translation coverage per language.

Counts translated vs total message entries in ``docs/locales/*/LC_MESSAGES/*.po``
using Babel (handles multi-line strings correctly).

The published-language policy uses ``USER_GUIDE.po`` coverage (>= 80%).

Usage:
    uv run python scripts/docs_i18n_status.py
    uv run python scripts/docs_i18n_status.py --min 80   # exit 1 if USER_GUIDE < 80%
"""

from __future__ import annotations

import sys
from pathlib import Path

from babel.messages import pofile

ROOT = Path(__file__).resolve().parent.parent
LOCALES_DIR = ROOT / "docs" / "locales"
PUBLISH_THRESHOLD = 80.0


def po_stats(po_file: Path) -> tuple[int, int]:
    """Return (translated, total) message entries for a .po file."""
    if not po_file.exists():
        return 0, 0
    with po_file.open("rb") as handle:
        catalog = pofile.read_po(handle)
    translated = total = 0
    for message in catalog:
        if not message.id:
            continue
        total += 1
        if message.string:
            translated += 1
    return translated, total


def language_coverage(lang_dir: Path) -> tuple[float, float, int]:
    """Return (overall %, user_guide %, files) for a language directory."""
    translated = total = files = 0
    for po_file in sorted((lang_dir / "LC_MESSAGES").glob("*.po")):
        files += 1
        t, n = po_stats(po_file)
        translated += t
        total += n
    overall = (translated / total * 100) if total else 0.0
    ug_t, ug_n = po_stats(lang_dir / "LC_MESSAGES" / "USER_GUIDE.po")
    ug = (ug_t / ug_n * 100) if ug_n else 0.0
    return overall, ug, files


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

    print(f"{'lang':<8}{'overall':>9}{'user_guide':>12}{'files':>7}   published")
    below: list[str] = []
    for lang_dir in sorted(p for p in LOCALES_DIR.iterdir() if p.is_dir()):
        overall, ug, files = language_coverage(lang_dir)
        published = "yes" if ug >= PUBLISH_THRESHOLD else "no"
        flag = ""
        if min_pct is not None and lang_dir.name != "en" and ug < min_pct:
            flag = "  ⚠️"
            below.append(lang_dir.name)
        print(f"{lang_dir.name:<8}{overall:>8.1f}%{ug:>11.1f}%{files:>7}   {published}{flag}")

    if min_pct is not None and below:
        print(f"\n❌ Languages below {min_pct:.0f}% USER_GUIDE coverage: {', '.join(below)}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
