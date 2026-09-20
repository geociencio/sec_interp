#!/usr/bin/env bash
# Sync mirror architecture/report docs from docs/ → code_walkthrough vaults.
# Keeps wikilinks [[ARCHITECTURE_EN]] resolvable in Obsidian without drift.
#
# Usage:
#   bash scripts/sync_vault_mirrors.sh
#   bash scripts/sync_vault_mirrors.sh --check   # exit 1 if out of sync

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DOCS=(
  "ARCHITECTURE_EN.md"
  "ARCHITECTURE_MONOLITHIC_VS_CLEAN_EN.md"
  "PLUGIN_REPORT_AND_COMPARISON_EN.md"
)
VAULTS=(
  "docs/code_walkthrough"
  "docs/code_walkthrough_en"
)

check_mode=false
if [[ "${1:-}" == "--check" ]]; then
  check_mode=true
fi

stale=0
for doc in "${DOCS[@]}"; do
  src="$ROOT/docs/$doc"
  for vault in "${VAULTS[@]}"; do
    dst="$ROOT/$vault/$doc"
    if [[ ! -f "$src" ]]; then
      echo "⚠️  source missing: docs/$doc"
      continue
    fi
    if [[ ! -f "$dst" ]] || ! cmp -s "$src" "$dst"; then
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
