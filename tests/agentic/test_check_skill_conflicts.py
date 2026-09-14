"""Unit tests for the skill-conflict detector (now in validate_agent_system.py)."""

import sys
import unittest
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parents[2] / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

import validate_agent_system as csc  # noqa: E402


def _skill(name, description="a description", trigger="a trigger"):
    return {
        "name": name,
        "description": description,
        "trigger": trigger,
        "dir": name,
    }


class TestFindConflicts(unittest.TestCase):
    def test_no_conflicts(self):
        skills = [
            _skill("a", "alpha", "when writing code"),
            _skill("b", "beta", "when releasing"),
        ]
        self.assertEqual(csc.find_conflicts(skills), [])

    def test_missing_field(self):
        skills = [{"name": "a", "description": "d", "dir": "a"}]
        issues = csc.find_conflicts(skills)
        self.assertTrue(any("trigger" in i for i in issues))

    def test_duplicate_name(self):
        skills = [_skill("dup", "one", "t1"), _skill("dup", "two", "t2")]
        issues = csc.find_conflicts(skills)
        self.assertTrue(any("duplicate skill name" in i for i in issues))

    def test_duplicate_description(self):
        skills = [
            _skill("a", "same description", "t1"),
            _skill("b", "same description", "t2"),
        ]
        issues = csc.find_conflicts(skills)
        self.assertTrue(any("duplicate description" in i for i in issues))

    def test_trigger_overlap(self):
        skills = [
            _skill("a", "d1", "when using /foo"),
            _skill("b", "d2", "when using /foo"),
            _skill("c", "d3", "when using /foo"),
            _skill("d", "d4", "when using /foo"),
        ]
        issues = csc.find_conflicts(skills)
        self.assertTrue(any("/foo" in i for i in issues))

    def test_trigger_below_threshold_ok(self):
        skills = [
            _skill("a", "d1", "when using /foo"),
            _skill("b", "d2", "when using /foo"),
            _skill("c", "d3", "when using /foo"),
        ]
        issues = csc.find_conflicts(skills)
        self.assertFalse(any("/foo" in i for i in issues))


if __name__ == "__main__":
    unittest.main()
