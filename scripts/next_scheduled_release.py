"""Select the next due release for the scheduled release workflow.

Reads ``.release-queue.json`` and prints, in GitHub Actions output format, the
first release whose date is due and whose tag has not been published yet:

    version=<x.y.z>
    branch=release/vX.Y.Z

When nothing is due, prints ``nothing_due=true``.

Usage:
    python scripts/next_scheduled_release.py [version]

Passing ``version`` forces that release regardless of its date (manual
``workflow_dispatch``), as long as it has not been published yet.
"""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import date
from pathlib import Path

QUEUE_PATH = Path(".release-queue.json")


def published_tags() -> set[str]:
    """Return the tag names already present on the origin remote.

    Returns:
        A set of tag names (e.g. ``{"v3.8.0", "v3.9.0"}``). Empty when the
        remote cannot be queried.

    """
    try:
        result = subprocess.run(
            ["git", "ls-remote", "--tags", "origin"],
            check=True,
            capture_output=True,
            text=True,
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        return set()
    tags: set[str] = set()
    for line in result.stdout.splitlines():
        ref = line.split("\t")[-1].strip()
        if not ref:
            continue
        tags.add(ref.removeprefix("refs/tags/").removesuffix("^{}"))
    return tags


def main(argv: list[str]) -> int:
    """Print the next due release, if any."""
    requested = argv[1].strip() if len(argv) > 1 else ""
    data = json.loads(QUEUE_PATH.read_text(encoding="utf-8"))
    tags = published_tags()
    today = date.today()

    for item in data["releases"]:
        version = item["version"]
        if f"v{version}" in tags:
            continue
        if requested and version != requested:
            continue
        if requested or date.fromisoformat(item["date"]) <= today:
            print(f"version={version}")
            print(f"branch={item['branch']}")
            return 0

    print("nothing_due=true")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
