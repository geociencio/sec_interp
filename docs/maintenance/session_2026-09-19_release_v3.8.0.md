# Maintenance Session: 2026-09-19 - Release v3.8.0

## Technical Summary

Executed the full `/release-plugin` workflow to publish **SecInterp v3.8.0**, which
consolidates the Core/GUI decoupling refactor and ships two reliability fixes. The session
also cleaned a dirty working tree, synchronized every version reference and documentation
artefact, verified all quality gates, packaged the plugin, and published the GitHub release.

## Changes Made

### Pre-release cleanup
- Reverted generated/sample churn that was not part of the release:
  `resources/resources.py`, `examples/sample_data/MURALLA.qgs`, and `MURALLA.qgs~`.
- Committed the uncommitted tooling dependency bump `ai-context-core 3.3.0 → 3.4.0`
  (`pyproject.toml`, `uv.lock`) as `50a70ee`.
- Committed two analysis documents (`docs/qa/MANUAL_CODE_ANALYSIS.md`,
  `docs/maintenance/ai-context-core/developer_recommendations.md`) as `084ca3c8`.

### Versioning and documentation
- Bumped **3.7.2 → 3.8.0** in `metadata.txt`, `pyproject.toml`, `docs/source/conf.py`, and
  `uv.lock` (plus the `metadata.txt` changelog, with `%` escaped as `%%`).
- Updated `docs/CHANGELOG.md` (`[Unreleased]` → `[3.8.0] - 2026-09-19`).
- Back-filled `docs/docsec/CHANGELOG.md` (Spanish) with **3.7.1**, **3.7.2**, and **3.8.0**.
- Refreshed `README.md` badges (Version, QGIS 3.28+, QGIS Compliance 85.0, Code Quality
  99.9) and added the "What's New in v3.8.0" section.
- Updated `.agent/QUICK_REFERENCE.md` metrics (606 tests, maintainability 99.9, stability
  52.4, returns 99.7%, params 93.3%).
- Added the `docs/DEVELOPMENT_LOG.md` milestone entry and created
  `docs/releases/notes/v3.8.0.md`.
- Regenerated `AI_CONTEXT.md` via `uv run ai-ctx analyze`.

### Verification and publication
- Quality gates: **CC ≤ 10 PASS**, module stability 52.4, maintainability 99.9, security
  100.0, docstring 100%, type hints 93.3% params / 99.7% returns.
- Security: `make security-scan` PASS (Bandit + detect-secrets) and
  `qgis-analyzer security --deep` 0 vulnerabilities.
- Tests: **606/606 OK** in Docker.
- Release commit `4b7906cc` (`chore(release): prepare v3.8.0`), tag `v3.8.0`, pushed
  `main` + tag to `origin` (pre-push gate PASS).
- Packaged `dist/sec_interp.3.8.0.zip` (3.8 MB, 460 files, SHA256
  `cc7bb993e0b9e4a95922b5c0214975bc2c7538a1549b798757edb27fb29a784d`); strict ZIP audit
  found no `.agent`/`scripts`/`tests`/`docs`/`__pycache__` content.
- Published the GitHub release `v3.8.0` (now **Latest**) with the ZIP asset attached.

## Verification Results

- `make docker-test`: 606/606 OK
- `uv run qgis-analyzer analyze . --max-cc 10`: PASS
- `make security-scan`: PASS
- `uv run qgis-analyzer security --deep .`: 100/100 (0 vulnerabilities)
- `ruff` / pre-commit / pre-push gates: PASS

## Impact

SecInterp v3.8.0 is released and live on GitHub. The Core/GUI Extract-then-Compute boundary
is enforced (architecture allowlist 36 → 6) with no user-facing behavior change, and two
reliability fixes ship (QGIS 4 legend enum, 3D export default). The only remaining action is
the manual upload of the ZIP to plugins.qgis.org.
