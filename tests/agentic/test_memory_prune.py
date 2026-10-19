"""Unit tests for memory_prune.py lesson and snapshot pruning."""

import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_ROOT / ".agent" / "tools"))
sys.path.insert(0, str(_ROOT / "scripts"))

import memory_prune as mp  # noqa: E402


class TestPruneNextStepsSnapshots(unittest.TestCase):
    def test_prunes_only_old_snapshots(self):
        with tempfile.TemporaryDirectory() as d:
            directory = Path(d)
            old = directory / "next_steps_2020-01-01.md"
            recent = directory / "next_steps_2999-01-01.md"
            old.write_text("# old")
            recent.write_text("# recent")

            removed = mp.prune_next_steps_snapshots(directory, apply=True)

            self.assertEqual(removed, 1)
            self.assertFalse(old.exists())
            self.assertTrue(recent.exists())

    def test_missing_directory_returns_zero(self):
        removed = mp.prune_next_steps_snapshots(Path("/nonexistent/dir"), apply=True)
        self.assertEqual(removed, 0)

    def test_non_snapshot_files_ignored(self):
        with tempfile.TemporaryDirectory() as d:
            directory = Path(d)
            (directory / "not_a_snapshot.md").write_text("# keep me")

            removed = mp.prune_next_steps_snapshots(directory, apply=True)

            self.assertEqual(removed, 0)
            self.assertTrue((directory / "not_a_snapshot.md").exists())


class TestPruneLessons(unittest.TestCase):
    """Only old, explicitly consolidated lessons may be pruned."""

    @staticmethod
    def _lessons_file(directory: Path) -> Path:
        path = directory / "AGENT_LESSONS.md"
        path.write_text(
            "# Lessons\n\n"
            "```yaml\n"
            "lessons:\n"
            "  - date: '2020-01-01'\n"
            "    category: TOOLING\n"
            "    topic: old consolidated lesson\n"
            "    lesson: old consolidated\n"
            "    action: none\n"
            "    consolidated_in: coding-standards\n"
            "  - date: '2020-01-02'\n"
            "    category: TOOLING\n"
            "    topic: old unmarked lesson\n"
            "    lesson: old unmarked\n"
            "    action: none\n"
            "  - date: '2999-01-01'\n"
            "    category: TESTING\n"
            "    topic: recent lesson\n"
            "    lesson: recent\n"
            "    action: none\n"
            "```\n"
        )
        return path

    def test_prunes_only_old_consolidated_lessons(self):
        with tempfile.TemporaryDirectory() as d:
            path = self._lessons_file(Path(d))
            with patch.object(mp, "LESSONS_FILE", path):
                pruned = mp.prune_lessons(apply=True, lessons_file=path)
            content = path.read_text()

        self.assertEqual(pruned, 1)
        self.assertIn("[PRUNED]", content)
        self.assertIn("old consolidated lesson", content)  # index line
        self.assertNotIn("consolidated_in", content)  # active entry removed
        self.assertIn("old unmarked lesson", content)
        self.assertIn("recent lesson", content)

    def test_missing_lessons_file_returns_zero(self):
        with patch.object(mp, "LESSONS_FILE", Path("/nonexistent/AGENT_LESSONS.md")):
            self.assertEqual(
                mp.prune_lessons(
                    apply=True, lessons_file=Path("/nonexistent/AGENT_LESSONS.md")
                ),
                0,
            )


class TestLessonLineLimit(unittest.TestCase):
    """The active log must stay under the policy budget."""

    def test_within_limit(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "AGENT_LESSONS.md"
            path.write_text("\n".join(["line"] * 350))
            within_limit, lines = mp.check_line_limit(path)

        self.assertTrue(within_limit)
        self.assertEqual(lines, 350)

    def test_over_limit(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "AGENT_LESSONS.md"
            path.write_text("\n".join(["line"] * 351))
            within_limit, lines = mp.check_line_limit(path)

        self.assertFalse(within_limit)
        self.assertEqual(lines, 351)

    def test_missing_file_reports_zero(self):
        within_limit, lines = mp.check_line_limit(Path("/nonexistent/AGENT_LESSONS.md"))
        self.assertTrue(within_limit)
        self.assertEqual(lines, 0)


if __name__ == "__main__":
    unittest.main()
