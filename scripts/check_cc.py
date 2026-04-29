#!/usr/bin/env python3
"""
Cyclomatic Complexity Validator (Gen 6)
Checks that no function exceeds the project threshold (CC <= 10).
"""

import json
import sys
from pathlib import Path

# Configuration
CONTEXT_FILE = Path("json/project_context.json")
CC_THRESHOLD = 10


def main():
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
            if cc > CC_THRESHOLD:
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
            f"❌ [Hotspot Alert] {len(violations)} functions exceed CC threshold (>{CC_THRESHOLD}):"
        )
        # Sort by complexity descending
        violations.sort(key=lambda x: x["cc"], reverse=True)
        for v in violations:
            print(f"  - {v['path']}:{v['line']} -> {v['name']} (CC={v['cc']})")
        print(
            "\n💡 Recommendation: Decompose these monolithic methods into smaller private helpers."
        )
        sys.exit(1)

    print(f"✅ Quality Gate Passed: All functions comply with CC <= {CC_THRESHOLD}.")
    sys.exit(0)


if __name__ == "__main__":
    main()
