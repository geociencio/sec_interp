"""Unit tests for sync_metrics.py session history rotation."""

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_ROOT / ".agent" / "tools"))
sys.path.insert(0, str(_ROOT / "scripts"))

import sync_metrics  # noqa: E402


class TestRotateSessionHistory(unittest.TestCase):
    def _write(self, directory, data):
        path = Path(directory) / "agent_metrics.json"
        path.write_text(json.dumps(data))
        return path

    def test_rotates_previous_into_history(self):
        data = {
            "summary": {
                "tests_ok": 620,
                "quality_score_latest": 52.3,
            },
            "last_session": {
                "date": "2026-05-23",
                "topic": "i18n_hygiene",
                "tests_ok": 620,
                "status": "SUCCESS",
            },
            "history": [],
        }
        with tempfile.TemporaryDirectory() as d:
            path = self._write(d, data)
            ok = sync_metrics.rotate_session_history("new_topic", path)

            self.assertTrue(ok)
            result = json.loads(path.read_text())
            self.assertEqual(result["last_session"]["topic"], "new_topic")
            self.assertEqual(result["last_session"]["tests_ok"], 620)
            self.assertEqual(len(result["history"]), 1)
            self.assertEqual(result["history"][0]["session"], "i18n_hygiene")

    def test_does_not_duplicate_existing_history(self):
        data = {
            "summary": {"tests_ok": 620, "quality_score_latest": 52.3},
            "last_session": {
                "date": "2026-05-23",
                "topic": "i18n_hygiene",
                "status": "SUCCESS",
            },
            "history": [{"date": "2026-05-23", "session": "i18n_hygiene"}],
        }
        with tempfile.TemporaryDirectory() as d:
            path = self._write(d, data)
            ok = sync_metrics.rotate_session_history("next", path)
            self.assertTrue(ok)
            result = json.loads(path.read_text())
            self.assertEqual(len(result["history"]), 1)

    def test_missing_file_returns_false(self):
        ok = sync_metrics.rotate_session_history("topic", Path("/nonexistent/agent_metrics.json"))
        self.assertFalse(ok)


class TestStripAnsi(unittest.TestCase):
    """The analyzer emits ANSI colors; the parser must strip them."""

    def test_strips_color_sequences(self):
        colored = "\x1b[93m- Module Stability Score: \x1b[93m54.0/100\x1b[0m"
        self.assertEqual(
            sync_metrics._strip_ansi(colored),
            "- Module Stability Score: 54.0/100",
        )

    def test_plain_text_unchanged(self):
        self.assertEqual(sync_metrics._strip_ansi("plain 52.3/100"), "plain 52.3/100")

    def test_parses_score_from_colored_line(self):
        line = sync_metrics._strip_ansi("Module Stability Score: \x1b[93m54.0/100\x1b[0m")
        self.assertEqual(float(line.split(":")[-1].strip().split("/")[0]), 54.0)


class TestReadAnalyzerContext(unittest.TestCase):
    """The JSON artifact is the authoritative source for every issue type."""

    def test_aggregates_all_issue_types(self):
        data = {
            "metrics": {
                "quality_score": 55.7,
                "maintainability_score": 99.9,
                "security_score": 100.0,
            },
            "qgis_compliance": {
                "best_practices": {
                    "issues": [
                        {"type": "GOD_OBJECT"},
                        {"type": "GOD_OBJECT"},
                        {"type": "UNPRECISE_LAYER"},
                    ]
                }
            },
            "research_summary": {
                "type_hint_coverage": 97.2,
                "return_hint_coverage": 99.7,
                "docstring_coverage": 99.0,
            },
            "analyzed_at": "2026-10-18T17:10:12",
        }
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "project_context.json"
            path.write_text(json.dumps(data))
            with patch.object(sync_metrics, "ANALYZER_RESULTS", path):
                context = sync_metrics.read_analyzer_context()

        self.assertEqual(context["issues"], {"GOD_OBJECT": 2, "UNPRECISE_LAYER": 1})
        self.assertEqual(context["total_issues"], 3)
        self.assertEqual(context["scores"]["module_stability"], 55.7)
        self.assertEqual(context["research"]["docstring_coverage"], 99.0)

    def test_missing_artifact_returns_empty(self):
        with patch.object(sync_metrics, "ANALYZER_RESULTS", Path("/nonexistent/context.json")):
            self.assertEqual(sync_metrics.read_analyzer_context(), {})


