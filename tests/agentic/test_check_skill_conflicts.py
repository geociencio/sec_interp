"""Unit tests for the skill-conflict detector (now in validate_agent_system.py)."""

import sys
import unittest
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_ROOT / ".agent" / "tools"))
sys.path.insert(0, str(_ROOT / "scripts"))

import validate_agent_system as csc  # noqa: E402


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


if __name__ == "__main__":
    unittest.main()
