#!/usr/bin/env python3
"""Generate the file-to-note map for the SecInterp Code Walkthrough **v2** vault.

Builds ``project_structure_links.md`` in ``docs/code_walkthrough_v2/`` (ES) and
``docs/code_walkthrough_en_v2/`` (EN): one row per plugin-owned Python file with
a wikilink to the vault note documenting it. Unlike ``project_structure*.md``
(verbatim mirrors of ``docs/structure/``), this document is vault-owned and may
contain ``[[wikilinks]]``.

Usage:
  uv run python scripts/generate_structure_links.py --write
  uv run python scripts/generate_structure_links.py --check
"""

from __future__ import annotations

import argparse
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import generate_vault_v2 as g  # noqa: E402  (shared slug/tier logic)

VAULTS = {
    "es": ROOT / "docs" / "code_walkthrough_v2",
    "en": ROOT / "docs" / "code_walkthrough_en_v2",
}
FILENAME = "project_structure_links.md"

GROUP_ORDER = ["core", "gui", "exporters", "plugin", "resources", "root"]


def build_file_map() -> dict[str, tuple[str, str, int]]:
    """Return rel_path -> (slug, tier, lines) for every plugin-owned file."""
    srcs = g.collect_sources()
    tiers: dict[str, list[tuple[Path, int]]] = {"A": [], "B": [], "C": []}
    for src in srcs:
        lines = len(src.read_text(encoding="utf-8").splitlines())
        tiers[g.tier_of(lines)].append((src, lines))

    slug_map = g.resolve_individual_slugs(tiers["A"] + tiers["B"])
    groups: dict[str, list[tuple[Path, int]]] = defaultdict(list)
    for src, lines in tiers["C"]:
        groups[src.parent.relative_to(g.ROOT).as_posix()].append((src, lines))
    group_slugs = g.resolve_group_slugs(set(slug_map.values()), list(groups))

    file_map: dict[str, tuple[str, str, int]] = {}
    for tier in ("A", "B"):
        for src, lines in tiers[tier]:
            rel = src.relative_to(g.ROOT).as_posix()
            file_map[rel] = (slug_map[src.as_posix()], tier, lines)
    for pkg, files in groups.items():
        for src, lines in files:
            rel = src.relative_to(g.ROOT).as_posix()
            file_map[rel] = (group_slugs[pkg], "C", lines)
    return file_map


def top_group(rel: str) -> str:
    head = rel.split("/")[0]
    if head in ("core", "gui", "exporters", "plugin", "resources"):
        return head
    return "root"


def render(file_map: dict[str, tuple[str, str, int]], lang: str) -> str:
    if lang == "es":
        title = "# SecInterp — Mapa archivo → nota (bóveda v2)"
        intro = (
            "> Cada archivo Python del plugin con un enlace wiki a la nota de la "
            "bóveda que lo documenta. A diferencia de `project_structure*.md` "
            "(espejos de `docs/structure/`), este documento es propio de la bóveda y "
            "sus enlaces son navegables en Obsidian.\n>\n"
            "> Los archivos Tier C (< 50 líneas) comparten la nota de su paquete."
        )
        cols = "| Archivo | Líneas | Tier | Nota |"
        sep = "|---|--:|:---:|---|"
    else:
        title = "# SecInterp — File → note map (v2 vault)"
        intro = (
            "> Every plugin Python file with a wiki link to the vault note "
            "documenting it. Unlike `project_structure*.md` (mirrors of "
            "`docs/structure/`), this document is vault-owned and its links are "
            "navigable in Obsidian.\n>\n"
            "> Tier C files (< 50 lines) share their package note."
        )
        cols = "| File | Lines | Tier | Note |"
        sep = "|---|--:|:---:|---|"
    section_names = {
        "core": "core/",
        "gui": "gui/",
        "exporters": "exporters/",
        "plugin": "plugin/",
        "resources": "resources/",
        "root": "root",
    }
    lines = [title, "", intro, ""]
    by_group: dict[str, list[str]] = defaultdict(list)
    for rel in file_map:
        by_group[top_group(rel)].append(rel)
    for grp in GROUP_ORDER:
        rels = sorted(by_group.get(grp, []))
        if not rels:
            continue
        lines.append(f"## `{section_names[grp]}` ({len(rels)})")
        lines.append("")
        lines.append(cols)
        lines.append(sep)
        for rel in rels:
            slug, tier, nlines = file_map[rel]
            lines.append(f"| `{rel}` | {nlines} | {tier} | [[{slug}]] |")
        lines.append("")
    lines.append(f"*Vault-owned map — regenerate with `scripts/{Path(__file__).name} --write`.*")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate the v2 vault file-to-note map")
    parser.add_argument("--write", action="store_true", help="Write the documents")
    parser.add_argument("--check", action="store_true", help="Fail if documents differ")
    args = parser.parse_args()

    file_map = build_file_map()
    print(f"Mapped {len(file_map)} files.")
    if not (args.write or args.check):
        for rel in sorted(file_map)[:10]:
            print(f"  {rel} -> [[{file_map[rel][0]}]] ({file_map[rel][1]})")
        print("  ...")
        print("\nUse --write to generate or --check to verify.")
        return 0

    failed = False
    for lang, vault in VAULTS.items():
        content = render(file_map, lang)
        dst = vault / FILENAME
        if args.check:
            if not dst.is_file() or dst.read_text(encoding="utf-8") != content:
                print(f"❌ {dst.relative_to(ROOT)} differs; run --write.")
                failed = True
            else:
                print(f"✓ up-to-date {dst.relative_to(ROOT)}")
        else:
            dst.write_text(content, encoding="utf-8")
            print(f"Wrote {dst.relative_to(ROOT)}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
