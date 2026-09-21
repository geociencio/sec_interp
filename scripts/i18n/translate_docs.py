#!/usr/bin/env python3
"""Documentation translation helper.

Subcommands:
    compile   Compile .po catalogs to .mo (used by build_docs.sh).
    update    Extract .pot from the docs and sync the .po catalogs
              (``sphinx-build -b gettext`` + ``sphinx-intl update``).
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

LOCALES = ["en", "es", "fr", "pt_BR", "de", "ru", "zh_CN", "id", "it", "pl", "nl", "fi", "hi", "ja"]
SOURCE_DIR = "docs/source"
POT_DIR = "docs/build/gettext"
LOCALES_DIR = "docs/locales"

# Only user-facing pages are translated; the autodoc pages (sec_interp.*) and
# historical docs stay in English.
USER_FACING = {
    "USER_GUIDE",
    "ARCHITECTURE",
    "DEVELOPMENT_GUIDE",
    "CORE_DISTINCTION_GUIDE",
    "CORE_DISTINCTION_GUIDE_EN",
    "TECHNICAL_COMPENDIUM",
    "MAINTENANCE_LOG",
}


def compile_catalogs() -> None:
    """Compile .po files to .mo files."""
    print("🛠️  Compiling documentation catalogs...")
    locales_dir = Path(LOCALES_DIR)
    if not locales_dir.exists():
        print("Error: docs/locales directory not found.")
        return

    po_files = list(locales_dir.glob("**/LC_MESSAGES/*.po"))
    if not po_files:
        print("No .po files found.")
        return

    for po_file in po_files:
        mo_file = po_file.with_suffix(".mo")
        print(f"  - Compiling {po_file.relative_to(locales_dir)}...")
        os.system(f"msgfmt {po_file} -o {mo_file}")


def update_catalogs(locales: list[str] | None = None) -> None:
    """Extract the .pot and sync the .po catalogs with the current docs."""
    locales = locales or LOCALES
    print("📥 Extracting translatable strings (gettext)...")
    subprocess.run(
        ["uv", "run", "sphinx-build", "-b", "gettext", SOURCE_DIR, POT_DIR],
        check=True,
    )

    # Keep only the user-facing catalogs so we don't create thousands of empty
    # entries for the autodoc pages.
    pot_dir = Path(POT_DIR)
    for pot in pot_dir.glob("*.pot"):
        if pot.stem not in USER_FACING:
            pot.unlink()
    print(f"    Kept user-facing catalogs: {', '.join(sorted(USER_FACING))}")

    print(f"🔄 Updating catalogs for: {' '.join(locales)}")
    cmd = ["uv", "run", "sphinx-intl", "update", "-p", POT_DIR, "-d", LOCALES_DIR]
    for lang in locales:
        cmd += ["-l", lang]
    subprocess.run(cmd, check=True)
    print("✅ Catalogs updated (obsolete entries pruned, new msgids added).")


def main() -> int:
    """Dispatch the requested subcommand."""
    if len(sys.argv) > 1 and sys.argv[1] == "compile":
        compile_catalogs()
        return 0
    if len(sys.argv) > 1 and sys.argv[1] == "update":
        update_catalogs(sys.argv[2:] or None)
        return 0
    print("Usage: translate_docs.py {compile|update [LOCALE ...]}")
    return 2


if __name__ == "__main__":
    sys.exit(main())
