#!/usr/bin/env python3
"""
Documentation translation helper.
Translates Sphinx .po files using reference master data or AI assistance.
"""

import os
import sys
from pathlib import Path


def compile_catalogs():
    """Compile .po files to .mo files."""
    print("🛠️  Compiling documentation catalogs...")
    locales_dir = Path("docs/locales")
    if not locales_dir.exists():
        print("Error: docs/locales directory not found.")
        return

    # Find all .po files
    po_files = list(locales_dir.glob("**/LC_MESSAGES/*.po"))
    if not po_files:
        print("No .po files found.")
        return

    for po_file in po_files:
        mo_file = po_file.with_suffix(".mo")
        # uv run msgfmt docs/locales/es/LC_MESSAGES/USER_GUIDE.po -o docs/locales/es/LC_MESSAGES/USER_GUIDE.mo
        print(f"  - Compiling {po_file.relative_to(locales_dir)}...")
        os.system(f"msgfmt {po_file} -o {mo_file}")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "compile":
        compile_catalogs()
    else:
        print("Usage: translate_docs.py compile")
        # Future: add AI translation logic here
