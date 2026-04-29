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
  - date: 2026-04-28
    category: TOOLING
    topic: QGIS 4 Sphinx Mocking
    lesson: >
      When updating Sphinx documentation for QGIS 4.x readiness, adding 'qgis.PyQt',
      'PyQt6', and specific Qt modules to 'autodoc_mock_imports' is essential to
      prevent build errors in environments where these libraries are not installed.
    action: >
      Always include Qt6-related mocks in 'conf.py' when targeting QGIS 4 compatibility
      to ensure documentation builds are decoupled from the local Qt environment.

  - date: 2026-04-28
    category: TESTING
    topic: Post-Merge Stability Verification
    lesson: >
      Major branch merges (like the Cyclomatic Complexity refactoring) can introduce
      subtle regressions in complex orchestrators even if individual tests passed
      in the branch.
    action: >
      Always execute the full project test suite ('make test' or discovery)
      immediately after a merge to 'main' to verify global system integrity.

  - date: 2026-04-28
    category: ARCHITECTURE
    topic: API-Agnostic Stability
    lesson: >
      Consistently using 'qgis.PyQt' shims instead of direct 'PyQt5' or 'PyQt6' imports
      guarantees a stable codebase that operates seamlessly across QGIS 3 and 4
      runtimes without requiring conditional branching or manual porting.
    action: >
      Enforce the 'qgis.PyQt' standard in all new modules and use 'qgis-analyzer'
      to audit and prevent direct Qt library imports.


  - date: 2026-04-26
    category: TOOLING
    topic: Complexity Branch Counting (or "")
    lesson: >
      qgis-plugin-analyzer 1.13.1 counts 'or ""' expressions in function arguments
      or return statements as additional logical branches, which can push cyclomatic
      complexity over the limit in methods with many optional fields.
    action: >
      Decompose monolithic orchestrators into discrete 'Steps' (private methods) and
      use intermediate variables or DTO defaults instead of inline 'or' logic to
      maintain low CC scores.

  - date: 2026-04-26
    category: ARCHITECTURE
    topic: Orchestrator Decomposition
    lesson: >
      Decoupling complex data processing flows into a 'Step-by-Step' pattern within
      orchestrator services (core/services) improves testability and reduces complexity
      without breaking the Extract-then-Compute paradigm.
    action: >
      Use private methods prefixed with _stepN_ to document the execution flow of
      complex services, keeping the main method clean and linear.

  - date: 2026-04-26
    category: ARCHITECTURE
    topic: Explicit Signal Disconnection
    lesson: >
      Static analyzers like qgis-analyzer may flag signal connections as leaks if
      disconnections are not explicit and symmetric within the same class context.
    action: >
      Ensure all signals connected in 'connect_signals' are explicitly disconnected
      by slot name in 'disconnect_signals' using 'contextlib.suppress'.

  - date: 2026-04-26
    category: TOOLING
    topic: QGIS-Analyzer Static Summary
    lesson: >
      The 'summary' command is a static JSON viewer. It does not reflect real-time
      code changes unless 'analyze' is executed first.
    action: >
      Always force a full re-analysis ('qgis-analyzer analyze .') before verifying
      fixes with 'summary' to avoid phantom issue reporting.

  - date: 2026-04-25
    category: TOOLING
    topic: Flake8 vs Ruff Configuration Parity
    lesson: >
      Ruff and Flake8 can have different default rule scopes or ignored rules (like
      F821, E402). If the CI/CD or QGIS repository strict analyzer uses Flake8
      without the pyproject.toml ignores, the build will fail despite Ruff reporting
      0 errors.
    action: >
      When resolving linting issues for external platforms, always run the exact tool
      (e.g., Flake8) expected by the platform and manage exclusions through
      '# noqa' comments directly in the code rather than relying exclusively on
      'pyproject.toml' ignores.

  - date: 2026-04-05
    category: ARCHITECTURE
    topic: Gen 5 Blueprint Scaffolding
    lesson: >
      Blueprint Scaffolding architecture is superior for scaling frameworks while
      maintaining a generic core. Integrating the Reflect Loop (Agent Auditor
      critique) significantly reduces hallucination risk in autonomous planning.
      MCP is the backbone for standardized and secure tool orchestration.
    action: >
      Use the /ia-critic workflow after every major planning phase. Expand
      mcp_server.py to cover all validation-heavy core logic.

  - date: 2026-03-30
    category: ARCHITECTURE
    topic: Manager-based GUI Orchestration
    lesson: >
      Refactoring monolithic dialog classes into specialized Managers (Signal,
      Preview, Export, Input) reduces cyclomatic complexity (CC) and decouples
      UI lifecycle from feature logic.
    action: >
      Adopt the Manager pattern for all complex QGIS Dialogs, delegating signal
      handling and state persistence to dedicated orchestrators.
    consolidated_in: ui-framework/SKILL.md

  - date: 2026-03-30
    category: ARCHITECTURE
    topic: Interface-driven Core Design
    lesson: >
      Defining service contracts via Abstract Base Classes (ABCs) in 'core/interfaces'
      allows the ProfileController to remain agnostic of concrete implementations,
      enabling seamless Dependency Injection and Mock-based testing.
    action: >
      Always define a clear interface for new Core services before implementation
      to ensure loose coupling and testability.
    consolidated_in: coding-standards/SKILL.md

  - date: 2026-03-30
    category: i18n
    topic: Master Data SSoT Workflow
    lesson: >
      Treating JSON dictionaries as the Single Source of Truth (SSoT) for translations
      allows for safe, automated injection into Qt '.ts' files, eliminating XML
      formatting errors and enabling asynchronous parallel machine translation.
    action: >
      Never modify '.ts' files manually; always use the 'master_data/*.json'
      registries as the primary editing point for all locales.
    consolidated_in: i18n-standards/SKILL.md

  - date: 2026-03-29
    category: TOOLING
    topic: JSON Git-Diff Stability
    lesson: >
      When using machine translation APIs to asynchronously update dictionaries,
      json.dump without deterministic key sorting creates chaotic and unreviewable
      git diffs on every run.
    action: >
      Always enforce 'sort_keys=True' when dumping JSON dictionary arrays that act
      as 'translation memories' or configuration hubs.
    consolidated_in: coding-standards/SKILL.md

  - date: 2026-03-29
    category: TOOLING
    topic: Robust XML Modification
    lesson: >
      Using naive regex to search and replace values in Qt translation '.ts' files
      leads to massive malformed XML structures. 'xml.etree.ElementTree' is orders
      of magnitude safer.
    action: >
      Always utilize native AST or XML parsing libraries when injecting or modifying
      structured files, completely avoiding custom Regex patches.
    consolidated_in: i18n-standards/SKILL.md

  - date: 2026-03-25
    category: ARCHITECTURE
    topic: Vector Layer Synchronization
    lesson: >
      In-memory layer updates inside QGIS require a strict transaction boundary
      (startEditing, deleteFeatures, addFeatures, commitChanges) to guarantee
      atomicity and correct signal emission for the canvas renderers.
    action: >
      Encapsulate live QgsVectorLayer mutation in unified save_to_layer and
      sync_from_layer routines and explicitly clear cache logic.
    consolidated_in: qgis-core/SKILL.md

  - date: 2026-03-22
    category: TOOLING
    topic: ai-context-core CLI
    lesson: >
      The CLI executable for 'ai-context-core' is 'ai-ctx', not 'ai-context'.
      The v3.3.0 update fixes previous aggregation bugs where global metrics
      (Functions, Classes, MI) were reported as zero.
    action: >
      Always use 'uv run ai-ctx' for project analysis.

  - date: 2026-03-19
    category: TESTING
    topic: Docker-based Verification (QGIS Headless)
    lesson: >
      Verifying QGIS-dependent functionality (like DXF/GPKG export) is impossible
      in local environments lacking the full QGIS/PyQt stack. Relying on mocks only
      validates the orchestration logic, not the file driver compatibility.
    action: >
      Always use 'make docker-test' or run reproduction scripts inside the QGIS
      Docker container to confirm actual file creation and driver-specific behavior.
    consolidated_in: qa-docker/SKILL.md

  - date: 2026-03-16
    category: TOOLING
    topic: Static Analysis Parser Failures
    lesson: >
      Tools relying on Regex for code parsing frequently fail on multi-line function
      signatures (e.g., those formatted by 'black'). This leads to severe false
      positives in Type Hint coverage reports.
    action: >
      Do not blindly trust static analysis metrics that drop inexplicably. Always
      verify the true source code using the Python 'ast' module before attempting
      massive refactors.

  - date: 2026-03-12
    category: ARCHITECTURE
    topic: Deterministic Lifecycle Cleanup
    lesson: >
      In QGIS plugins with complex UI/Tool interactions, relying on Python's garbage
      collector or implicit deletion is insufficient. Explicit and ordered cleanup
      in closeEvent is required to prevent orphaned GraphicsItems and signal leaks.
    action: >
      Orchestrate a cleanup sequence in closeEvent for all managers and tools.
      Implement a specialized cleanup_finalized() for tools to ensure canvas hygiene.
    consolidated_in: qgis-core/SKILL.md

  - date: 2026-03-09
    category: TESTING
    topic: Patch Specificity for Local Imports
    lesson: >
      Classes imported locally inside functions must be patched using the absolute
      path of the calling module where the lookup occurs, not the module of origin.
    action: >
      Always verify if a class is imported at the module level or inside a method
      before defining the patch target path.
    consolidated_in: qa-docker/SKILL.md

  - date: 2026-03-08
    category: ARCHITECTURE
    topic: System Standardization & Reflection
    lesson: >
      A purely English-based agentic system improves context injection and reduces
      parsing ambiguity. Implementing formalized reflection loops (post-execution)
      allows for better semantic memory retention.
    action: >
      Adopt English as the universal standard for internal system files. Maintain
      a mandatory reflection phase in all core workflows.
    consolidated_in: documentation-standards/SKILL.md

  - date: 2026-02-28
    category: ARCHITECTURE
    topic: Layer Caching and Mock Integrity
    lesson: >
      When centralizing layer resolution with caching (LayerResolver), mock layers
      must have unique IDs across tests to prevent cross-test cache pollution.
    action: >
      Implement a global UNIQUE_ID_COUNTER in test mocks and call
      LayerResolver.clear_cache() in BaseTestCase.setUp().
    consolidated_in: qa-docker/SKILL.md

  - date: 2026-02-19
    category: ARCHITECTURE
    topic: Resilience & Lazy Loading
    lesson: >
      When implementing experimental features or heavy domain services, use a
      SafeLoader/Lazy Loading pattern to prevent cascading failures during plugin
      initialization.
    action: >
      Implement SafeLoader for all optional or heavy services and use demand-based
      instantiation.
    consolidated_in: qgis-core/SKILL.md

  - date: 2026-02-05
    category: USER_PREFERENCE
    topic: Development Tools
    lesson: >
      Preference for black (formatting), uv (dependencies), and programmatic UI
      (no .ui files).
    action: Apply these standards in every new GUI implementation.
    consolidated_in: coding-standards/SKILL.md

  # ─── PRUNED LESSONS (already in SKILL.md — kept as index only) ─────────────
  # The following entries have been fully absorbed into specialized skills.
  # They are retained here as a consolidated index only.
  #
  # [PRUNED] 2026-03-29 TECHNICAL/Modulo Boundaries → geological-logic/SKILL.md
  # [PRUNED] 2026-03-25 TECHNICAL/GeoPackage Append → qgis-core/SKILL.md
  # [PRUNED] 2026-03-15 TECHNICAL/DXF Export Limitations → qgis-core/SKILL.md
  # [PRUNED] 2026-03-15 TECHNICAL/Export Setting Persistence → coding-standards/SKILL.md
  # [PRUNED] 2026-03-12 ARCHITECTURE/DTO vs Tuple Flow → coding-standards/SKILL.md
  # [PRUNED] 2026-03-09 TESTING/Qt Object Mocks → qa-docker/SKILL.md
  # [PRUNED] 2026-03-09 TESTING/Dynamic Mock Return Values → qa-docker/SKILL.md
  # [PRUNED] 2026-03-08 TESTING/Iterative Mocking for Arithmetic → qa-docker/SKILL.md
  # [PRUNED] 2026-02-25 TECHNICAL/Data Modeling → coding-standards/SKILL.md
  # [PRUNED] 2026-02-16 TECHNICAL/Signal Tracing vs Mocks → qgis-core/SKILL.md
  # [PRUNED] 2026-02-15 TECHNICAL/QGIS Signal Leaks → qgis-core/SKILL.md
  # [PRUNED] 2026-02-15 QUALITY/qgis-analyzer Context → qa-docker/SKILL.md
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
