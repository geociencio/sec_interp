"""Unit tests for memory_prune.py next_steps snapshot pruning."""

import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parents[2] / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

import memory_prune as mp  # noqa: E402


class TestPruneNextStepsSnapshots(unittest.TestCase):
    def test_prunes_only_old_snapshots(self):
        with tempfile.TemporaryDirectory() as d:
            directory = Path(d)
            old = directory / "next_steps_2020-01-01.md"
            recent = directory / "next_steps_2999-01-01.md"
            old.write_text("# old")
            recent.write_text("# recent")

            removed = mp.prune_next_steps_snapshots(directory)

            self.assertEqual(removed, 1)
            self.assertFalse(old.exists())
            self.assertTrue(recent.exists())

    def test_missing_directory_returns_zero(self):
        removed = mp.prune_next_steps_snapshots(Path("/nonexistent/dir"))
        self.assertEqual(removed, 0)

    def test_non_snapshot_files_ignored(self):
        with tempfile.TemporaryDirectory() as d:
            directory = Path(d)
            (directory / "not_a_snapshot.md").write_text("# keep me")

            removed = mp.prune_next_steps_snapshots(directory)

            self.assertEqual(removed, 0)
            self.assertTrue((directory / "not_a_snapshot.md").exists())


if __name__ == "__main__":
    unittest.main()
