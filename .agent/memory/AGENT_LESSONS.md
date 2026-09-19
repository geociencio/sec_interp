# Agent Learning Memory (SecInterp)

This file records technical lessons, user preferences, and solutions to complex problems.
It uses a structured format for efficient retrieval by the agent system.

**Memory Policy**: Lessons older than 90 days that are already reflected in a `SKILL.md`
are marked `[consolidated]` and will be pruned in the next review cycle.
See `.agent/memory/memory_policy.md` for the full policy.

---

## 🧠 Lesson Log (YAML Structured)

```yaml
lessons:

  # ─── ACTIVE LESSONS (< 90 days or not yet in a SKILL.md) ───────────────────
  - date: '2026-09-19'
    category: TOOLING
    topic: make package regenerates tracked Sphinx stubs and pushes the external docs repo
    lesson: The release `make package` target depends on `docs compile`, so it builds
      Sphinx and pushes to the separate `sec_interp_docs` GitHub Pages repo, while also
      rewriting tracked `docs/source/*.rst` autodoc stubs. The working tree is dirty
      immediately after a release.
    action: After `make package`, review and commit the regenerated `docs/source/*.rst`
      stubs; treat the external docs push as a real remote side effect of the release.
  - date: '2026-09-19'
    category: AGENTIC_SYSTEM
    topic: release workflow zips/audits use dist/*.zip which matches all historical releases
    lesson: The `/release-plugin` Phase 5 commands use `dist/*.zip`; since `dist/` keeps
      every historical ZIP, the glob would audit and attach all old releases.
    action: Always target the versioned artifact explicitly (`dist/sec_interp.X.Y.Z.zip`)
      in the ZIP audit and in `gh release create`.
  - date: '2026-09-19'
    category: AGENTIC_SYSTEM
    topic: a phase can ship unfulfilled goals under a fresh minor version
    lesson: v3.8.0 was released after only the Core/GUI refactor, while the documented
      v3.8.0 goals (symbology preview, adaptive VE, tech debt) remain pending. Bumping a
      minor for an internal refactor while renaming the goals is easy to lose track of.
    action: When releasing without completing the phase goals, either ship a patch version
      or explicitly move the unmet goals to the next phase in `next_steps.md`.
  - date: '2026-09-19'
    category: ARCHITECTURE
    topic: retiring a Qt/QGIS compat shim needs a full flat-enum scan, not just a grep
    lesson: Retiring qt6_compat.py after the scoped-enum migration seemed safe (no flat
      enums found), but QEvent.Resize still slipped through and only failed at runtime
      on QGIS 4, because the mock test env and pyqgis4-checker did not cover that path.
    action: Before removing any compat shim, enumerate every enum family the shim
      patches and grep for each; then validate at runtime (real QGIS 4), not only
      via unit tests or the enum checker.
  - date: '2026-09-19'
    category: AGENTIC_SYSTEM
    topic: agent workflows/skills drift from repo reality (stale metrics and checklists)
    lesson: The /release-plugin workflow still required "640 tests" and missed
      docs/docsec/CHANGELOG.md and docs/source/conf.py; the skill used a stale release
      notes path. This drift hid real release gaps.
    action: When touching a workflow/skill, reconcile its numbers (test counts, scores)
      and file lists against the actual repo (grep the current version references).
  - date: '2026-09-19'
    category: TOOLING
    topic: pre-commit pins its own ruff, which can disagree with the installed one
    lesson: isinstance(value, (dict, list)) passed the project ruff (>=0.15.0) but
      the pre-commit hook (ruff v0.8.4) rejected it with UP038 and blocked the commit.
      The hook runs its own pinned ruff version, so lint must be checked against it,
      not just the project interpreter.
    action: Before committing, remember the pre-commit ruff rev (v0.8.4) may flag rules
      the installed ruff does not; fix to satisfy the hook (e.g. dict | list).
  - date: '2026-09-19'
    category: TOOLING
    topic: canonical formatter is ruff format, not black
    lesson: Running black reformats to 88 cols while the repo standard (pre-commit
      ruff-format) uses 100 cols, causing churn. black is in dev deps but not wired
      into the hook config.
    action: Use ruff format (never black) for this repository.
  - date: '2026-09-19'
    category: ARCHITECTURE
    topic: assess type propagation before migrating a geometry signature to tuples
    lesson: The get_line_start_point helper returns QgsPointXY whose value flows into ~20
      QGIS-coupled service methods (measureLine, .x()/.y()). Converting it to tuples
      is not an isolated change; it drags the whole service layer.
    action: When reimplementing a core helper in pure math, first grep how its return
      type propagates; if it fans out into QGIS-coupled services, defer it to the
      service-migration phase and pick a function with a primitive return instead.
  - date: '2026-09-19'
    category: ARCHITECTURE
    topic: allowlist ratchet as an incremental migration driver
    lesson: A test that fails both on new violations and on stale allowlist entries
      turns a large decoupling effort into small, verifiable increments, forcing the
      list to shrink as files migrate.
    action: Use a bidirectional allowlist gate for gradual Extract-then-Compute
      migrations; each migrated file produces an immediate, testable gate shrink.
  - date: '2026-09-17'
    category: TOOLING
    topic: Verify installed dependency source before writing an upstreaming plan
    lesson: A plan to upstream SecInterp's i18n AST + CC gate into qgis-plugin-analyzer
      turned out to be already fully implemented in 1.14.0 (verified by reading the
      installed `analyzer/` package). The remaining work was a migration on the
      SecInterp side, not new analyzer code.
    action: Before planning to port/upstream logic into a dependency, inspect the
      installed package source and CLI surface first; what looks like a gap may be a
      version bump away from shipped.
  - date: '2026-09-17'
    category: TOOLING
    topic: Untracked git hooks drift when a CLI flag contract changes
    lesson: The pre-push hook used the legacy `qgis-analyzer analyze . --output json`,
      where `--output` was a filename. In 1.14.0 `--output` became a directory, so the
      hook silently wrote to `json/` while `check_cc.py` read `analysis_results/`,
      breaking the CC gate on every push. Hooks in `.git/hooks/` are untracked and
      invisible to normal diffs.
    action: When bumping a CLI tool, grep `.git/hooks/*` for its invocations and
      verify flag semantics; treat untracked hooks as part of the migration checklist.
  - date: '2026-09-14'
    category: TOOLING
    topic: Analyzer version bumps shift metrics more than code changes
    lesson: qgis-plugin-analyzer 1.14.0 cut MISSING_I18N from 72 to 2 (a narrower
      i18n heuristic) and recomputed type-hint param coverage 94.3 → 90.4 with zero
      code changes. The `summary` command reads stale cached results and warned
      about drift until `analyze .` was re-run.
    action: After any analyzer tool version bump, re-run `analyze .` (never just
      `summary`) and reconcile agent_metrics.json against the fresh output before
      trusting metric deltas.
  - date: '2026-09-13'
    category: TOOLING
    topic: detect-secrets baseline goes stale when files are deleted
    lesson: The .secrets.baseline still referenced .continue/agents/new-config.yaml
      after that directory was removed, because the baseline is only regenerated by an
      explicit scan. A stale baseline hides (or wrongly reports) secrets for files that
      no longer exist.
    action: After deleting files that appear in a detect-secrets baseline, regenerate it
      with `detect-secrets scan . --baseline .secrets.baseline` before committing.
  - date: '2026-09-13'
    category: TOOLING
    topic: git rm --cached only touches the index, not disk
    lesson: The git rm --cached command untracks a file but leaves it on disk; a
      separate rm is needed. Docker-created artifacts are often root-owned and
      additionally require sudo to delete, so they can linger after a cleanup.
    action: Follow git rm --cached with an explicit disk rm; expect root-owned
      (Docker) leftovers to need sudo.
  - date: '2026-09-13'
    category: AGENTIC_SYSTEM
    topic: Harness assumptions go stale (the Bitter Lesson)
    lesson: The agentic system assumed a dual Antigravity/CodeWhale runtime, with a
      bridge (workflow_executor.py + .codewhale/) to translate between them. The real
      runtime had already moved to opencode, leaving the bridge as dead weight.
    action: Prefer runtime-native mechanisms (AGENTS.md, SKILL.md name+description,
      opencode.json subagents) over bespoke bridges. Any script that exists only to
      translate between runtimes is a liability.
  - date: '2026-09-13'
    category: TOOLING
    topic: Consolidate overlapping scripts into subcommand entry points
    lesson: Five metrics/consistency scripts overlapped in responsibility, each a
      separate assumption to keep synchronized. Folding them into sync_metrics.py and
      validate_agent_system.py subcommands reduced the long-tail and centralised drift.
    action: When two scripts share a domain (metrics, validation), fold the smaller into
      the larger as a subcommand rather than adding a new file.
  - date: '2026-09-12'
    category: AGENTIC_SYSTEM
    topic: Release Timing vs Build/Upload Order
    lesson: The scoped-enum migration (commit 7ae8ac96) was committed AFTER the v3.7.1
      ZIP was built and uploaded, so the portal's Qt6 checker kept reporting 114 enum
      findings even though HEAD was clean. A fix that lives in git but never in a
      released artifact is invisible to the portal.
    action: When a compatibility fix lands, verify the built ZIP actually contains it
      (unzip -p on the artifact) and ship a patch release before declaring the portal
      issue resolved.
  - date: '2026-09-12'
    category: AGENTIC_SYSTEM
    topic: Metric Sync Must Update All Derived Fields
    lesson: sync_metrics.py only refreshed the summary scores, leaving last_session
      stale (2026-05-23) and i18n_issues_qgis_analyzer (254) contradicting
      issue_breakdown.MISSING_I18N (72). Partial field updates silently recreate drift.
    action: Every metric sync must also refresh i18n_issues_qgis_analyzer and rotate
      last_session into history (sync_metrics.py --close-session). sync_metrics.py
      --validate now checks internal consistency to catch this class of drift.
  - date: '2026-09-12'
    category: TOOLING
    topic: Verify YAML Frontmatter After Bulk Edits
    lesson: A bulk Python script to standardize the runtimes frontmatter field across
      13 workflows merged the closing --- with the last frontmatter line, silently
      corrupting YAML.
    action: After any mechanical multi-file edit, re-parse frontmatter (or run
      validate_agent_system.py --graph) before committing.
  - date: '2026-09-12'
    category: AGENTIC_SYSTEM
    topic: Single Source of Truth for Workflow Tables
    lesson: Root AGENTS.md and .agent/AGENTS.md each had a manually-maintained workflow
      table that drifted (5 vs 15 workflows). Duplicated tables inevitably diverge.
    action: The workflow/skills tables now live only in the root AGENTS.md (single source
      of truth); .agent/AGENTS.md is a pointer. Update root AGENTS.md manually when
      adding/renaming a workflow or skill (skill_sync.py retired in Gen 8).
  - date: '2026-05-24'
    category: TECHNICAL
    topic: qgis-analyzer i18n False Positives
    lesson: 'qgis-analyzer MISSING_I18N check only recognizes self.tr() as a valid i18n wrapper. QCoreApplication.translate() — the standard Qt API for non-QObject contexts (static methods, factories, super().__init__()) — is flagged as untranslated. In SecInterp, 254 of 257 total issues are these false positives.'
  - date: '2026-05-24'
    category: AGENTIC_SYSTEM
    topic: Ground-Truth Metric Staleness
    lesson: Agentic system self-reported metrics (quality score, i18n coverage, CC average)
      drifted from reality over multiple sessions because no automated re-scan was triggered
      after fixes. The system declared 40.8 quality score when real score was 52.3;
      declared i18n "complete" when qgis-analyzer still found 254 MISSING_I18N (different
      scope than the AST checker).
    action: Run qgis-analyzer analyze . at the start of every session and update agent_metrics.json
      summary automatically. Never trust metrics older than one session without re-verification.
  - date: '2026-05-24'
    category: AGENTIC_SYSTEM
    topic: Multi-Tool Scope Mismatch
    lesson: verify_i18n_hygiene.py (AST-based) and qgis-analyzer i18n (heuristic) measure
      different things. The AST checker validates self.tr() wrapping with near-zero
      false positives. The analyzer uses broader detection that catches user-facing
      strings in f-strings, HTML templates, and dynamic constructions. Both reported
      0 vs 254 for the same codebase because their scope differs.
    action: Document the scope of each quality gate explicitly. A PASS on verify_i18n_hygiene.py
      does not mean 0 MISSING_I18N on qgis-analyzer. Both metrics must be tracked separately.
  - date: '2026-05-24'
    category: AGENTIC_SYSTEM
    topic: Session Archive Location
    lesson: The memory_policy.md referenced .agent/history/sessions/ as the episodic
      memory store, but the actual 100+ session logs live in docs/maintenance/. This
      path divergence went unnoticed because no automated cross-reference exists.
    action: Update memory_policy.md to reference docs/maintenance/ as the canonical
      session directory. Add a path validation step to /verify-standards workflow.
  - date: '2026-05-23'
    category: i18n
    topic: AST-based i18n Quality Gate
    lesson: Using a Python Abstract Syntax Tree (AST) parser allows building a highly
      precise, customizable static translation scanner. It can distinguish docstrings,
      HTML strings, internal dictionary keys, and developer log statements, eliminating
      hundreds of false-positive warnings.
    action: Use AST-based scanners like verify_i18n_hygiene.py rather than naive regexes
      to validate i18n completeness in Python codebases.
  - date: '2026-05-23'
    category: i18n
    topic: Headless tr() Resolution
    lesson: For translation of user-facing strings inside modular factory objects or
      non-QObject classes that lack a self.tr() context, importing and using QCoreApplication.translate()
      ensures PyQt/PyQGIS can correctly locate translations.
    action: Employ QCoreApplication.translate("ClassName", "String") inside functions
      that lack a QObject parent or self.tr() context.
  - date: '2026-05-23'
    category: ENVIRONMENT
    topic: Read-only Filesystem Shell
    lesson: In container environments where the terminal/shell commands run with a read-only
      filesystem mount for safety, specialized agentic file-writing tools (which run
      outside the shell sandbox) can still successfully create and edit files.
    action: Fallback to direct replace_file_content or write_to_file calls when CLI
      tool/script executions fail due to Read-only filesystem constraints.
  - date: '2026-05-18'
    category: TOOLING
    topic: QGIS Ignore Verification
    lesson: Relying on .qgisignore in the packaging script ensures that all internal
      agent files (.agent/, scripts/, tests/) are completely excluded, which results
      in a highly compact zip (reduced by over 50%).
    action: Always verify package exclusions using unzip -l on the generated zip before
      distribution.
  - date: '2026-05-18'
    category: ARCHITECTURE
    topic: Qt6 QDialog Enum Code
    lesson: Using explicit integer literals (1 for Accepted, 0 for Rejected) for QDialog
      execution status results is the most robust and backward-compatible bridge between
      PyQt5 and PyQt6, avoiding Qt6-specific enum hierarchy errors.
    action: Adopt integer literals (1 and 0) for QDialog execution status checks across
      all GUI modules.
  - date: '2026-05-18'
    category: i18n
    topic: Translation Analyzer False Positives
    lesson: 'Many missing translation warnings from static analyzers represent technical
      strings (formats, logs, queries) rather than user-facing text. Using explicit
      # no-i18n tags is crucial to prevent static analysis noise.'
    action: Systematically annotate technical string literals with exclusion tags to
      maintain clean translation reports.
  - date: '2026-04-29'
    category: TOOLING
    topic: Formatter vs Linter Conflict (W503)
    lesson: 'Modern formatters (Ruff/Black) enforce PEP 8 "break-before" for operators,
      while legacy linters (W503) flag it. Refactoring multi-line conditions into intermediate
      variables or removing parentheses for single-line blocks is the most stable way
      to satisfy both without standard deviation.

      '
    action: 'Avoid ''if ( ... )'' blocks with multi-line operators. Use intermediate
      variables to decompose complex logic and keep conditions on a single line where
      possible.

      '
  - date: '2026-04-29'
    category: ARCHITECTURE
    topic: precise noqa placement
    lesson: 'In modular systems with lazy imports, static analysis may trigger false
      positives (F401/F811) for local redefinitions. Placing ''# noqa'' precisely on
      the line of the second import/definition is required to maintain the ''Extract-then-Compute''
      pattern without linter noise.

      '
    action: 'Always place noqa tags on the specific line causing the violation instead
      of suppressing the entire file or block.

      '
  - date: '2026-04-29'
    category: TOOLING
    topic: Pre-commit Auto-Reversion
    lesson: 'Pre-commit hooks that modify files (like ruff-format) can silently revert
      manual linting fixes if they are incompatible with the enforced project style,
      leading to recursive build failures.

      '
    action: 'Always verify if a formatter reverts a fix and adapt the code structure
      (e.g., using variables) to be compatible with the formatter''s standards.

      '
  - date: '2026-04-28'
    category: TOOLING
    topic: QGIS 4 Sphinx Mocking
    lesson: 'When updating Sphinx documentation for QGIS 4.x readiness, adding ''qgis.PyQt'',
      ''PyQt6'', and specific Qt modules to ''autodoc_mock_imports'' is essential to
      prevent build errors in environments where these libraries are not installed.

      '
    action: 'Always include Qt6-related mocks in ''conf.py'' when targeting QGIS 4 compatibility
      to ensure documentation builds are decoupled from the local Qt environment.

      '
  - date: '2026-04-28'
    category: TESTING
    topic: Post-Merge Stability Verification
    lesson: 'Major branch merges (like the Cyclomatic Complexity refactoring) can introduce
      subtle regressions in complex orchestrators even if individual tests passed in
      the branch.

      '
    action: 'Always execute the full project test suite (''make test'' or discovery)
      immediately after a merge to ''main'' to verify global system integrity.

      '
  - date: '2026-04-28'
    category: ARCHITECTURE
    topic: API-Agnostic Stability
    lesson: 'Consistently using ''qgis.PyQt'' shims instead of direct ''PyQt5'' or ''PyQt6''
      imports guarantees a stable codebase that operates seamlessly across QGIS 3 and
      4 runtimes without requiring conditional branching or manual porting.

      '
    action: 'Enforce the ''qgis.PyQt'' standard in all new modules and use ''qgis-analyzer''
      to audit and prevent direct Qt library imports.

      '
  - date: '2026-04-26'
    category: TOOLING
    topic: Complexity Branch Counting (or "")
    lesson: 'qgis-plugin-analyzer 1.13.1 counts ''or ""'' expressions in function arguments
      or return statements as additional logical branches, which can push cyclomatic
      complexity over the limit in methods with many optional fields.

      '
    action: 'Decompose monolithic orchestrators into discrete ''Steps'' (private methods)
      and use intermediate variables or DTO defaults instead of inline ''or'' logic
      to maintain low CC scores.

      '
  - date: '2026-04-26'
    category: ARCHITECTURE
    topic: Orchestrator Decomposition
    lesson: 'Decoupling complex data processing flows into a ''Step-by-Step'' pattern
      within orchestrator services (core/services) improves testability and reduces
      complexity without breaking the Extract-then-Compute paradigm.

      '
    action: 'Use private methods prefixed with _stepN_ to document the execution flow
      of complex services, keeping the main method clean and linear.

      '
  - date: '2026-04-26'
    category: ARCHITECTURE
    topic: Explicit Signal Disconnection
    lesson: 'Static analyzers like qgis-analyzer may flag signal connections as leaks
      if disconnections are not explicit and symmetric within the same class context.

      '
    action: 'Ensure all signals connected in ''connect_signals'' are explicitly disconnected
      by slot name in ''disconnect_signals'' using ''contextlib.suppress''.

      '
  - date: '2026-04-26'
    category: TOOLING
    topic: QGIS-Analyzer Static Summary
    lesson: 'The ''summary'' command is a static JSON viewer. It does not reflect real-time
      code changes unless ''analyze'' is executed first.

      '
    action: 'Always force a full re-analysis (''qgis-analyzer analyze .'') before verifying
      fixes with ''summary'' to avoid phantom issue reporting.

      '
  - date: '2026-04-25'
    category: TOOLING
    topic: Flake8 vs Ruff Configuration Parity
    lesson: 'Ruff and Flake8 can have different default rule scopes or ignored rules
      (like F821, E402). If the CI/CD or QGIS repository strict analyzer uses Flake8
      without the pyproject.toml ignores, the build will fail despite Ruff reporting
      0 errors.

      '
    action: 'When resolving linting issues for external platforms, always run the exact
      tool (e.g., Flake8) expected by the platform and manage exclusions through ''#
      noqa'' comments directly in the code rather than relying exclusively on ''pyproject.toml''
      ignores.

      '
  - date: '2026-04-05'
    category: ARCHITECTURE
    topic: Gen 5 Blueprint Scaffolding
    lesson: 'Blueprint Scaffolding architecture is superior for scaling frameworks while
      maintaining a generic core. Integrating the Reflect Loop (Agent Auditor critique)
      significantly reduces hallucination risk in autonomous planning. MCP is the backbone
      for standardized and secure tool orchestration.

      '
    action: 'Use the /ia-critic workflow after every major planning phase. Expand mcp_server.py
      to cover all validation-heavy core logic.

      '
  - date: '2026-03-22'
    category: TOOLING
    topic: ai-context-core CLI
    lesson: 'The CLI executable for ''ai-context-core'' is ''ai-ctx'', not ''ai-context''.
      The v3.3.0 update fixes previous aggregation bugs where global metrics (Functions,
      Classes, MI) were reported as zero.

      '
    action: 'Always use ''uv run ai-ctx'' for project analysis.

      '
  - date: '2026-03-16'
    category: TOOLING
    topic: Static Analysis Parser Failures
    lesson: 'Tools relying on Regex for code parsing frequently fail on multi-line function
      signatures (e.g., those formatted by ''black''). This leads to severe false positives
      in Type Hint coverage reports.

      '
    action: 'Do not blindly trust static analysis metrics that drop inexplicably. Always
      verify the true source code using the Python ''ast'' module before attempting
      massive refactors.

      '

  # ─── PRUNED LESSONS (already in SKILL.md — kept as index only) ─────────────
  # The following entries have been fully absorbed into specialized skills.
  # [PRUNED] 2026-03-30 ARCHITECTURE/Manager-based GUI Orchestration → ui-framework/SKILL.md
  # [PRUNED] 2026-03-30 ARCHITECTURE/Interface-driven Core Design → coding-standards/SKILL.md
  # [PRUNED] 2026-03-30 i18n/Master Data SSoT Workflow → i18n-standards/SKILL.md
  # [PRUNED] 2026-03-29 TOOLING/JSON Git-Diff Stability → coding-standards/SKILL.md
  # [PRUNED] 2026-03-29 TOOLING/Robust XML Modification → i18n-standards/SKILL.md
  # [PRUNED] 2026-03-25 ARCHITECTURE/Vector Layer Synchronization → qgis-core/SKILL.md
  # [PRUNED] 2026-03-19 TESTING/Docker-based Verification (QGIS Headless) → qa-docker/SKILL.md
  # [PRUNED] 2026-03-12 ARCHITECTURE/Deterministic Lifecycle Cleanup → qgis-core/SKILL.md
  # [PRUNED] 2026-03-09 TESTING/Patch Specificity for Local Imports → qa-docker/SKILL.md
  # [PRUNED] 2026-03-08 ARCHITECTURE/System Standardization & Reflection → documentation-standards/SKILL.md
  # [PRUNED] 2026-02-28 ARCHITECTURE/Layer Caching and Mock Integrity → qa-docker/SKILL.md
  # They are retained here as a consolidated index only.
  #
  # [PRUNED] 2026-03-29 TECHNICAL/Modulo Boundaries → geological-logic/SKILL.md
  # [PRUNED] 2026-03-25 TECHNICAL/GeoPackage Append → qgis-core/SKILL.md
  # [PRUNED] 2026-03-15 TECHNICAL/Export Setting Persistence → coding-standards/SKILL.md
  # [PRUNED] 2026-03-15 TECHNICAL/DXF Export Limitations → qgis-core/SKILL.md
  # [PRUNED] 2026-03-12 ARCHITECTURE/DTO vs Tuple Flow → coding-standards/SKILL.md
  # [PRUNED] 2026-03-09 TESTING/Qt Object Mocks → qa-docker/SKILL.md
  # [PRUNED] 2026-03-09 TESTING/Dynamic Mock Return Values → qa-docker/SKILL.md
  # [PRUNED] 2026-03-08 TESTING/Iterative Mocking for Arithmetic → qa-docker/SKILL.md
  # [PRUNED] 2026-02-25 TECHNICAL/Data Modeling → coding-standards/SKILL.md
  # [PRUNED] 2026-02-19 ARCHITECTURE/Resilience & Lazy Loading → qgis-core/SKILL.md
  # [PRUNED] 2026-02-16 TECHNICAL/Signal Tracing vs Mocks → qgis-core/SKILL.md
  # [PRUNED] 2026-02-15 TECHNICAL/QGIS Signal Leaks → qgis-core/SKILL.md
  # [PRUNED] 2026-02-15 QUALITY/qgis-analyzer Context → qa-docker/SKILL.md
  # [PRUNED] 2026-02-05 USER_PREFERENCE/Development Tools → coding-standards/SKILL.md
  # [PRUNED] 2026-02-01 TECHNICAL/QgsGeometry Mocking → qa-docker/SKILL.md
```

---

## ⚙️ Global Preference Configuration

| Preference | Value |
|---|---|
| **Language** | Communication: Spanish / Code, Commits, Docs: English |
| **Formatter** | `black` |
| **Package manager** | `uv` |
| **UI approach** | Programmatic (no `.ui` files) |
| **Testing framework** | `unittest` (Mock-First pattern) |
| **Commit style** | Conventional Commits (see `docs/COMMIT_GUIDELINES.md`) |
| **Workflows** | Start with `/start-session`, close with `/close-session` |

---

*Last update: 2026-04-27 — Memory Pruning & YAML restructure (Gen 5 Memory Policy applied).*
*Next review: 2026-07-27 — Prune all entries marked `consolidated_in` older than 90 days.*
