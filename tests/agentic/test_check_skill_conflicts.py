"""Unit tests for the skill-conflict detector and the lesson line budget."""

import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_ROOT / ".agent" / "tools"))
sys.path.insert(0, str(_ROOT / "scripts"))

import skill_conflicts as csc  # noqa: E402
import validate_agent_system as vas  # noqa: E402


def _skill(name, description="a description"):
    return {
        "name": name,
        "description": description,
        "dir": name,
    }


class TestFindConflicts(unittest.TestCase):
    def test_no_conflicts(self):
        skills = [
            _skill("a", "alpha"),
            _skill("b", "beta"),
        ]
        self.assertEqual(csc.find_conflicts(skills), [])

    def test_missing_field(self):
        skills = [{"name": "a", "dir": "a"}]
        issues = csc.find_conflicts(skills)
        self.assertTrue(any("description" in i for i in issues))

    def test_duplicate_name(self):
        skills = [_skill("dup", "one"), _skill("dup", "two")]
        issues = csc.find_conflicts(skills)
        self.assertTrue(any("duplicate skill name" in i for i in issues))

    def test_duplicate_description(self):
        skills = [
            _skill("a", "same description"),
            _skill("b", "same description"),
        ]
        issues = csc.find_conflicts(skills)
        self.assertTrue(any("duplicate description" in i for i in issues))


class TestMemoryLimit(unittest.TestCase):
    """The framework validator enforces the 350-line active-lesson budget."""

    def test_over_limit_returns_error(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "AGENT_LESSONS.md"
            path.write_text("\n".join(["line"] * 351))
            with patch.object(vas.forge_paths, "LESSONS_FILE", path):
                issues = vas.validate_memory_budget()

        self.assertEqual(len(issues), 1)
        self.assertEqual(issues[0].severity, "ERROR")
        self.assertIn("351", issues[0].message)

    def test_within_limit_returns_empty(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "AGENT_LESSONS.md"
            path.write_text("\n".join(["line"] * 350))
            with patch.object(vas.forge_paths, "LESSONS_FILE", path):
                issues = vas.validate_memory_budget()

        self.assertEqual(issues, [])


if __name__ == "__main__":
    unittest.main()
