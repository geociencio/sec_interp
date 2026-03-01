#!/usr/bin/env python3
"""Script to dynamically update TESTING_STATUS.md based on current tests."""

import os
import re
from datetime import datetime
from pathlib import Path


def count_tests_in_file(file_path):
    """Count test methods in a file."""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    # Simple regex to count test_... methods
    return len(re.findall(r"def\s+test_", content))


def get_test_inventory(test_dir):
    """Get a detailed list of tests for the inventory section."""
    inventory = []
    for root, dirs, files in os.walk(test_dir):
        # Sort files to keep stable inventory
        for file in sorted(files):
            if file.startswith("test_") and file.endswith(".py"):
                path = Path(root) / file
                rel_path = path.relative_to(test_dir.parent)
                count = count_tests_in_file(path)
                if count > 0:
                    inventory.append(f"- **{rel_path}**: {count} tests")
    return "\n".join(inventory)


def update_section(content, section_id, new_value):
    """Update a specific section in the markdown content."""
    pattern = f"<!-- {section_id} -->.*?<!-- /{section_id} -->"
    replacement = f"<!-- {section_id} -->{new_value}<!-- /{section_id} -->"
    return re.sub(pattern, replacement, content, flags=re.DOTALL)


def main():
    base_dir = Path(__file__).resolve().parent.parent
    test_dir = base_dir / "tests"
    status_file = test_dir / "TESTING_STATUS.md"

    if not status_file.exists():
        print(f"Error: {status_file} not found.")
        return

    with open(status_file, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Count tests by category
    categories = {
        "CORE_COUNT": test_dir / "core",
        "GUI_COUNT": test_dir / "gui",
        "EXP_COUNT": test_dir / "exporters",
        "INT_COUNT": test_dir / "integration",
    }

    total_tests = 0
    for key, path in categories.items():
        cat_count = 0
        if path.exists():
            for root, _, files in os.walk(path):
                for file in files:
                    if file.startswith("test_") and file.endswith(".py"):
                        cat_count += count_tests_in_file(Path(root) / file)

        content = update_section(content, key, str(cat_count))
        total_tests += cat_count

    # 2. Update summary metrics
    content = update_section(content, "TOTAL_TESTS", str(total_tests))
    content = update_section(
        content, "LAST_UPDATE", datetime.now().strftime("%Y-%m-%d")
    )

    # 3. Update Detailed Inventory
    inventory = get_test_inventory(test_dir)
    pattern = "(<!-- START_INVENTORY -->).*?(<!-- END_INVENTORY -->)"
    content = re.sub(pattern, f"\\1\n{inventory}\n\\2", content, flags=re.DOTALL)

    with open(status_file, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"Successfully updated {status_file} with {total_tests} tests.")


if __name__ == "__main__":
    main()
