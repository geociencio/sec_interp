#!/usr/bin/env bash
# Sync mirror architecture/report docs and structure docs into the code-walkthrough vaults.
# Keeps wikilinks ([[ARCHITECTURE_EN]], [[project_structure_table]], …) resolvable in Obsidian.
#
# - Architecture/report mirrors -> all vaults (v1 + v2, ES + EN).
# - Structure docs (project_structure*.md/txt) -> v2 vaults only (v1 is frozen).
#
# Usage:
#   bash scripts/sync_vault_mirrors.sh
#   bash scripts/sync_vault_mirrors.sh --check   # exit 1 if out of sync

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"

# Architecture/report mirrors (source: docs/).
DOCS=(
  "ARCHITECTURE_EN.md"
  "ARCHITECTURE_MONOLITHIC_VS_CLEAN_EN.md"
  "PLUGIN_REPORT_AND_COMPARISON_EN.md"
)
VAULTS=(
  "docs/code_walkthrough"
  "docs/code_walkthrough_en"
  "docs/code_walkthrough_v2"
  "docs/code_walkthrough_en_v2"
)

# Structure docs (source: docs/structure/) -> v2 vaults only.
STRUCTURE_DOCS=(
  "project_structure.md"
  "project_structure_table.md"
  "project_structure.txt"
)
VAULTS_V2=(
  "docs/code_walkthrough_v2"
  "docs/code_walkthrough_en_v2"
)

check_mode=false
if [[ "${1:-}" == "--check" ]]; then
  check_mode=true
fi

# The source docs live in docs/ and link vault notes as
# `[doc](code_walkthrough/<slug>.md)`. Inside a vault the note is a sibling,
# so the `code_walkthrough/` prefix must be stripped or the link resolves to a
# non-existent nested `code_walkthrough/code_walkthrough/` directory.
transform() {
  sed 's#](code_walkthrough/#](#g' "$1"
}

stale=0

# 1. Architecture/report mirrors -> all vaults.
for doc in "${DOCS[@]}"; do
  src="$ROOT/docs/$doc"
  for vault in "${VAULTS[@]}"; do
    dst="$ROOT/$vault/$doc"
    if [[ ! -f "$src" ]]; then
      echo "⚠️  source missing: docs/$doc"
      continue
    fi
    if [[ ! -f "$dst" ]] || ! diff -q <(transform "$src") "$dst" >/dev/null; then
      if $check_mode; then
        echo "❌ stale mirror: $vault/$doc"
        stale=1
      else
        transform "$src" > "$dst"
        echo "✓ synced $vault/$doc"
      fi
    else
      echo "✓ up-to-date $vault/$doc"
    fi
  done
done

# 2. Structure docs -> v2 vaults only.
for doc in "${STRUCTURE_DOCS[@]}"; do
  src="$ROOT/docs/structure/$doc"
  for vault in "${VAULTS_V2[@]}"; do
    dst="$ROOT/$vault/$doc"
    if [[ ! -f "$src" ]]; then
      echo "⚠️  source missing: docs/structure/$doc"
      continue
    fi
    if [[ ! -f "$dst" ]] || ! diff -q "$src" "$dst" >/dev/null; then
      if $check_mode; then
        echo "❌ stale mirror: $vault/$doc"
        stale=1
      else
        cp "$src" "$dst"
        echo "✓ synced $vault/$doc"
      fi
    else
      echo "✓ up-to-date $vault/$doc"
    fi
  done
done

if $check_mode && [[ $stale -ne 0 ]]; then
  echo ""
  echo "Run: bash scripts/sync_vault_mirrors.sh"
  exit 1
fi
