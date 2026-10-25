"""Guards for the retired scheduled-release train.

The queue-driven releases (v3.9.1–v3.11.0) were retired on 2026-10-25; releases are
now cut manually from ``main``. These tests keep the automation from creeping back
without a deliberate decision.
"""

import unittest
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
_WORKFLOWS = _ROOT / ".github" / "workflows"
_SCHEDULE = _ROOT / "docs" / "releases" / "SCHEDULE.md"


class TestReleaseWorkflowRetired(unittest.TestCase):
    """The scheduled/queue release train must stay retired."""

    def test_scheduled_workflow_is_removed(self):
        self.assertFalse((_WORKFLOWS / "scheduled-release.yml").exists())

    def test_release_queue_is_removed(self):
        self.assertFalse((_ROOT / ".release-queue.json").exists())

    def test_selector_script_is_removed(self):
        self.assertFalse((_ROOT / "scripts" / "next_scheduled_release.py").exists())

    def test_schedule_doc_describes_manual_release(self):
        text = _SCHEDULE.read_text(encoding="utf-8")
        self.assertIn("Manual release checklist", text)
        self.assertIn("make pre-release", text)

    def test_no_workflow_references_the_retired_queue(self):
        for workflow in _WORKFLOWS.glob("*.yml"):
            text = workflow.read_text(encoding="utf-8")
            self.assertNotIn("next_scheduled_release", text, workflow.name)
            self.assertNotIn("release-queue", text, workflow.name)


if __name__ == "__main__":
    unittest.main()
