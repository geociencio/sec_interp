---
description: Unified Release Workflow (QGIS Release Flow) - Generation 6 Standard
agent: qa_engineer
skills: [release-management, qa-docker, commit-standards, i18n-standards, changelog-generator]
stop_conditions:
  - "Any function exceeds CC > 10 → Block release and refactor"
  - "Docstring coverage < 100% → Block release and fix documentation"
  - "Forbidden files (.agent, scripts, tests) found in ZIP → Abort and fix .qgisignore"
  - "make security-scan reports CRITICAL findings (Bandit/detect-secrets) → Block release and fix before packaging"
validation: |
  - Verify that 616+ tests pass in Docker
  - Confirm CC <= 10 for all methods (qgis-analyzer --max-cc 10)
  - Ensure Zero High-Severity Security Findings
  - Validate ZIP contents (Plugin-only, no agentic system)
---

# Workflow: Release Plugin (Gen 6)

Follow this 5-phase workflow to perform an official release of the SecInterp plugin.

### Phase 1: Quality and Preparation

1. **Operational Audit**:
   // turbo
   ```bash
   uv run python scripts/sync_metrics.py --report
   uv run qgis-analyzer analyze . --max-cc 10
   ```
   🤖 **Agent Action**: Verify CC <= 10 and 100% docstring/return-type coverage.

2. **Full Analysis**:
   // turbo
   ```bash
   uv run qgis-analyzer analyze . -o analysis_results
   ```
   🤖 **Agent Action**: Update badges in `README.md` based on current scores.

### Phase 2: Versioning and Documentation

1. **Synchronize Version (vX.Y.Z)** — full checklist:

   | # | File | What to update |
   |:--|:-----|:--------------|
   | 1 | `metadata.txt` | `version` + `changelog` (escape `%` as `%%`) |
   | 2 | `pyproject.toml` | `version` |
   | 3 | `README.md` | badges (Version, Quality, Tests) + "What's New" |
   | 4 | `docs/CHANGELOG.md` | move `[Unreleased]` → `[X.Y.Z]` + date |
   | 5 | `docs/docsec/CHANGELOG.md` | same (Spanish changelog) |
   | 6 | `docs/source/conf.py` | `release = "X.Y.Z"` |
   | 7 | `docs/releases/notes/v[X.Y.Z].md` | new release note |
   | 8 | `docs/DEVELOPMENT_LOG.md` | milestone entry |
   | 9 | `.agent/QUICK_REFERENCE.md` | test count + metrics |

   🤖 **Agent Action**: Validate that `metadata.txt`, `pyproject.toml`, and
   `docs/source/conf.py` versions match exactly.

2. **Changelog Update**:
   - Use **changelog-generator** to move `[Unreleased]` to the new version in `docs/CHANGELOG.md`.
   - Add a summary of the Phase achievements.

3. **Generate Release Notes**:
   - Create `docs/releases/notes/v[VERSION].md` with a descriptive and professional title (English required).
   - Use the **changelog-generator** skill to transform technical commits into user-facing value.

4. **Development Log Milestone**:
   - Add a milestone entry in `docs/DEVELOPMENT_LOG.md` summarizing the phase closure.

5. **Documentation Audit**:
   - Ensure `AGENTS.md` (root SSoT), `.agent/QUICK_REFERENCE.md`, and other core
     docs reflect the latest architectural changes or standards.
   - Regenerate `AI_CONTEXT.md` via `uv run ai-ctx analyze`.

### Phase 3: Final Verification (Safety Net)

1. **Security Scan (CRITICAL — includes Bandit)**:
   // turbo
   ```bash
   make security-scan
   ```
   // turbo
   ```bash
   uv run qgis-analyzer security --deep .
   ```

   🤖 **Agent Action**: `make security-scan` runs **Bandit** (`B110 try_except_pass`, hardcoded passwords, unsafe functions, etc.), **detect-secrets**, and **Flake8** via `scripts/security_scan.py`. It exits non-zero on any CRITICAL finding. Do NOT proceed to packaging if it fails. This is the full scan that catches code smells the `qgis-analyzer security` secrets-only check does not.

2. **Tests (Full Suite)**:
   // turbo
   ```bash
   make docker-test
   ```
   🤖 **Agent Action**: 100% pass rate required (616 tests).

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
   gh release create vX.Y.Z --title "vX.Y.Z" --notes-file docs/releases/notes/vX.Y.Z.md dist/*.zip --draft
   ```

## Expected Result
- Official version published (Plugin-only ZIP).
- Zero technical debt regressions.
- Sincronized metrics and documentation.
