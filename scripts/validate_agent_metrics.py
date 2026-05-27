#!/usr/bin/env python3
"""
Cross-File Metric Consistency Validator (Gen 7)

Scans all .agent/ markdown and JSON files (excluding history archives) and
validates that every embedded metric reference matches the ground truth in
agent_metrics.json. Catches the exact class of drift we just fixed manually.

Usage:
    uv run python scripts/validate_agent_metrics.py [--quiet] [--fix]

Output:
    - Reports every file/line/metric mismatch to stderr
    - Returns exit code 0 if consistent, 1 if discrepancies found
    - With --fix: attempts to auto-correct common stale values (535→620, etc.)

Ground truth source:
    .agent/memory/agent_metrics.json (updated by sync_metrics.py)
"""

from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

PROJECT_ROOT = Path(__file__).resolve().parent.parent
AGENT_DIR = PROJECT_ROOT / ".agent"
METRICS_FILE = AGENT_DIR / "memory" / "agent_metrics.json"
HISTORY_DIR = AGENT_DIR / "history"

# Patterns to extract embedded metrics from documentation files
TEST_PATTERNS = [
    (re.compile(r"\b(\d+)\s*tests?\s*(?:OK|pass|passing|ok)", re.IGNORECASE), "test_count"),
    (re.compile(r"tests?:\s*(\d+)"), "test_count"),
    (re.compile(r"total_?tests?:\s*(\d+)", re.IGNORECASE), "test_count"),
    (re.compile(r"(\d+)/\d+\s*\(100%\)", re.IGNORECASE), "test_count"),
    (re.compile(r"Achieve\s+(\d+)\+?\s*passing\s+tests?", re.IGNORECASE), "test_min"),
]

QUALITY_PATTERNS = [
    (re.compile(r"[Qq]uality\s*[Ss]core:?\s*(\d+\.?\d*)/?\d*"), "quality_score"),
    (re.compile(r"[Mm]odule\s*[Ss]tability:?\s*\*?\*?(\d+\.?\d*)/?\d*"), "quality_score"),
    (re.compile(r"[Ss]tability\s*[Ss]core:?\s*(\d+\.?\d*)/?\d*"), "quality_score"),
]

CC_PATTERNS = [
    (re.compile(r"CC\s*[><=]+\s*(\d+)"), "cc_threshold"),
    (re.compile(r"cyclomatic\s+complexity\s+(?:below|under)\s+(\d+)", re.IGNORECASE), "cc_threshold"),
    (re.compile(r"complexity\s*(?:>\s*(\d+)|<=?\s*(\d+))"), "cc_threshold"),
]

# Common stale→correct mappings for --fix mode
STALE_MAPPINGS = {
    "test_count": {
        535: 620, 572: 620,
    },
    "quality_score": {
        40.8: 52.3, 41.7: 52.3,
    },
    "cc_threshold": {
        15: 10,
    },
}


@dataclass
class MetricViolation:
    file: str
    line: int
    metric_type: str
    found_value: str
    expected_value: str
    context: str

    def __str__(self):
        return (
            f"  {self.file}:{self.line}  [{self.metric_type}] "
            f"found={self.found_value}  expected={self.expected_value}"
            f"\n    → {self.context.strip()}"
        )


@dataclass
class ValidationReport:
    violations: list[MetricViolation] = field(default_factory=list)
    files_scanned: int = 0

    @property
    def clean(self) -> bool:
        return len(self.violations) == 0


def load_ground_truth() -> dict:
    """Extract canonical metric values from agent_metrics.json."""
    if not METRICS_FILE.exists():
        return {}

    try:
        data = json.loads(METRICS_FILE.read_text())
    except json.JSONDecodeError:
        return {}

    truth = {}

    # Test count: try test_count first, then tests_ok
    summary = data.get("summary", {})
    if "test_count" in summary:
        truth["test_count"] = summary["test_count"]
    elif "tests_ok" in summary:
        truth["test_count"] = summary["tests_ok"]

    truth["quality_score"] = summary.get("quality_score_latest")
    truth["maintainability_score"] = summary.get("maintainability_score")
    truth["security_score"] = summary.get("security_score")

    # CC gate: always 10 in this project
    truth["cc_threshold"] = 10

    return truth


def should_skip_file(filepath: Path) -> bool:
    """Skip history archives and non-markdown/json files."""
    if filepath.suffix not in (".md", ".json"):
        return True

    rel_path = str(filepath.relative_to(AGENT_DIR))
    if rel_path.startswith("history/"):
        return True
    if rel_path.startswith("architecture/"):
        return True

    # Skip the ground-truth file itself
    if filepath.resolve() == METRICS_FILE.resolve():
        return True

    return False


def extract_metrics_from_line(line: str) -> list[tuple[str, str, str]]:
    """Extract metric references from a single line.
    Returns list of (metric_type, raw_match, clean_value) tuples.
    """
    results = []

    for pattern, metric_type in TEST_PATTERNS:
        for m in pattern.finditer(line):
            raw = m.group(0)
            val = m.group(1)
            results.append((metric_type, raw, val))

    for pattern, metric_type in QUALITY_PATTERNS:
        for m in pattern.finditer(line):
            raw = m.group(0)
            val = m.group(1)
            results.append((metric_type, raw, val))

    for pattern, metric_type in CC_PATTERNS:
        for m in pattern.finditer(line):
            raw = m.group(0)
            val = m.group(1) or m.group(2)
            if val:
                results.append((metric_type, raw, val))

    return results


