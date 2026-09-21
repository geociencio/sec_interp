#!/usr/bin/env python3
"""Sync the plugin version/date shown in the active docs with ``metadata.txt``.

``metadata.txt`` is the single source of truth for the version. This keeps the
hand-maintained headers of the active docs from drifting.

Usage:
    uv run python scripts/sync_docs_version.py          # update headers
    uv run python scripts/sync_docs_version.py --check   # exit 1 if stale
"""

from __future__ import annotations

import re
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

EXCLUDE_PARTS = {
    "archive",
    "plans",
    "releases",
    "maintenance",
    "walkthroughs",
    "adr",
    "maintainer",
    "qa",
    "research",
    "build",
    "locales",
    "code_walkthrough",
    "code_walkthrough_en",
    "history",
    "logs",
    "node_modules",
    ".venv",
}

DOC_GLOBS = ["docs/**/*.md", "README.md", "README_DEV.md"]


def read_version() -> str:
    """Read the plugin version from ``metadata.txt``."""
    text = (ROOT / "metadata.txt").read_text(encoding="utf-8")
    match = re.search(r"^version\s*=\s*(.+)$", text, re.M)
    return match.group(1).strip() if match else "0.0.0"


def sync_text(text: str, version: str, today: str, refresh_date: bool = True) -> str:
    """Return ``text`` with version (and optionally date) headers synced.

    ``refresh_date=False`` (used by ``--check``) only compares the version, so
    the informational "Last Updated" date does not fail the gate every day.
    """
    for sep in ("Last Updated: ", "Last update: "):
        if refresh_date:
            text = re.sub(
                rf"(> Version )\d+\.\d+\.\d+( \| {sep})(\d{{4}}-\d{{2}}-\d{{2}})",
                rf"\g<1>{version}\g<2>{today}",
                text,
            )
        else:
            text = re.sub(
                rf"(> Version )\d+\.\d+\.\d+( \| {sep})(\d{{4}}-\d{{2}}-\d{{2}})",
                rf"\g<1>{version}\g<2>\g<3>",
                text,
            )
    text = re.sub(r"(\*\*Plugin Version\*\*: )\d+\.\d+\.\d+", rf"\g<1>{version}", text)
    text = re.sub(r"(\*\*Version\*\*: )\d+\.\d+\.\d+", rf"\g<1>{version}", text)
    return text


def active_docs() -> list[Path]:
    """Collect the active (non-historical) documentation files."""
    docs: set[Path] = set()
    for pattern in DOC_GLOBS:
        for p in ROOT.glob(pattern):
            if any(part in p.parts for part in EXCLUDE_PARTS):
                continue
            docs.add(p)
    return sorted(docs)


def main() -> int:
    """Sync or verify version headers and return a process exit code."""
    check = "--check" in sys.argv
    version = read_version()
    today = date.today().isoformat()
    stale: list[Path] = []

    for doc in active_docs():
        text = doc.read_text(encoding="utf-8")
        updated = sync_text(text, version, today, refresh_date=not check)
        if updated != text:
            stale.append(doc)
            if not check:
                doc.write_text(updated, encoding="utf-8")

    if stale and check:
        print("❌ Stale version headers (run: make docs-version):")
        for doc in stale:
            print(f"  - {doc.relative_to(ROOT)}")
        return 1

    if stale:
        print(f"✓ Updated version headers in {len(stale)} doc(s) to {version}.")
    else:
        print(f"✓ Version headers up to date ({version}).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
