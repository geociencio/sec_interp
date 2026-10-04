#!/usr/bin/env bash
# Export the agentic framework (.agent/) as a standalone repository for Codeberg.
#
# NOTE (F3+): the framework is now consumed as a git submodule of
# https://codeberg.org/geociencio/agentic-forge. Re-publishing is normally done
# directly in that repository; this script remains for bootstrapping a fresh
# copy from the checked-out .agent/ content.
#
# Modes:
#   (default)       Fresh export with NO git history. Use this for a PUBLIC repo,
#                   because the .agent/ history predates the F1 split and contains
#                   old project state (AGENT_LESSONS, task boards, next_steps).
#   --with-history  Preserve the .agent/ history via `git subtree split`.
#                   Only use it for a PRIVATE repo.
#
# Usage:
#   scripts/export_agentic_forge.sh [--with-history] [--out DIR] [--remote URL] [--license FILE]
#
# Examples:
#   scripts/export_agentic_forge.sh --out /tmp/agentic-forge
#   scripts/export_agentic_forge.sh --license LICENSE-GPL-3.0.txt \
#       --remote git@codeberg.org:<user>/agentic-forge.git

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FRAMEWORK_DIR=".agent"
DEFAULT_OUT="dist/agentic-forge"
SPLIT_BRANCH="agentic-forge-export"

WITH_HISTORY=0
OUT="$REPO_ROOT/$DEFAULT_OUT"
REMOTE=""
LICENSE_FILE=""

usage() {
  sed -n '2,20p' "${BASH_SOURCE[0]}"
}

while [ $# -gt 0 ]; do
  case "$1" in
    --with-history) WITH_HISTORY=1 ;;
    --out) OUT="$2"; shift ;;
    --remote) REMOTE="$2"; shift ;;
    --license) LICENSE_FILE="$2"; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown option: $1" >&2; usage; exit 2 ;;
  esac
  shift
done

cd "$REPO_ROOT"

if [ ! -d "$FRAMEWORK_DIR" ]; then
  echo "❌ Framework directory '$FRAMEWORK_DIR' not found." >&2
  exit 1
fi

if [ "$WITH_HISTORY" -eq 1 ] && [ -f .gitmodules ] && grep -q '"\.agent"' .gitmodules; then
  echo "❌ --with-history is unsupported while .agent is a submodule; push to the framework repo directly." >&2
  exit 2
fi

# Safety gate: absolute home paths must never leak into a public repository.
if grep -rn "/home/" "$FRAMEWORK_DIR" >/dev/null 2>&1; then
  echo "❌ Absolute '/home/' paths found in $FRAMEWORK_DIR. Sanitize before exporting:" >&2
  grep -rn "/home/" "$FRAMEWORK_DIR" >&2
  exit 1
fi

rm -rf "$OUT"
mkdir -p "$OUT"

if [ "$WITH_HISTORY" -eq 1 ]; then
  echo "🗂️  Splitting history for $FRAMEWORK_DIR (private mode)…"
  git branch -D "$SPLIT_BRANCH" >/dev/null 2>&1 || true
  git subtree split -P "$FRAMEWORK_DIR" -b "$SPLIT_BRANCH" >/dev/null
  git clone -q --no-local --single-branch --branch "$SPLIT_BRANCH" "$REPO_ROOT" "$OUT"
  git -C "$OUT" branch -m "$SPLIT_BRANCH" main
  git -C "$OUT" remote remove origin >/dev/null 2>&1 || true
else
  echo "📦 Fresh export without history (public-safe mode)…"
  cp -R "$FRAMEWORK_DIR"/. "$OUT"/
  rm -rf "$OUT/.git" 2>/dev/null || true
fi

# A minimal .gitignore for the exported repository.
cat > "$OUT/.gitignore" <<'EOF'
__pycache__/
*.py[cod]
.ruff_cache/
.venv/
dist/
EOF

if [ -n "$LICENSE_FILE" ]; then
  if [ -f "$LICENSE_FILE" ]; then
    cp "$LICENSE_FILE" "$OUT/LICENSE"
  else
    echo "⚠️  License file '$LICENSE_FILE' not found; skipping." >&2
  fi
elif [ -f "$FRAMEWORK_DIR/LICENSE" ]; then
  cp "$FRAMEWORK_DIR/LICENSE" "$OUT/LICENSE"
else
  echo "⚠️  No license found. Add $FRAMEWORK_DIR/LICENSE or pass --license." >&2
fi

if [ "$WITH_HISTORY" -eq 0 ]; then
  (
    cd "$OUT"
    git init -q -b main
    git add -A
    git commit -qm "chore: initial agentic-forge export"
  )
fi

echo "✅ Framework exported to: $OUT"

if [ -n "$REMOTE" ]; then
  echo "🔗 Adding remote 'origin' → $REMOTE"
  git -C "$OUT" remote remove origin >/dev/null 2>&1 || true
  git -C "$OUT" remote add origin "$REMOTE"
  echo "   Push with: git -C \"$OUT\" push -u origin main"
else
  echo "Next steps:"
  echo "  1. Create an EMPTY repository on Codeberg (no README/license)."
  echo "  2. git -C \"$OUT\" remote add origin git@codeberg.org:<user>/agentic-forge.git"
  echo "  3. git -C \"$OUT\" push -u origin main"
fi
