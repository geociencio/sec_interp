#!/usr/bin/env python3
"""
Pre-push hook script to block commits introducing High Cyclomatic Complexity.
Runs qgis-analyzer and blocks push if any function exceeds CC > 10.
"""

import json
import subprocess
import sys
from pathlib import Path

MAX_CC = 10
JSON_REPORT_PATH = Path("analysis_results/project_context.json")


def main():
    print("Running CC gate check (qgis-analyzer)...")

    # Ensure analyzer runs and generates JSON
    try:
        subprocess.run(
            ["uv", "run", "qgis-analyzer", "analyze", "."],
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError as e:
        print("Error running qgis-analyzer:", e.stderr)
        sys.exit(1)

    if not JSON_REPORT_PATH.exists():
        print(f"Error: Analyzer report not found at {JSON_REPORT_PATH}")
        sys.exit(1)

    try:
        with open(JSON_REPORT_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error reading {JSON_REPORT_PATH}: {e}")
        sys.exit(1)

    high_cc_functions = []

    # Parse modules and functions
    for module in data.get("modules", []):
        mod_path = module.get("path", "Unknown Module")

        # Check regular functions and methods
        for func in module.get("functions", []):
            cc = func.get("complexity", 1)
            if cc > MAX_CC:
                high_cc_functions.append(
                    {"module": mod_path, "name": func.get("name", "Unknown"), "cc": cc}
                )

    if high_cc_functions:
        print(
            f"\n\033[91m\u274c PRE-PUSH BLOCKED: Found {len(high_cc_functions)} functions exceeding max CC ({MAX_CC})\033[0m"
        )
        print("-" * 60)
        for item in high_cc_functions:
            print(
                f"  \033[93m{item['module']}\033[0m : {item['name']} (CC: {item['cc']})"
            )
        print("-" * 60)
        print("\nPlease refactor these functions to lower complexity before pushing.")
        sys.exit(1)

    print(f"\033[92m\u2705 CC gate passed. No functions exceed CC > {MAX_CC}.\033[0m")
    sys.exit(0)


if __name__ == "__main__":
    main()
