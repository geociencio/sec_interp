"""Unit tests for validate_agent_metrics.py internal-consistency checks."""

import json
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parents[2] / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

import validate_agent_metrics as vam  # noqa: E402


class TestInternalConsistencyHelpers(unittest.TestCase):
    def test_i18n_consistency_detects_mismatch(self):
        summary = {
            "i18n_issues_qgis_analyzer": 254,
            "issue_breakdown": {"MISSING_I18N": 72},
        }
        issues = []
        vam._check_i18n_consistency(summary, issues)
        self.assertEqual(len(issues), 1)

    def test_i18n_consistency_ok_when_matching(self):
        summary = {
            "i18n_issues_qgis_analyzer": 72,
            "issue_breakdown": {"MISSING_I18N": 72},
        }
        issues = []
        vam._check_i18n_consistency(summary, issues)
        self.assertEqual(issues, [])

    def test_issue_total_matches_breakdown(self):
        summary = {
            "total_issues": 75,
            "issue_breakdown": {
                "MISSING_I18N": 72,
                "NON_PYTHONIC_LOOP": 2,
                "SPATIAL_INDEX": 1,
            },
        }
        issues = []
        vam._check_issue_total(summary, issues)
        self.assertEqual(issues, [])

    def test_issue_total_detects_mismatch(self):
        summary = {
            "total_issues": 100,
            "issue_breakdown": {"MISSING_I18N": 72},
        }
        issues = []
        vam._check_issue_total(summary, issues)
        self.assertEqual(len(issues), 1)

    def test_test_count_detects_mismatch(self):
        summary = {"test_count": 620, "tests_ok": 572}
        issues = []
        vam._check_test_count(summary, issues)
        self.assertEqual(len(issues), 1)

    def test_test_count_ok_when_matching(self):
        summary = {"test_count": 620, "tests_ok": 620}
        issues = []
        vam._check_test_count(summary, issues)
        self.assertEqual(issues, [])

    def test_score_source_detects_mismatch(self):
        summary = {"maintainability_score": 90.7}
        data = {
            "ground_truth_sources": {
                "qgis_analyzer": {"scores": {"maintainability": 99.9}}
            }
        }
        issues = []
        vam._check_score_sources(summary, data, issues)
        self.assertEqual(len(issues), 1)

    def test_session_date_older_than_history(self):
        data = {
            "last_session": {"date": "2026-05-23"},
            "history": [{"date": "2026-09-06"}],
        }
        issues = []
        vam._check_session_date(data, issues)
        self.assertEqual(len(issues), 1)


class TestCheckInternalConsistency(unittest.TestCase):
    def _write_metrics(self, directory, data):
        path = Path(directory) / "agent_metrics.json"
        path.write_text(json.dumps(data))
        return path

    def test_consistent_file_returns_no_issues(self):
        data = {
            "summary": {
                "i18n_issues_qgis_analyzer": 72,
                "issue_breakdown": {
                    "MISSING_I18N": 72,
                    "NON_PYTHONIC_LOOP": 2,
                    "SPATIAL_INDEX": 1,
                },
                "total_issues": 75,
                "test_count": 620,
                "tests_ok": 620,
                "quality_score_latest": 52.3,
                "maintainability_score": 99.9,
                "security_score": 100.0,
            },
            "ground_truth_sources": {
                "qgis_analyzer": {
                    "scores": {
                        "module_stability": 52.3,
                        "maintainability": 99.9,
                        "security": 100.0,
                    }
                }
            },
            "last_session": {"date": "2026-09-06"},
            "history": [{"date": "2026-09-06"}],
        }
        with tempfile.TemporaryDirectory() as d:
            path = self._write_metrics(d, data)
            issues = vam.check_internal_consistency(path)
            self.assertEqual(issues, [])

    def test_missing_file(self):
        issues = vam.check_internal_consistency(Path("/nonexistent/agent_metrics.json"))
        self.assertEqual(issues, ["agent_metrics.json not found"])


if __name__ == "__main__":
    unittest.main()
