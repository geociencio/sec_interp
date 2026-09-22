#!/usr/bin/env python3
"""Generate the SecInterp Code Walkthrough **v2** vault (bilingual, complete).

Creates skeleton notes for every plugin-owned Python file (``core/``, ``gui/``,
``exporters/``, ``plugin/``, ``resources/`` and the root entry points) into the
**new** vaults ``docs/code_walkthrough_v2/`` (ES) and
``docs/code_walkthrough_en_v2/`` (EN). The existing v1 vaults are never touched.

Files are tiered by size so trivial modules (``__init__.py``, short interfaces)
are grouped into one package note while substantive files get their own note:

- Tier A (>= 100 lines) -> individual note (target 400-500 lines)
- Tier B (50-99 lines)  -> individual note (target ~300-400 lines)
- Tier C (< 50 lines)   -> grouped into one note per package directory

Usage:
  uv run python scripts/generate_vault_v2.py --dry-run
  uv run python scripts/generate_vault_v2.py --write
"""

from __future__ import annotations

import argparse
import ast
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VAULTS = {
    "es": ROOT / "docs" / "code_walkthrough_v2",
    "en": ROOT / "docs" / "code_walkthrough_en_v2",
}
TEMPLATES = {
    "es": VAULTS["es"] / "_template.md",
    "en": VAULTS["en"] / "_template.md",
}
SCAN_DIRS = ["core", "gui", "exporters", "plugin", "resources"]
ROOT_PY = ["__init__.py", "logger_config.py", "run_qgis_manage.py", "sec_interp_plugin.py"]

TIER_A_MIN = 100
TIER_B_MIN = 50

# High-importance modules allowed to exceed the 500-line note ceiling (up to 700).
# These are orchestrators/composition roots that legitimately document to ~500-650 lines.
HIGH_IMPORTANCE = {
    "sec_interp_plugin.py",
    "core/controller.py",
    "core/services/drillhole_service.py",
    "core/services/preview_service.py",
    "core/services/export/orchestrator.py",
    "gui/main_dialog.py",
    "gui/dialog_preview_manager.py",
    "gui/preview_renderer.py",
    "gui/preview_layer_factory.py",
    "gui/preview_task_orchestrator.py",
}
HIGH_IMPORTANCE_CEILING = 700


def collect_sources() -> list[Path]:
    """Return every plugin-owned Python file (deduplicated)."""
    srcs: list[Path] = []
    seen: set[str] = set()
    for name in ROOT_PY:
        p = ROOT / name
        if p.is_file():
            srcs.append(p)
            seen.add(p.as_posix())
    for d in SCAN_DIRS:
        base = ROOT / d
        if not base.is_dir():
            continue
        for p in sorted(base.rglob("*.py")):
            if "__pycache__" in p.parts or p.as_posix() in seen:
                continue
            srcs.append(p)
            seen.add(p.as_posix())
    return sorted(srcs)


def tier_of(lines: int) -> str:
    if lines >= TIER_A_MIN:
        return "A"
    if lines >= TIER_B_MIN:
        return "B"
    return "C"


def slug_for(src: Path) -> str:
    """Base slug: file stem, or parent dir name for ``__init__.py``."""
    return src.parent.name if src.name == "__init__.py" else src.stem


def package_slug_for(src: Path) -> str:
    """Unambiguous slug for a Tier C package group note."""
    rel = src.parent.relative_to(ROOT).as_posix()
    return rel.replace("/", "_").replace(".", "_")


def resolve_individual_slugs(sources: list[tuple[Path, int]]) -> dict[str, str]:
    """Map source path -> unique slug, disambiguating stem collisions."""
    by_slug: defaultdict[str, list[tuple[Path, int]]] = defaultdict(list)
    for src, lines in sources:
        by_slug[slug_for(src)].append((src, lines))
    resolved: dict[str, str] = {}
    for slug, items in by_slug.items():
        if len(items) == 1:
            resolved[items[0][0].as_posix()] = slug
            continue
        for src, _lines in sorted(items):
            rel = src.relative_to(ROOT).as_posix().replace("/", "_").replace(".", "_")
            resolved[src.as_posix()] = rel
    return resolved


