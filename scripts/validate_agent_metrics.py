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


def _check_i18n_consistency(summary: dict, issues: list[str]) -> None:
    """Validate that the i18n analyzer count matches the issue breakdown."""
    breakdown = summary.get("issue_breakdown", {})
    i18n_analyzer = summary.get("i18n_issues_qgis_analyzer")
    i18n_breakdown = breakdown.get("MISSING_I18N")
    if i18n_analyzer is not None and i18n_breakdown is not None and i18n_analyzer != i18n_breakdown:
        issues.append(
            f"summary.i18n_issues_qgis_analyzer ({i18n_analyzer}) != "
            f"summary.issue_breakdown.MISSING_I18N ({i18n_breakdown})"
        )


def _check_issue_total(summary: dict, issues: list[str]) -> None:
    """Validate that total_issues equals the sum of the issue breakdown."""
    breakdown = summary.get("issue_breakdown", {})
    total_issues = summary.get("total_issues")
    if total_issues is None or not breakdown:
        return
    breakdown_sum = sum(v for v in breakdown.values() if isinstance(v, int))
    if total_issues != breakdown_sum:
        issues.append(
            f"summary.total_issues ({total_issues}) != sum(issue_breakdown) ({breakdown_sum})"
        )


def _check_test_count(summary: dict, issues: list[str]) -> None:
    """Validate that test_count and tests_ok agree."""
    test_count = summary.get("test_count")
    tests_ok = summary.get("tests_ok")
    if test_count is not None and tests_ok is not None and test_count != tests_ok:
        issues.append(f"summary.test_count ({test_count}) != summary.tests_ok ({tests_ok})")


def _check_score_sources(summary: dict, data: dict, issues: list[str]) -> None:
    """Validate that summary scores match the qgis-analyzer ground-truth source."""
    gt = data.get("ground_truth_sources", {}).get("qgis_analyzer", {}).get("scores", {})
    score_checks = [
        ("quality_score_latest", "module_stability"),
        ("maintainability_score", "maintainability"),
        ("security_score", "security"),
    ]
    for summary_key, gt_key in score_checks:
        summary_val = summary.get(summary_key)
        gt_val = gt.get(gt_key)
        if summary_val is not None and gt_val is not None and summary_val != gt_val:
            issues.append(
                f"summary.{summary_key} ({summary_val}) != "
                f"ground_truth_sources.qgis_analyzer.scores.{gt_key} ({gt_val})"
            )


def _check_session_date(data: dict, issues: list[str]) -> None:
    """Validate that last_session.date is not older than the newest history entry."""
    last_date = data.get("last_session", {}).get("date")
    history = data.get("history", [])
    dates = [h.get("date") for h in history if h.get("date")]
    if last_date and dates and max(dates) > last_date:
        issues.append(
            f"last_session.date ({last_date}) is older than newest history entry ({max(dates)})"
        )


def check_internal_consistency() -> list[str]:
    """Validate that agent_metrics.json is internally coherent.

    Returns a list of human-readable inconsistency descriptions. An empty
    list means the file is internally consistent.
    """
    if not METRICS_FILE.exists():
        return ["agent_metrics.json not found"]

    try:
        data = json.loads(METRICS_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        return [f"agent_metrics.json is not valid JSON: {exc}"]

    issues: list[str] = []
    summary = data.get("summary", {})
    _check_i18n_consistency(summary, issues)
    _check_issue_total(summary, issues)
    _check_test_count(summary, issues)
    _check_score_sources(summary, data, issues)
    _check_session_date(data, issues)
    return issues


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

    internal_issues = check_internal_consistency()
    if internal_issues:
        if not quiet:
            print("❌ agent_metrics.json internal inconsistencies:")
            for issue in internal_issues:
                print(f"  - {issue}")
            print()

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

    if report.clean and not internal_issues:
        if not quiet:
            print("✅ All .agent/ files are metric-consistent with agent_metrics.json")
        sys.exit(0)

    if report.violations:
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
