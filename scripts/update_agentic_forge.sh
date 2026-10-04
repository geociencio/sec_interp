#!/usr/bin/env bash
# Update the agentic-forge framework submodule and validate the result.
#
# Usage:
#   scripts/update_agentic_forge.sh [--commit] [--branch BRANCH]
#
#   --commit         Commit the gitlink bump once validation passes.
#   --branch BRANCH  Tracked branch to update from (default: main).
#
# The framework lives at https://codeberg.org/geociencio/agentic-forge.
# Make generic changes there (or in .agent/ and push), then bump the gitlink here.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

COMMIT=0
BRANCH="main"
while [ $# -gt 0 ]; do
  case "$1" in
    --commit) COMMIT=1 ;;
    --branch) BRANCH="$2"; shift ;;
    -h|--help) sed -n '2,12p' "${BASH_SOURCE[0]}"; exit 0 ;;
    *) echo "Unknown option: $1" >&2; exit 2 ;;
  esac
  shift
done

if [ ! -f .gitmodules ]; then
  echo "❌ .agent is not configured as a submodule." >&2
  exit 1
fi

OLD="$(git submodule status .agent | awk '{print $1}')"
echo "🔄 Updating .agent → $BRANCH…"
git submodule update --init --remote .agent >/dev/null
NEW="$(git submodule status .agent | awk '{print $1}')"

if [ "$OLD" = "$NEW" ]; then
  echo "✅ Already up to date ($NEW)."
  exit 0
fi

echo "📦 Framework $OLD → $NEW"
git -C .agent log --oneline "$OLD".."$NEW" 2>/dev/null | sed 's/^/   /' || true

echo "🔎 Validating framework + overlay…"
uv run python scripts/validate_agent_system.py
uv run python scripts/sync_metrics.py --validate

if [ "$COMMIT" -eq 1 ]; then
  git add .agent
  git commit -m "chore(agent): bump agentic-forge submodule to ${NEW:0:7}"
  echo "✅ Committed gitlink bump."
else
  echo "Next: git add .agent && git commit -m \"chore(agent): bump agentic-forge submodule\""
fi
