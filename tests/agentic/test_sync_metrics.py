"""Unit tests for sync_metrics.py session history rotation."""

import json
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parents[2] / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

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


if __name__ == "__main__":
    unittest.main()
