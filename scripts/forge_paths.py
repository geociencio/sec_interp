#!/usr/bin/env python3
"""Resolve Agentic Forge paths for the current project.

Loads ``forge.toml`` from the repository root and exposes the framework
content directory (``.agent``) and the project-state directory
(``.agent-state``). Centralising path resolution here lets the tooling run
against any project and prepares the extraction of the generic tooling into
the ``agentic-forge`` framework.

The config file is discovered by walking up from this module's location, so it
keeps working after the tooling is moved under ``.agent/tools/``.
"""

from __future__ import annotations

from pathlib import Path

import tomllib

_CONFIG_NAME = "forge.toml"


def _find_project_root(start: Path) -> Path:
    """Return the nearest ancestor of ``start`` that contains ``forge.toml``."""
    for candidate in (start, *start.parents):
        if (candidate / _CONFIG_NAME).is_file():
            return candidate
    # Legacy fallback: this module used to live in <root>/scripts/.
    return start.resolve().parent.parent


def _load_config(root: Path) -> dict:
    config_path = root / _CONFIG_NAME
    if not config_path.is_file():
        return {}
    with config_path.open("rb") as handle:
        return tomllib.load(handle)


PROJECT_ROOT = _find_project_root(Path(__file__).resolve().parent)
_CONFIG = _load_config(PROJECT_ROOT)
_FORGE = _CONFIG.get("forge", {})

# Framework content (re-usable; may become a git submodule).
FRAMEWORK_DIR = PROJECT_ROOT / _FORGE.get("framework", ".agent")
SKILLS_DIR = FRAMEWORK_DIR / "skills"
WORKFLOW_DIR = FRAMEWORK_DIR / "workflows"
RESOURCES_DIR = FRAMEWORK_DIR / "resources"

# Project-owned state (never shipped by the framework).
STATE_DIR = PROJECT_ROOT / _FORGE.get("state", ".agent-state")
MEMORY_DIR = STATE_DIR / "memory"
HISTORY_DIR = STATE_DIR / "history"
METRICS_FILE = MEMORY_DIR / "agent_metrics.json"
LESSONS_FILE = MEMORY_DIR / "AGENT_LESSONS.md"
MEMORY_POLICY_FILE = MEMORY_DIR / "memory_policy.md"
TASK_FILE = STATE_DIR / "task.md"
NEXT_STEPS_FILE = STATE_DIR / "next_steps.md"

# Project-specific skills (overlay on top of the framework skills).
OVERLAY_SKILLS_DIR = STATE_DIR / "skills"


def state_and_framework_dirs() -> list[Path]:
    """Return the directories that make up the agentic system (existing only)."""
    return [directory for directory in (FRAMEWORK_DIR, STATE_DIR) if directory.exists()]


def skill_dirs() -> list[Path]:
    """Return every skill root (framework + project overlay), existing only."""
    return [d for d in (SKILLS_DIR, OVERLAY_SKILLS_DIR) if d.is_dir()]


def agent_roots() -> list[Path]:
    """Return the roots used to render agentic paths in reports."""
    return [d for d in (FRAMEWORK_DIR, STATE_DIR) if d.exists()]
