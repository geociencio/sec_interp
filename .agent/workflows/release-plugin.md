---
description: Unified Release Workflow (QGIS Release Flow) - Generation 6 Standard
agent: QA Engineer
skills: [release-management, qa-docker, commit-standards, i18n-standards, changelog-generator]
stop_conditions:
  - "Any function exceeds CC > 10 → Block release and refactor"
  - "Docstring coverage < 100% → Block release and fix documentation"
  - "Forbidden files (.agent, scripts, tests) found in ZIP → Abort and fix .qgisignore"
validation: |
  - Verify that 620+ tests pass in Docker
  - Confirm CC <= 10 for all methods (scripts/check_cc.py)
  - Ensure Zero High-Severity Security Findings
  - Validate ZIP contents (Plugin-only, no agentic system)
---

# Workflow: Release Plugin (Gen 6)

Follow this 5-phase workflow to perform an official release of the SecInterp plugin.

### Fase 0: Semantic Injection
Optimize the current context for release operations.
// turbo
```bash
uv run python scripts/context_selector.py "release preparation and packaging" --shell
```

### Phase 1: Quality and Preparation

1. **Operational Audit**:
   // turbo
   ```bash
   uv run python scripts/metrics_report.py
   uv run python scripts/check_cc.py
   ```
   🤖 **Agent Action**: Verify CC <= 10 and 100% docstring/return-type coverage.

2. **Full Analysis**:
   // turbo
   ```bash
   uv run qgis-analyzer analyze . -o analysis_results
   ```
   🤖 **Agent Action**: Update badges in `README.md` based on current scores.

### Phase 2: Versioning and Documentation

1. **Synchronize Version (vX.Y.Z)**:
   - Update `metadata.txt`: `version` and `changelog` (Escape `%` as `%%`).
   - Update `pyproject.toml`: `version`.
   - Update `README.md`: Version badge and "What's New" section.

   🤖 **Agent Action**: Validate that all 3 versions match exactly.

2. **Changelog Rotation**:
   - Use **changelog-generator** to move `[Unreleased]` to the new version in `docs/CHANGELOG.md`.
   - Add a summary of the Phase v3.5.0 achievements (100% Docstrings, Gen 6 Autonomy).

### Phase 3: Final Verification (Safety Net)

1. **Security Scan**:
   // turbo
   ```bash
   uv run qgis-analyzer security --deep .
   ```

2. **Tests (Full Suite)**:
   // turbo
   ```bash
   make docker-test
   ```
   🤖 **Agent Action**: 100% pass rate required (620 tests).

### Phase 4: Git and Tagging

1. **Release Commit**:
   ```bash
   git add metadata.txt pyproject.toml docs/CHANGELOG.md README.md
   git commit -m "chore(release): prepare vX.Y.Z"
   ```

2. **Tagging**:
   ```bash
   git tag -a vX.Y.Z -m "Release vX.Y.Z"
   git push origin main && git push origin vX.Y.Z
   ```

### Phase 5: Packaging and Distribution (PLUGIN ONLY)

1. **Clean Memory**:
   // turbo
   ```bash
   uv run python scripts/memory_prune.py
   ```

2. **Build Optimized ZIP**:
   // turbo
   ```bash
   make package VERSION=main
   ```

3. **Strict Artifact Audit**:
   // turbo
   ```bash
   unzip -l dist/*.zip | grep -E "\.agent|scripts|tests|docs|AI_CONTEXT|antigravity"
   ```
   🤖 **Agent Action**: **STOP** if the output is not empty. The agentic system MUST NOT be in the ZIP.

4. **GitHub Release**:
   ```bash
   gh release create vX.Y.Z --title "vX.Y.Z" --notes-file docs/releases/RELEASE_NOTES_vX.Y.Z.md dist/*.zip --draft
   ```

## Expected Result
- Official version published (Plugin-only ZIP).
- Zero technical debt regressions.
- Sincronized metrics and documentation.