def layer_tag_for(src: Path) -> str:
    rel = src.relative_to(ROOT).as_posix()
    if rel.startswith("core/"):
        return "core"
    if rel.startswith("gui/"):
        return "gui"
    if rel.startswith("exporters/"):
        return "exporters"
    if rel.startswith("plugin/"):
        return "plugin"
    return "root"


def domain_tag_for(src: Path) -> str:
    name = src.stem
    if "service" in name:
        return "services"
    if "manager" in name:
        return "managers"
    if "renderer" in name:
        return "renderers"
    if "extractor" in name or "adapter" in name or "fetcher" in name:
        return "adapters"
    if "validator" in name:
        return "validation"
    if "processor" in name or "engine" in name:
        return "processors"
    if "exporter" in name:
        return "exporters"
    return "utils" if "utils" in src.as_posix() else "general"


def _sig(node: ast.AST) -> str:
    """Best-effort signature string for a function or class."""
    try:
        return ast.unparse(node).split("\n")[0]
    except Exception:
        return ""


def _walk_symbols(tree: ast.AST) -> tuple[list[str], list[str], list[str]]:
    """Return (classes, functions, constants) as formatted strings."""
    classes: list[str] = []
    functions: list[str] = []
    constants: list[str] = []
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            methods = [n.name for n in node.body if isinstance(n, ast.FunctionDef)]
            classes.append(f"`class {node.name}` — {len(methods)} métodos")
            for m in node.body:
                if isinstance(m, ast.FunctionDef):
                    functions.append(f"`{node.name}.{m.name}({_sig(m)})`")
        elif isinstance(node, ast.FunctionDef):
            functions.append(f"`{node.name}({_sig(node)})`")
        elif isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Name) and t.id.isupper():
                    constants.append(f"`{t.id}`")
    return classes, functions, constants


def extract_metadata(src: Path) -> dict:
    text = src.read_text(encoding="utf-8")
    try:
        tree = ast.parse(text)
    except SyntaxError:
        tree = None
    doc = ast.get_docstring(tree) if tree else None
    first_line = doc.strip().splitlines()[0] if doc else ""
    imports: list[str] = []
    if tree:
        for node in tree.body[:10]:
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                try:
                    imports.append(ast.unparse(node))
                except Exception:
                    imports.append(ast.dump(node))
                if len(imports) >= 8:
                    break
    classes, functions, constants = _walk_symbols(tree) if tree else ([], [], [])
    # public functions for the method-walkthrough section
    public_funcs: list[tuple[str, str]] = []
    if tree:
        for node in tree.body:
            if isinstance(node, ast.FunctionDef) and not node.name.startswith("_"):
                public_funcs.append((node.name, _sig(node)))
    inventory_lines: list[str] = []
    if classes:
        inventory_lines.append("**Clases:** " + "; ".join(classes))
    if constants:
        inventory_lines.append("**Constantes:** " + ", ".join(constants))
    if functions:
        inventory_lines.append("**Funciones/Métodos:**")
        for f in functions:
            inventory_lines.append(f"- {f}")
    return {
        "doc": doc or "",
        "first_line": first_line,
        "imports": "\n".join(imports) or "# (no imports)",
        "inventory": "\n".join(inventory_lines) or "(sin símbolos)",
        "public_funcs": public_funcs,
        "symbols": ", ".join(f"`{n}`" for n, _ in public_funcs) or "(no symbols)",
        "lines": str(len(text.splitlines())),
    }


_SKELETON_RE = re.compile(
    r"\(pendiente\)|\(pending\)|\(skeleton\)|\(añadir resumen\)|\(add summary\)|\(enriquecer",
    re.IGNORECASE,
)


def _is_skeleton(path: Path) -> bool:
    """Return True if the note still contains placeholder markers."""
    return bool(_SKELETON_RE.search(path.read_text(encoding="utf-8")))


def file_inventory_table(files: list[tuple[Path, int]], lang: str) -> str:
    """Build a Markdown table enumerating every file in a package group."""
    file_col = "Archivo" if lang == "es" else "File"
    lines_col = "Líneas" if lang == "es" else "Lines"
    role_col = "Rol" if lang == "es" else "Role"
    rows = [f"| {file_col} | {lines_col} | {role_col} |", "|---|--:|---|"]
    for src, ln in sorted(files):
        role = extract_metadata(src)["first_line"] or "—"
        rows.append(f"| `{src.name}` | {ln} | {role} |")
    return "\n".join(rows)


