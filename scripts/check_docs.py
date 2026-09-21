#!/usr/bin/env python3
"""Documentation quality gate.

Fails (exit 1) when the *active* documentation:
  1. references Python modules that do not exist;
  2. contains broken relative links;
  3. is out of sync with its mirror copies (docs/source, vaults).

Historical records (plans, archive, releases, maintenance logs, walkthroughs,
ADRs) are intentionally skipped.

Usage:
    uv run python scripts/check_docs.py
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Directories that hold historical records, analysis or generated trees (not audited).
EXCLUDE_PARTS = {
    "archive",
    "plans",
    "releases",
    "maintenance",
    "walkthroughs",
    "adr",
    "maintainer",  # historical analyses (carry "historical document" notices)
    "qa",  # historical analyses
    "research",  # research notes
    "build",
    "locales",
    "code_walkthrough",
    "code_walkthrough_en",
    "history",
    "logs",
    "node_modules",
    ".venv",
}
# Log-style files whose links may point to pruned artifacts.
EXCLUDE_FILES = {
    "DEVELOPMENT_LOG.md",
    "CHANGELOG.md",
    "CHANGELOG_EN.md",
    "MAINTENANCE_LOG.md",
    "v250_fix_report.md",  # historical fix report
}

DOC_GLOBS = ["docs/**/*.md", "README.md", "README_DEV.md"]

# Illustrative placeholders that are not real references.
IGNORE_REFS = {"slug.md", "slug"}

_PY_REF = re.compile(r"`([A-Za-z0-9_./-]+\.py)`")
_MD_LINK = re.compile(r"\]\(([^)]+)\)")
_REGEX_META = set("*?+[](){}^$|\\")


def existing_files() -> tuple[set[str], set[str]]:
    """Return (relative paths, basenames) of all repo files, excluding caches."""
    paths: set[str] = set()
    basenames: set[str] = set()
    for p in ROOT.rglob("*"):
        if not p.is_file():
            continue
        if any(part in p.parts for part in (".venv", "build", "__pycache__", ".git")):
            continue
        paths.add(p.relative_to(ROOT).as_posix())
        basenames.add(p.name)
    return paths, basenames


def active_docs() -> list[Path]:
    """Collect the active (non-historical) documentation files."""
    docs: set[Path] = set()
    for pattern in DOC_GLOBS:
        for p in ROOT.glob(pattern):
            if p.name in EXCLUDE_FILES:
                continue
            if any(part in p.parts for part in EXCLUDE_PARTS):
                continue
            docs.add(p)
    return sorted(docs)


def check_py_refs(docs: list[Path], paths: set[str], basenames: set[str]) -> list[str]:
    """Flag references to ``.py`` modules that do not exist."""
    issues: list[str] = []
    for d in docs:
        for lineno, line in enumerate(d.read_text(encoding="utf-8", errors="ignore").splitlines(), 1):
            for ref in sorted(set(_PY_REF.findall(line))):
                if ref.split("/")[-1] in IGNORE_REFS:
                    continue
                if ref in paths or ref.split("/")[-1] in basenames:
                    continue
                issues.append(f"{d.relative_to(ROOT)}:{lineno}: missing module `{ref}`")
    return issues


def check_links(docs: list[Path]) -> list[str]:
    """Flag broken relative markdown links."""
    issues: list[str] = []
    for d in docs:
        base = d.parent
        for match in _MD_LINK.finditer(d.read_text(encoding="utf-8", errors="ignore")):
            target = match.group(1)
            if target.startswith(("http", "#", "mailto:", "file:")):
                continue
            if target in IGNORE_REFS or target.split("/")[-1] in IGNORE_REFS:
                continue
            if any(ch in target for ch in _REGEX_META):  # regex examples, not links
                continue
            resolved = (base / target.split("#")[0]).resolve()
            if not resolved.exists():
                issues.append(f"{d.relative_to(ROOT)}: broken link -> {target}")
    return issues


def check_sync() -> list[str]:
    """Ensure the mirror-sync scripts report no drift."""
    issues: list[str] = []
    for script in ("sync_docs_mirrors.sh", "sync_vault_mirrors.sh"):
        proc = subprocess.run(
            ["bash", str(ROOT / "scripts" / script), "--check"],
            capture_output=True,
            text=True,
            check=False,
        )
        if proc.returncode != 0:
            issues.append(f"{script}: mirrors out of sync\n{proc.stdout.strip()}")
    return issues


def main() -> int:
    """Run all documentation checks and return a process exit code."""
    paths, basenames = existing_files()
    docs = active_docs()
    issues = check_py_refs(docs, paths, basenames) + check_links(docs) + check_sync()
    if issues:
        print("❌ Documentation check failed:\n")
        for issue in issues:
            print(f"  - {issue}")
        print(f"\n{len(issues)} issue(s).")
        return 1
    print(f"✅ Documentation check passed ({len(docs)} active docs).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
