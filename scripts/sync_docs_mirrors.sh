#!/usr/bin/env bash
# Sync canonical repository docs into the Sphinx source tree (docs/source).
#
# Several docs exist twice: the repo-facing copy under docs/ (canonical) and a
# copy under docs/source/ that Sphinx builds. This keeps them identical.
#
# Usage:
#   bash scripts/sync_docs_mirrors.sh
#   bash scripts/sync_docs_mirrors.sh --check   # exit 1 if out of sync

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PAIRS=(
  "CORE_DISTINCTION_GUIDE.md"
  "CORE_DISTINCTION_GUIDE_EN.md"
)

check_mode=false
if [[ "${1:-}" == "--check" ]]; then
  check_mode=true
fi

stale=0
for f in "${PAIRS[@]}"; do
  src="$ROOT/docs/$f"
  dst="$ROOT/docs/source/$f"
  if [[ ! -f "$src" ]]; then
    echo "⚠️  source missing: docs/$f"
    continue
  fi
  if [[ ! -f "$dst" ]] || ! cmp -s "$src" "$dst"; then
    if $check_mode; then
      echo "❌ stale mirror: docs/source/$f"
      stale=1
    else
      cp "$src" "$dst"
      echo "✓ synced docs/source/$f"
    fi
  else
    echo "✓ up-to-date docs/source/$f"
  fi
done

if $check_mode && [[ $stale -ne 0 ]]; then
  echo ""
  echo "Run: bash scripts/sync_docs_mirrors.sh"
  exit 1
fi
