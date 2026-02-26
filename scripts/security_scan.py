#!/usr/bin/env python3
"""
Security Scanner for SecInterp Plugin
Replicates QGIS Portal security scanning locally.

Usage:
    python scripts/security_scan.py [--verbose]

Tools Used (QGIS Portal Compatible):
    - Bandit: Security vulnerability scanner
    - detect-secrets: Secrets and credentials detector
    - Flake8: Code quality checker (portal compatible)
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Tuple


class SecurityScanner:
    """Unified security scanner using QGIS portal tools."""

    def __init__(self, plugin_dir: Path, verbose: bool = False):
        self.plugin_dir = plugin_dir
        self.verbose = verbose
        self.results: Dict[str, Tuple[int, str, Dict]] = {}

    def _run_command(self, cmd: List[str], tool_name: str) -> Tuple[int, str, Dict]:
        """Run a command and capture output."""
        try:
            result = subprocess.run(  # nosec B603
                cmd, capture_output=True, text=True, cwd=self.plugin_dir
            )

            # Try to parse JSON output
            report = {}
            if result.stdout:
                try:
                    report = json.loads(result.stdout)
                except json.JSONDecodeError:
                    report = {"raw_output": result.stdout}

            return result.returncode, result.stdout, report
        except Exception as e:
            print(f"❌ Error running {tool_name}: {e}")
            return 1, str(e), {}

    def run_bandit(self) -> Tuple[int, str, Dict]:
        """Run Bandit security analysis (CRITICAL)."""
        print("🔒 Running Bandit (Security Vulnerabilities)...")

        cmd = [
            "bandit",
            "-r",
            ".",
            "-c",
            ".bandit",
            "-f",
            "json",
        ]

        code, output, report = self._run_command(cmd, "Bandit")

        if self.verbose and report:
            issues = report.get("results", [])
            print(f"   Found {len(issues)} potential issues")

        return code, output, report

    def run_detect_secrets(self) -> Tuple[int, str, Dict]:
        """Run detect-secrets scanner (CRITICAL)."""
        print("🔐 Running detect-secrets (Hardcoded Secrets)...")

        cmd = [
            "detect-secrets",
            "scan",
            ".",
            "--baseline",
            ".secrets.baseline",
        ]

        code, output, report = self._run_command(cmd, "detect-secrets")

        if self.verbose and report:
            results = report.get("results", {})
            total_secrets = sum(len(secrets) for secrets in results.values())
            print(f"   Found {total_secrets} potential secrets")

        return code, output, report

    def run_flake8(self) -> Tuple[int, str, Dict]:
        """Run Flake8 code quality checks (INFO) - QGIS Portal Compatible."""
        print("📊 Running Flake8 (Code Quality - Portal Compatible)...")

        cmd = [
            "flake8",
            ".",
            "--config",
            ".flake8",
        ]

        code, output, report = self._run_command(cmd, "Flake8")

        if self.verbose and isinstance(report, dict):
            violations = report.get("violations", [])
            print(f"   Found {len(violations)} style/quality issues")

        return code, output, report

    def _save_report(self, tool_name: str, report: Dict):
        """Save detailed report to file."""
        report_file = self.plugin_dir / f"{tool_name}_report.json"
        with open(report_file, "w") as f:
            json.dump(report, f, indent=2)
        print(f"   📄 Report saved: {report_file.name}")

    def run_all(self) -> int:
        """Run all security scans."""
        print("=" * 70)
        print("SecInterp Security Scanner (QGIS Portal Compatible)")
        print("=" * 70)
        print()

        # Run all scans
        self.results["bandit"] = self.run_bandit()
        self.results["detect-secrets"] = self.run_detect_secrets()
        self.results["flake8"] = self.run_flake8()

        print()
        print("=" * 70)
        print("SCAN SUMMARY")
        print("=" * 70)

        critical_issues = 0
        warnings = 0

        for tool, (code, output, report) in self.results.items():
            # Determine severity
            if tool in ["bandit", "detect-secrets"]:
                severity = "CRITICAL" if code != 0 else "✅ PASS"
                if code != 0:
                    critical_issues += 1
            else:  # flake8
                severity = "INFO" if code != 0 else "✅ PASS"
                if code != 0:
                    warnings += 1

            print(f"{tool:20s}: {severity}")

            # Save detailed report
            if report:
                self._save_report(tool, report)

        print("=" * 70)
        print()

        # Final verdict
        if critical_issues > 0:
            print(f"❌ CRITICAL: {critical_issues} security tool(s) found issues!")
            print("   Review: bandit_report.json, detect-secrets_report.json")
            print()
            print("⚠️  These issues may prevent QGIS Portal approval.")
            return 1
        elif warnings > 0:
            print(f"⚠️  INFO: {warnings} code quality issue(s) found.")
            print("   Review: flake8_report.json")
            print()
            print("✅ No critical security issues. Quality issues are informational.")
            return 0
        else:
            print("✅ All security and quality checks passed!")
            print()
            print("🎉 Plugin is ready for QGIS Portal upload.")
            return 0


def main():
    parser = argparse.ArgumentParser(
        description="Security scanner for SecInterp (QGIS Portal compatible)"
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Show detailed output"
    )
    args = parser.parse_args()

    plugin_dir = Path(__file__).parent.parent
    scanner = SecurityScanner(plugin_dir, verbose=args.verbose)
    sys.exit(scanner.run_all())


if __name__ == "__main__":
    main()
