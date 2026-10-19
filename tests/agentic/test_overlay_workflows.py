"""Tests for validating and graphing framework + overlay workflows."""

import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_ROOT / ".agent" / "tools"))
sys.path.insert(0, str(_ROOT / "scripts"))

import validate_agent_system as vas  # noqa: E402


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _workflow(skills: str = "qa-docker", extra: str = "") -> str:
    return (
        "---\n"
        "description: test workflow\n"
        "agent: qa_engineer\n"
        f"skills: [{skills}]\n"
        "---\n\n"
        "# Workflow\n"
        f"{extra}\n"
    )


class TestOverlayWorkflowValidation(unittest.TestCase):
    """The validator must scan .agent/workflows and .agent-state/workflows."""

    def _roots(self, directory: str) -> tuple[Path, Path]:
        root = Path(directory)
        framework = root / "framework" / "workflows"
        overlay = root / "state" / "workflows"
        framework.mkdir(parents=True)
        overlay.mkdir(parents=True)
        _write(framework / "start-session.md", _workflow())
        return framework, overlay

    def test_overlay_workflow_skill_is_validated(self):
        with tempfile.TemporaryDirectory() as d:
            framework, overlay = self._roots(d)
            _write(overlay / "release-plugin.md", _workflow("missing-skill"))
            issues = vas.validate_workflows({"qa-docker"}, set(), [framework, overlay])

        self.assertTrue(any("unknown skill" in issue.message for issue in issues))
        self.assertTrue(any("release-plugin.md" in issue.file for issue in issues))

    def test_overlay_missing_frontmatter_is_reported(self):
        with tempfile.TemporaryDirectory() as d:
            framework, overlay = self._roots(d)
            _write(overlay / "broken.md", "# no frontmatter\n")
            issues = vas.validate_workflows({"qa-docker"}, set(), [framework, overlay])

        self.assertTrue(any("Missing YAML frontmatter" in issue.message for issue in issues))

    def test_overlay_script_reference_is_validated(self):
        with tempfile.TemporaryDirectory() as d:
            framework, overlay = self._roots(d)
            _write(
                overlay / "scripted.md",
                _workflow(extra="```bash\npython scripts/not_a_real_script.py\n```"),
            )
            issues = vas.validate_workflows({"qa-docker"}, set(), [framework, overlay])

        self.assertTrue(any("unknown script" in issue.message for issue in issues))

    def test_duplicate_workflow_names_across_roots_are_reported(self):
        with tempfile.TemporaryDirectory() as d:
            framework, overlay = self._roots(d)
            _write(framework / "duplicate.md", _workflow())
            _write(overlay / "duplicate.md", _workflow())
            issues = vas.validate_workflows({"qa-docker"}, set(), [framework, overlay])

        self.assertTrue(any("Duplicate workflow name" in issue.message for issue in issues))


class TestOverlayWorkflowGraph(unittest.TestCase):
    """The dependency graph must include overlay workflows and skills."""

    def test_graph_includes_overlay_workflows(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            framework = root / "framework" / "workflows"
            overlay = root / "state" / "workflows"
            _write(framework / "start-session.md", _workflow())
            _write(overlay / "release-plugin.md", _workflow("qa-docker"))

            with patch.object(
                vas.forge_paths, "workflow_dirs", return_value=[framework, overlay]
            ):
                names = vas.get_all_workflows()
                nodes, broken = vas.scan_workflows()

        self.assertEqual(names, {"start-session", "release-plugin"})
        self.assertEqual({node.name for node in nodes}, {"start-session", "release-plugin"})
        self.assertEqual(broken, [])


if __name__ == "__main__":
    unittest.main()