def render_skeleton(
    tmpl: str,
    src: Path,
    meta: dict,
    tier: str,
    lang: str,
    file_inventory: str = "",
) -> str:
    rel_path = src.relative_to(ROOT).as_posix()
    slug = slug_for(src)
    layer = layer_tag_for(src)
    domain = domain_tag_for(src)
    if not file_inventory:
        file_inventory = (
            f"- `{src.name}` — nota individual de este archivo."
            if lang == "es"
            else f"- `{src.name}` — individual note for this file."
        )
    if rel_path in HIGH_IMPORTANCE:
        note_lines = f"note_lines: {HIGH_IMPORTANCE_CEILING}"
    else:
        hint = "opcional: tope > 500 para módulos de importancia alta (máx 700)"
        if lang == "en":
            hint = "optional: ceiling > 500 for high-importance modules (max 700)"
        note_lines = f"# note_lines: {HIGH_IMPORTANCE_CEILING}      # {hint}"
    replacements = {
        "{{REL_PATH}}": rel_path,
        "{{NOTE_LINES}}": note_lines,
        "{{FILE_BASENAME}}": src.name,
        "{{CLASS_NAME}}": slug,
        "{{LAYER}}": layer,
        "{{LAYER_TAG}}": layer,
        "{{DOMAIN_TAG}}": domain,
        "{{LINES}}": meta["lines"],
        "{{MODULE}}": slug,
        "{{FILE}}": src.name,
        "{{IMPORT_BLOCK}}": meta["imports"],
        "{{ONE_LINE_SUMMARY}}": meta["first_line"] or "(añadir resumen)",
        "{{STRUCTURE_INVENTORY}}": meta["inventory"],
        "{{FILE_INVENTORY}}": file_inventory,
        "{{M1_NAME}}": "método_1" if lang == "es" else "method_1",
        "{{M1_CODE}}": "# (enriquecer)",
        "{{M1_PROSE}}": "_(enriquecer leyendo el fuente)_",
        "{{M2_NAME}}": "método_2" if lang == "es" else "method_2",
        "{{M2_CODE}}": "# (enriquecer)",
        "{{M2_PROSE}}": "_(enriquecer leyendo el fuente)_",
        "{{FLOW_PHASE_1}}": "-",
        "{{FLOW_IN_1}}": "-",
        "{{FLOW_TRANSFORM_1}}": "-",
        "{{FLOW_OUT_1}}": "-",
        "{{FLOW_PHASE_2}}": "-",
        "{{FLOW_IN_2}}": "-",
        "{{FLOW_TRANSFORM_2}}": "-",
        "{{FLOW_OUT_2}}": "-",
        "{{PATTERN}}": "-",
        "{{WHERE}}": "-",
        "{{WHY}}": "-",
        "{{SYMBOL}}": meta["symbols"],
        "{{SIG}}": "-",
        "{{USE}}": "-",
        "{{ERROR_HANDLING}}": "_(pendiente)_" if lang == "es" else "_(pending)_",
        "{{TESTS}}": "_(pendiente)_" if lang == "es" else "_(pending)_",
        "{{PROBLEM_1}}": "(pendiente)" if lang == "es" else "(pending)",
        "{{SOLUTION_1}}": "(pendiente)" if lang == "es" else "(pending)",
        "{{PROBLEM_2}}": "(pendiente)" if lang == "es" else "(pending)",
        "{{SOLUTION_2}}": "(pendiente)" if lang == "es" else "(pending)",
        "{{ARCH_NOTE}}": "QGIS-agnóstico" if layer == "core" else "GUI adapter" if layer == "gui" else "Exporter",
        "{{OBS_1}}": "(pendiente)" if lang == "es" else "(pending)",
        "{{OBS_2}}": "(pendiente)" if lang == "es" else "(pending)",
        "{{STRENGTH}}": "(skeleton)",
        "{{RISK}}": "(skeleton)",
        "{{QUESTION}}": "(skeleton)",
        "{{RELATED_1}}": "Index",
        "{{WHY_1}}": "índice" if lang == "es" else "index",
        "{{RELATED_2}}": "controller",
        "{{WHY_2}}": "orquestador" if lang == "es" else "orchestrator",
    }
    for k, v in replacements.items():
        tmpl = tmpl.replace(k, v)
    return tmpl


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate SecInterp v2 vault skeletons")
    parser.add_argument("--dry-run", action="store_true", help="List plan without writing")
    parser.add_argument("--write", action="store_true", help="Write skeleton notes")
    parser.add_argument(
        "--layer",
        choices=["core", "gui", "exporters", "plugin", "root", "all"],
        default="all",
        help="Only generate notes for one layer (default: all)",
    )
    args = parser.parse_args()

    srcs = collect_sources()
    if args.layer != "all":
        srcs = [s for s in srcs if layer_tag_for(s) == args.layer]
    tiers: dict[str, list[tuple[Path, int]]] = {"A": [], "B": [], "C": []}
    for src in srcs:
        lines = len(src.read_text(encoding="utf-8").splitlines())
        tiers[tier_of(lines)].append((src, lines))

    print(f"Sources: {len(srcs)} total")
    print(f"  Tier A (>= {TIER_A_MIN}): {len(tiers['A'])}")
    print(f"  Tier B ({TIER_B_MIN}-{TIER_A_MIN - 1}): {len(tiers['B'])}")
    print(f"  Tier C (< {TIER_B_MIN}): {len(tiers['C'])}")

    # Tier C -> group by package dir
    groups: dict[str, list[tuple[Path, int]]] = defaultdict(list)
    for src, lines in tiers["C"]:
        groups[src.parent.relative_to(ROOT).as_posix()].append((src, lines))
    print(f"  Tier C groups: {len(groups)}")

    if args.dry_run:
        print("\nTier A preview:")
        for src, lines in tiers["A"][:15]:
            print(f"  {src.relative_to(ROOT)} -> {slug_for(src)}.md ({lines} l.)")
        return

    if not args.write:
        print("\nUse --write to generate or --dry-run to preview.")
        return

    tmpl_es = TEMPLATES["es"].read_text(encoding="utf-8")
    tmpl_en = TEMPLATES["en"].read_text(encoding="utf-8")

    written = 0
    # Tier A + B -> individual notes (with collision-safe slugs)
    individual = tiers["A"] + tiers["B"]
    slug_map = resolve_individual_slugs(individual)
    for tier in ("A", "B"):
        for src, _lines in tiers[tier]:
            meta = extract_metadata(src)
            final_slug = slug_map[src.as_posix()]
            for lang, vault, tmpl in (("es", VAULTS["es"], tmpl_es), ("en", VAULTS["en"], tmpl_en)):
                dst = vault / f"{final_slug}.md"
                if dst.exists() and not _is_skeleton(dst):
                    continue
                dst.write_text(render_skeleton(tmpl, src, meta, tier, lang), encoding="utf-8")
            written += 1
    # Tier C -> one note per package
    for pkg, files in sorted(groups.items()):
        src = files[0][0]
        meta = extract_metadata(src)
        names = ", ".join(f"`{f.stem}`" for f, _ in sorted(files))
        for lang, vault, tmpl in (("es", VAULTS["es"], tmpl_es), ("en", VAULTS["en"], tmpl_en)):
            dst = vault / f"{package_slug_for(src)}.md"
            if dst.exists() and not _is_skeleton(dst):
                continue
            inventory = file_inventory_table(files, lang)
            content = render_skeleton(tmpl, src, meta, "C", lang, file_inventory=inventory)
            summary = (
                f"Paquete `{pkg}/` ({len(files)} archivos): {names}"
                if lang == "es"
                else f"Package `{pkg}/` ({len(files)} files): {names}"
            )
            content = content.replace(meta["first_line"] or "(añadir resumen)", summary)
            dst.write_text(content, encoding="utf-8")
        written += 1

    print(f"Wrote {written} notes (per vault).")


if __name__ == "__main__":
    main()