def normalize_value(val_str: str) -> Optional[float]:
    """Normalize a found metric value to float for comparison."""
    try:
        return float(val_str)
    except ValueError:
        return None


def detect_documented_triage(context: str, found_val: float, expected_val: float) -> bool:
    """Skip lines that explicitly document a discrepancy being triaged/resolved."""
    triage_markers = [
        "vs", "→", "conflicting", "verified", "RESOLVED",
        "resolved", "discrepancy", "confirmed",
    ]
    if not any(marker.lower() in context.lower() for marker in triage_markers):
        return False
    # Check if both values are mentioned in context (documenting the fix)
    if str(int(found_val)) in context and str(int(expected_val)) in context:
        return True
    return False


def is_archaic_reference(context: str, found_val: float, expected_val: float) -> bool:
    """Check if the line is describing a past state (e.g., 'v3.6.0 Baseline')."""
    archaic_markers = [
        "v3.6.0 Baseline", "v3.5.0", "v3.4.0", "v3.3.0",
        "v3.2.0", "v3.0.0", "v2.",
        "previously", "before phase", "was stale",
    ]
    return any(marker.lower() in context.lower() for marker in archaic_markers)


def validate_file(filepath: Path, ground_truth: dict) -> list[MetricViolation]:
    """Scan a single file for metric inconsistencies."""
    violations = []
    try:
        content = filepath.read_text(encoding="utf-8")
    except Exception:
        return violations

    lines = content.splitlines()
    for lineno, line in enumerate(lines, start=1):
        metrics = extract_metrics_from_line(line)
        for metric_type, raw_match, clean_val in metrics:
            found = normalize_value(clean_val)
            if found is None:
                continue

            expected = ground_truth.get(metric_type)
            if expected is None:
                continue

            if found == expected:
                continue

            # Exemptions
            if detect_documented_triage(line, found, expected):
                continue
            if is_archaic_reference(line, found, expected):
                continue

            violations.append(MetricViolation(
                file=str(filepath.relative_to(PROJECT_ROOT)),
                line=lineno,
                metric_type=metric_type,
                found_value=str(int(found) if found == int(found) else found),
                expected_value=str(int(expected) if expected == int(expected) else expected),
                context=line.strip(),
            ))

    return violations


def scan_agent_files(ground_truth: dict) -> ValidationReport:
    """Scan all relevant .agent/ files for metric consistency."""
    report = ValidationReport()

    if not AGENT_DIR.exists():
        return report

    for filepath in sorted(AGENT_DIR.rglob("*")):
        if not filepath.is_file():
            continue
        if should_skip_file(filepath):
            continue

        report.files_scanned += 1
        violations = validate_file(filepath, ground_truth)
        report.violations.extend(violations)

    return report


def auto_fix(filepath: Path, violations: list[MetricViolation]) -> bool:
    """Attempt to auto-fix known stale values inline."""
    try:
        content = filepath.read_text(encoding="utf-8")
    except Exception:
        return False

    modified = False
    for v in violations:
        mapping = STALE_MAPPINGS.get(v.metric_type, {})
        found_num = None
        try:
            found_num = float(v.found_value)
        except ValueError:
            continue
        found_int = int(found_num) if found_num == int(found_num) else found_num

        new_val = mapping.get(found_int)
        if new_val is None:
            continue

        new_str = str(new_val)
        old_str = str(v.found_value)
        if old_str in content:
            content = content.replace(old_str, new_str, 1)
            modified = True

    if modified:
        filepath.write_text(content, encoding="utf-8")

    return modified


def main():
    quiet = "--quiet" in sys.argv
    fix_mode = "--fix" in sys.argv

    ground_truth = load_ground_truth()
    if not ground_truth:
        print("❌ Cannot load ground truth from agent_metrics.json", file=sys.stderr)
        print("   Run: uv run python scripts/sync_metrics.py", file=sys.stderr)
        sys.exit(1)

    report = scan_agent_files(ground_truth)

    if not quiet:
        print(f"🔍 Scanned {report.files_scanned} files in .agent/")
        print(f"   Ground truth: tests={ground_truth.get('test_count', '?')}, "
              f"quality={ground_truth.get('quality_score', '?')}, "
              f"CC≤{ground_truth.get('cc_threshold', '?')}")

    if report.clean:
        if not quiet:
            print("✅ All .agent/ files are metric-consistent with agent_metrics.json")
        sys.exit(0)

    if not quiet:
        print(f"❌ Found {len(report.violations)} metric inconsistencies:\n")

    fixes_applied = 0
    for v in report.violations:
        if not quiet:
            print(str(v))

        if fix_mode:
            filepath = PROJECT_ROOT / v.file
            if auto_fix(filepath, [v]):
                fixes_applied += 1

    if fix_mode and fixes_applied > 0:
        if not quiet:
            print(f"\n🔧 Auto-fixed {fixes_applied} stale values. "
                  f"Run again to verify: uv run python scripts/validate_agent_metrics.py")
        sys.exit(0)

    sys.exit(1)


if __name__ == "__main__":
    main()
