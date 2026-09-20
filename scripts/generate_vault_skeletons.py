#!/usr/bin/env python3
"""Generate Obsidian vault skeleton notes from Python sources.

Creates number-free notes (e.g. ``export_service.md``) in both vaults
(``docs/code_walkthrough`` ES + ``docs/code_walkthrough_en`` EN) using
``_template.md`` and AST-extracted metadata.

Usage:
  python scripts/generate_vault_skeletons.py --dry-run
  python scripts/generate_vault_skeletons.py --write

Pending = Python files in sec_interp/ without a vault note.
"""

from __future__ import annotations

import ast
import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VAULTS = {
    "es": ROOT / "docs" / "code_walkthrough",
    "en": ROOT / "docs" / "code_walkthrough_en",
}
TEMPLATES = {
    "es": VAULTS["es"] / "_template.md",
    "en": VAULTS["en"] / "_template.md",
}
# Scan roots (files directly under sec_interp/ + subpackages)
SCAN_DIRS = [
    ROOT / "core",
    ROOT / "gui",
    ROOT / "exporters",
]

# Map path → vault slug (filename without number)
def vault_slug_for(src: Path) -> str:
    if src.name == "__init__.py":
        return src.parent.name
    return src.stem

def layer_tag_for(src: Path) -> str:
    try:
        rel = src.relative_to(ROOT).as_posix()
    except ValueError:
        rel = src.as_posix()
    if rel.startswith("core/"):
        return "core"
    if rel.startswith("gui/"):
        return "gui"
    if rel.startswith("exporters/"):
        return "exporters"
    return "root"

def domain_tag_for(src: Path) -> str:
    name = src.stem
    if "service" in name:
        return "services"
    if "manager" in name:
        return "managers"
    if "renderer" in name:
        return "renderers"
    if "extractor" in name or "adapter" in name:
        return "adapters"
    if "validator" in name:
        return "validation"
    return "utils" if "utils" in str(src) else "general"

def extract_metadata(src: Path) -> dict:
    text = src.read_text(encoding="utf-8")
    try:
        tree = ast.parse(text)
    except SyntaxError:
        tree = None
    doc = ast.get_docstring(tree) if tree else None
    first_line = doc.strip().splitlines()[0] if doc else ""
    imports = []
    if tree:
        for node in tree.body[:12]:
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                try:
                    imports.append(ast.unparse(node))
                except Exception:
                    imports.append(ast.dump(node))
                if len(imports) >= 6:
                    break
    symbols = []
    if tree:
        for node in tree.body:
            if isinstance(node, ast.ClassDef):
                symbols.append(f"class {node.name}")
            elif isinstance(node, ast.FunctionDef):
                symbols.append(f"def {node.name}()")
            if len(symbols) >= 8:
                break
    return {
        "doc": doc or "",
        "first_line": first_line,
        "imports": "\n".join(imports) or "# (no imports)",
        "symbols": ", ".join(symbols) or "(no symbols)",
        "lines": str(len(text.splitlines())),
    }

def main() -> None:
    parser = argparse.ArgumentParser(description="Generate vault skeleton notes")
    parser.add_argument("--dry-run", action="store_true", help="List pending without writing")
    parser.add_argument("--write", action="store_true", help="Write skeleton notes")
    args = parser.parse_args()

    # Collect all Python files under SCAN_DIRS (recursive, skip __pycache__)
    all_py: list[Path] = []
    for d in SCAN_DIRS:
        if d.is_file() and d.suffix == ".py":
            all_py.append(d)
        elif d.is_dir():
            all_py.extend(p for p in d.rglob("*.py") if "__pycache__" not in p.parts)

    # Existing vault slugs (without .md)
    existing: set[str] = set()
    for vault in VAULTS.values():
        for md in vault.glob("*.md"):
            if md.name.startswith("_"):
                continue
            existing.add(md.stem)

    pending: list[Path] = []
    for src in sorted(all_py):
        slug = vault_slug_for(src)
        # Skip if a note for this slug already exists in either vault
        if slug in existing:
            continue
        # Skip tiny __init__ of packages already covered by package notes (domain, validation, etc.)
        if slug in {"domain", "validation", "adapters", "renderers", "tasks"}:
            # These packages already have notes (domain.md, validation.md, etc.)
            # Keep their __init__ out
            if src.name == "__init__.py":
                continue
        pending.append(src)

    print(f"Pending files: {len(pending)}")
    for src in pending[:30]:
        meta = extract_metadata(src)
        print(f"  {src.relative_to(ROOT)} -> {vault_slug_for(src)}.md  ({meta['lines']} lines) :: {meta['first_line'][:70]}")

    if args.dry_run:
        return

    if not args.write:
        print("\nUse --write to generate notes or --dry-run to preview.")
        return

    # Load templates
    tmpl_es = TEMPLATES["es"].read_text(encoding="utf-8")
    tmpl_en = TEMPLATES["en"].read_text(encoding="utf-8")

    for src in pending:
        slug = vault_slug_for(src)
        meta = extract_metadata(src)
        rel_path = src.relative_to(ROOT).as_posix()
        layer = layer_tag_for(src)
        domain = domain_tag_for(src)

        for lang, vault, tmpl in [("es", VAULTS["es"], tmpl_es), ("en", VAULTS["en"], tmpl_en)]:
            dst = vault / f"{slug}.md"
            if dst.exists():
                continue
            content = tmpl
            # Simple placeholder replacement (keep unknown placeholders as-is)
            replacements = {
                "{{REL_PATH}}": rel_path,
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
                "{{SUMMARY_EN}}": meta["first_line"] or "(add summary)",
                "{{PROBLEM_1}}": "(pendiente)",
                "{{SOLUTION_1}}": "(pendiente)",
                "{{PROBLEM_2}}": "(pendiente)",
                "{{SOLUTION_2}}": "(pendiente)",
                "{{ARCH_NOTE}}": "QGIS-agnóstico" if layer == "core" else "GUI adapter" if layer == "gui" else "Exporter",
                "{{OBS_1}}": meta["symbols"],
                "{{OBS_2}}": "",
                "{{MAIN_SYMBOL}}": slug,
                "{{CODE_SNIPPET}}": f"# Ver {rel_path}",
                "{{PARAM}}": "-",
                "{{ROLE}}": "-",
                "{{PATTERN}}": "-",
                "{{WHERE}}": "-",
                "{{WHY}}": "-",
                "{{SYMBOL}}": slug,
                "{{SIG}}": "-",
                "{{USE}}": "-",
                "{{STRENGTH}}": "(skeleton)",
                "{{RISK}}": "(skeleton)",
                "{{QUESTION}}": "(skeleton)",
                "{{RELATED_1}}": "Index",
                "{{WHY_1}}": "índice",
                "{{RELATED_2}}": "controller",
                "{{WHY_2}}": "orquestador",
            }
            for k, v in replacements.items():
                content = content.replace(k, v)
            dst.write_text(content, encoding="utf-8")
            print(f"wrote {dst.relative_to(ROOT)}")

if __name__ == "__main__":
    main()