class TestAnalyzerFreshness(unittest.TestCase):
    """agent_metrics.json must match the latest analyzer artifact."""

    def _write(self, directory, metrics, context):
        metrics_path = Path(directory) / "agent_metrics.json"
        context_path = Path(directory) / "project_context.json"
        metrics_path.write_text(json.dumps(metrics))
        context_path.write_text(json.dumps(context))
        return metrics_path, context_path

    @staticmethod
    def _context(issues, quality=55.7, maintainability=99.9, security=100.0):
        return {
            "metrics": {
                "quality_score": quality,
                "maintainability_score": maintainability,
                "security_score": security,
            },
            "qgis_compliance": {"best_practices": {"issues": issues}},
        }

    def test_detects_issue_total_mismatch(self):
        metrics = {
            "summary": {
                "total_issues": 36,
                "quality_score_latest": 55.7,
                "maintainability_score": 99.9,
                "security_score": 100.0,
            },
            "ground_truth_sources": {"qgis_analyzer": {"issues": {"total": 36}}},
        }
        context = self._context([{"type": "GOD_OBJECT"}, {"type": "UNPRECISE_LAYER"}])
        with tempfile.TemporaryDirectory() as d:
            metrics_path, context_path = self._write(d, metrics, context)
            with (
                patch.object(sync_metrics, "METRICS_FILE", metrics_path),
                patch.object(sync_metrics, "ANALYZER_RESULTS", context_path),
            ):
                mismatches = sync_metrics.validate_against_analyzer_context()

        self.assertTrue(any("total_issues" in mismatch for mismatch in mismatches))
        self.assertTrue(
            any("ground_truth_sources.qgis_analyzer.issues.total" in m for m in mismatches)
        )

    def test_clean_when_metrics_match(self):
        metrics = {
            "summary": {
                "total_issues": 2,
                "quality_score_latest": 55.7,
                "maintainability_score": 99.9,
                "security_score": 100.0,
            },
            "ground_truth_sources": {"qgis_analyzer": {"issues": {"total": 2}}},
        }
        context = self._context([{"type": "GOD_OBJECT"}, {"type": "UNPRECISE_LAYER"}])
        with tempfile.TemporaryDirectory() as d:
            metrics_path, context_path = self._write(d, metrics, context)
            with (
                patch.object(sync_metrics, "METRICS_FILE", metrics_path),
                patch.object(sync_metrics, "ANALYZER_RESULTS", context_path),
            ):
                mismatches = sync_metrics.validate_against_analyzer_context()

        self.assertEqual(mismatches, [])


class TestUpdateMetricsJson(unittest.TestCase):
    """Static and executed test counts are recorded separately."""

    def test_separates_static_and_executed_counts(self):
        data = {
            "summary": {},
            "history": [{"date": "2026-10-18"}],
            "meta": {},
            "ground_truth_sources": {},
        }
        metrics = {
            "qgis_analyzer": {
                "scores": {
                    "module_stability": 55.7,
                    "maintainability": 99.9,
                    "security": 100.0,
                },
                "issues": {"UNPRECISE_LAYER": 1},
                "total_issues": 1,
                "research": {},
            },
            "cc": {"passed": None},
            "i18n": {"passed": True},
            "module_sizes": {},
            "tests_executed": 743,
        }
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "agent_metrics.json"
            path.write_text(json.dumps(data))
            with patch.object(sync_metrics, "METRICS_FILE", path):
                ok = sync_metrics.update_metrics_json(metrics)
            result = json.loads(path.read_text())

        self.assertTrue(ok)
        summary = result["summary"]
        static_count = sync_metrics.count_total_tests()
        self.assertEqual(summary["tests_static"], static_count)
        self.assertEqual(summary["tests_executed"], 743)
        self.assertEqual(summary["test_count"], static_count)
        self.assertEqual(summary["tests_ok"], static_count)
        self.assertEqual(summary["total_issues"], 1)
        self.assertEqual(summary["issue_breakdown"]["UNPRECISE_LAYER"], 1)
        self.assertEqual(summary["total_sessions"], 1)
        self.assertEqual(result["ground_truth_sources"]["tests_local"]["result"], "743 ran OK")


if __name__ == "__main__":
    unittest.main()
