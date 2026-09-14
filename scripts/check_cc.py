#!/usr/bin/env python3
"""
Cyclomatic Complexity Validator (Gen 8)

Checks that no function exceeds the project's cyclomatic complexity threshold.

Usage:
    uv run python scripts/check_cc.py [--threshold N]
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Configuration
CONTEXT_FILE = Path("json/project_context.json")
DEFAULT_CC_THRESHOLD = 10


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Cyclomatic complexity validator (checks CC <= threshold)."
    )
    parser.add_argument(
        "--threshold",
        type=int,
        default=DEFAULT_CC_THRESHOLD,
        help=f"Maximum cyclomatic complexity per function (default: {DEFAULT_CC_THRESHOLD})",
    )
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    threshold = args.threshold

    if not CONTEXT_FILE.exists():
        print(
            f"❌ Error: {CONTEXT_FILE} not found. Ensure qgis-analyzer has been executed."
        )
        sys.exit(1)

    try:
        data = json.loads(CONTEXT_FILE.read_text())
    except Exception as e:
        print(f"❌ Error parsing JSON: {e}")
        sys.exit(1)

    modules = data.get("modules", [])
    violations = []

    for mod in modules:
        path = mod.get("path", "unknown")
        # Skip vendor or scaffold if present
        if "antigravity-framerepo" in path or "vendor" in path:
            continue

        for func in mod.get("functions", []):
            cc = func.get("complexity", 0)
            if cc > threshold:
                violations.append(
                    {
                        "path": path,
                        "name": func.get("name"),
                        "line": func.get("line"),
                        "cc": cc,
                    }
                )

    if violations:
        print(
            f"❌ [Hotspot Alert] {len(violations)} functions exceed CC threshold (>{threshold}):"
        )
        # Sort by complexity descending
        violations.sort(key=lambda x: x["cc"], reverse=True)
        for v in violations:
            print(f"  - {v['path']}:{v['line']} -> {v['name']} (CC={v['cc']})")
        print(
            "\n💡 Recommendation: Decompose these monolithic methods into smaller private helpers."
        )
        sys.exit(1)

    print(f"✅ Quality Gate Passed: All functions comply with CC <= {threshold}.")
    sys.exit(0)


if __name__ == "__main__":
    main()
