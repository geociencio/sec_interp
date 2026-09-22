#!/usr/bin/env python3
"""Note-size and completeness gate for the SecInterp Code Walkthrough **v2** vault.

Validates ``docs/code_walkthrough_v2/`` (ES) and ``docs/code_walkthrough_en_v2/`` (EN):

1. **Hard cap** — no note may exceed 500 lines by default. High-importance notes
   may declare ``note_lines: <n>`` in their frontmatter to raise the ceiling up to the
   absolute maximum of 700 lines.
2. **Completeness** — a note without placeholders must reach the minimum for its tier
   (Tier A/C: 400 lines, Tier B: 300 lines). Skeleton notes (with placeholders) are
   tolerated unless ``--strict`` is passed.
3. **No stale placeholders** — ``--strict`` fails on any leftover ``(pendiente)`` /
   ``(pending)`` / ``(skeleton)`` / ``(enriquecer...)`` marker.
4. **Slug parity** — ES and EN vaults expose the exact same note set.

Usage:
  uv run python scripts/check_notes.py            # report + warn on skeletons
  uv run python scripts/check_notes.py --strict   # fail on any skeleton
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import generate_vault_v2 as g  # noqa: E402  (shared slug/tier logic)

VAULTS = {
    "es": ROOT / "docs" / "code_walkthrough_v2",
    "en": ROOT / "docs" / "code_walkthrough_en_v2",
}
SKIP_STEMS = {
    "_template",
    "Index",
    "ARCHITECTURE_EN",
    "ARCHITECTURE_MONOLITHIC_VS_CLEAN_EN",
    "PLUGIN_REPORT_AND_COMPARISON_EN",
    "project_structure",
    "project_structure_table",
}

MAX_LINES = 500
MAX_ABS_LINES = 700  # absolute ceiling even for high-importance notes
MIN_LINES = {"A": 400, "B": 300, "C": 400}

NOTE_LINES_RE = re.compile(r"^note_lines:\s*(\d+)\s*$", re.MULTILINE)

PLACEHOLDER_RE = re.compile(
    r"\(pendiente\)|\(pending\)|\(skeleton\)|\(añadir resumen\)|\(add summary\)|\(enriquecer[^)]*\)|_\(pendiente\)_|_\(pending\)_",
    re.IGNORECASE,
)


def frontmatter_note_lines(text: str) -> int | None:
    """Return the per-note ceiling declared in frontmatter, or None.

    Only the first frontmatter block (the leading ``---`` block) is considered.
    """
    parts = text.split("\n---")
    if len(parts) < 2:
        return None
    match = NOTE_LINES_RE.search(parts[0])
    return int(match.group(1)) if match else None


def build_expectations() -> dict[str, str]:
    """Return slug -> tier for every note the generator is expected to produce."""
    srcs = g.collect_sources()
    tiers: dict[str, list[tuple[Path, int]]] = {"A": [], "B": [], "C": []}
    for src in srcs:
        lines = len(src.read_text(encoding="utf-8").splitlines())
        tiers[g.tier_of(lines)].append((src, lines))

    slug_tier: dict[str, str] = {}
    slug_map = g.resolve_individual_slugs(tiers["A"] + tiers["B"])
    for tier in ("A", "B"):
        for src, _lines in tiers[tier]:
            slug_tier[slug_map[src.as_posix()]] = tier

    groups: set[str] = {g.package_slug_for(src) for src, _ in tiers["C"]}
    for slug in groups:
        slug_tier[slug] = "C"
    return slug_tier


def vault_notes(vault: Path) -> dict[str, Path]:
    return {md.stem: md for md in vault.glob("*.md") if md.stem not in SKIP_STEMS}


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the v2 vault notes")
    parser.add_argument("--strict", action="store_true", help="Fail on skeletons/placeholders")
    args = parser.parse_args()

    expectations = build_expectations()
    notes = {lang: vault_notes(v) for lang, v in VAULTS.items()}

    errors: list[str] = []
    warnings: list[str] = []
    placeholder_count = 0

    # Slug parity
    es_slugs = set(notes["es"])
    en_slugs = set(notes["en"])
    if es_slugs != en_slugs:
        errors.append(f"slug parity mismatch: ES-only {sorted(es_slugs - en_slugs)}, EN-only {sorted(en_slugs - es_slugs)}")

    # Per-note checks
    for lang, vault_notes_map in notes.items():
        for slug, path in sorted(vault_notes_map.items()):
            text = path.read_text(encoding="utf-8")
            lines = text.count("\n") + 1
            has_placeholder = bool(PLACEHOLDER_RE.search(text))
            tier = expectations.get(slug)
            ceiling = frontmatter_note_lines(text) or MAX_LINES

            if ceiling > MAX_ABS_LINES:
                errors.append(f"{path.relative_to(ROOT)}: note_lines={ceiling} exceeds absolute max {MAX_ABS_LINES}")

            if lines > ceiling:
                errors.append(f"{path.relative_to(ROOT)}: {lines} lines > ceiling {ceiling}")

            if has_placeholder:
                placeholder_count += 1
                warnings.append(f"{path.relative_to(ROOT)}: skeleton (placeholder detected)")
                if args.strict:
                    errors.append(f"{path.relative_to(ROOT)}: placeholder present in --strict mode")
                continue

            if tier is None:
                warnings.append(f"{path.relative_to(ROOT)}: not in the expected note set")
                continue

            minimum = MIN_LINES[tier]
            if lines < minimum:
                errors.append(f"{path.relative_to(ROOT)}: {lines} lines < {minimum} (tier {tier})")

    for w in warnings:
        print(f"⚠️  {w}")
    if errors:
        print("\n❌ Vault note gate failed:")
        for e in errors:
            print(f"  - {e}")
        print(f"\n{len(errors)} error(s).")
        return 1

    total = sum(len(n) for n in notes.values())
    print(f"✅ Vault note gate passed — {total} notes, {placeholder_count} skeleton(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
