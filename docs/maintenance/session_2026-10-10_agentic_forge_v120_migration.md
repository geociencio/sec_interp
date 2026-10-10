# Maintenance Session: 2026-10-10 - agentic-forge v1.2.0 Migration (Scoped Submodule + QGIS Domain Pack)

## Technical Summary

Aligned SecInterp's agentic system with the genericized **`agentic-forge`** framework
by bumping the `.agent/` submodule from `a77548b` (**v1.1.0**) to `2de22cf`
(**v1.2.0**), the same revision already pinned by the sibling projects
(`ai-context-core`, `qgis-plugin-manager`). The v1.2.0 core is **genericized**:
the QGIS-specific skills and workflows were extracted to `scaffold/qgis/`, so the
adoption requires **mounting the QGIS domain pack** into the project overlay
(`.agent-state/`) and repointing the root `AGENTS.md`.

## What changed in v1.2.0 (framework)

- **Skills**: moved `qgis-core`, `qgis-migration-4x`, `ui-framework` to
  `scaffold/qgis/skills/`; added the generic `testing-standards` skill.
- **Workflows**: moved `audit-plugin`, `release-plugin`, `run-tests-in-qgis` to
  `scaffold/qgis/workflows/`; added generic `audit-package` / `release-package`.
- Core workflows genericized (project commands become config/placeholders);
  `tools/` unchanged (still `forge.py`, `forge_paths.py`, `validate_agent_system.py`, ...).

## Changes Made

- **Submodule**: `.agent` `a77548b` → `2de22cf` (`v1.2.0`) via `git merge --ff-only origin/main`.
- **QGIS domain pack mounted** into the project overlay (documented `scaffold` →
  overlay pattern):
  - `.agent-state/skills/{qgis-core,qgis-migration-4x,ui-framework}`
  - `.agent-state/workflows/{audit-plugin,release-plugin,run-tests-in-qgis}.md`
- **`opencode.json`**: `skills.paths` now `[".agent/skills", ".agent-state/skills"]`
  so the overlay (including the mounted QGIS skills) is discoverable.
- **Root `AGENTS.md`**: repointed the 3 QGIS skills to `.agent-state/skills/...`,
  the 3 QGIS workflows to `.agent-state/workflows/...`, added `testing-standards`,
  and clarified the framework/overlay split in the intro, workflow section, skills
  section and "Key Resources".
- **Living docs fixed** (broken paths after the move): `gui/AGENTS.md`,
  `core/AGENTS.md`, `docs/research/TESTING_STRATEGIES.md`.
- **Stale CLI fixed**: `ai-ctx analyze .` → `ai-ctx analyze --path .` in
  `README_DEV.md` and `docs/docsec/DEVELOPMENT_GUIDE{,_EN}.md` (the positional
  form is rejected by `ai-ctx` 5.x).
- **`.agent-state/next_steps.md`**: marked the cross-repo framework-alignment
  pending item as done.

## Verification Results

- **Validation**: `python .agent/tools/forge.py validate` →
  **`Validated 14 skills, 14 workflows`** · `All .agent/ files pass system validation`.
- **Skills**: 9 framework + 5 overlay (2 project + 3 QGIS) = 14; all resolve.
- **Submodule**: `git submodule status .agent` → `2de22cf… (v1.2.0)`.
- **No dangling references** to the moved skills/workflows in living docs
  (historical `docs/maintenance/` and dated research snapshots left as-is).
- **No plugin code touched**: `core/`, `gui/`, `exporters/` unchanged.

## Impact

SecInterp now consumes the **same framework revision as its siblings** and owns
its QGIS domain pack as a project overlay, so future framework updates no longer
risk dropping the QGIS skills/workflows. The long-standing inconsistency
(`session_2026-10-08` claimed `.agent` @ `v1.2.0` while the pointer was actually
`a77548b`) is resolved.

## Notes / Follow-ups

- `opencode.json` config is loaded at startup: **restart opencode** for the new
  `skills.paths` to take effect.
- The genericized core workflows no longer embed project commands
  (`ai-ctx` / `qgis-analyzer`); the project keeps them in `forge.toml`
  (`analyzer_command`) and root `AGENTS.md`.
- Pending upstream (unchanged): promote `geological-logic` to `scaffold/geology`.
