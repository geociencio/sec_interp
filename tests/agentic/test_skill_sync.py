"""Unit tests for skill_sync.py workflow loading and table generation."""

import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parents[2] / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

import skill_sync  # noqa: E402


class TestWriteTableBetweenMarkers(unittest.TestCase):
    def test_replaces_existing_region(self):
        content = "a\n<!-- S -->old<!-- E -->\nb"
        out = skill_sync._write_table_between_markers(
            content, "<!-- S -->", "<!-- E -->", "NEW"
        )
        self.assertIn("NEW", out)
        self.assertNotIn("old", out)

    def test_appends_when_no_markers(self):
        content = "just some text"
        out = skill_sync._write_table_between_markers(
            content, "<!-- S -->", "<!-- E -->", "NEW"
        )
        self.assertIn("NEW", out)
        self.assertTrue(out.startswith("just some text"))


class TestLoadWorkflows(unittest.TestCase):
    def test_loads_valid_workflows_and_skips_others(self):
        with tempfile.TemporaryDirectory() as d:
            base = Path(d)
            wf_dir = base / "workflows"
            wf_dir.mkdir()

            (wf_dir / "start-session.md").write_text(
                "---\ndescription: d\nagent: A\nskills: [s1]\n---\nbody\n"
            )
            (wf_dir / "index.md").write_text("# index")
            (wf_dir / "bad.md").write_text("---\ndescription: d\n---\n")

            workflows = skill_sync.load_workflows(base, wf_dir)

            self.assertEqual(len(workflows), 1)
            self.assertEqual(workflows[0]["name"], "start-session")
            self.assertEqual(workflows[0]["agent"], "A")
            self.assertEqual(workflows[0]["skills"], ["s1"])


if __name__ == "__main__":
    unittest.main()
