# Agent Learning Memory (SecInterp)

This file records the **active** technical lessons, user preferences, and solutions to
complex problems. It is loaded at the start of every session, so it must stay short.

**Memory Policy**: active content must stay **under 350 lines**; lessons older than
90 days that are already reflected in a `SKILL.md` are marked `consolidated_in` and
pruned by `forge.py memory prune`. See `.agent-state/memory/memory_policy.md`.

**Archive**: the previous full log (98 lessons, 2026-03-16 → 2026-10-18) is preserved at
`.agent-state/history/memory/AGENT_LESSONS_2026-10-19_full.md`. `71` lessons were
archived on 2026-10-19; the most reusable rules are distilled in the project skills
(`project-context`, `qgis-core`, `ui-framework`, `geological-logic`).

---

## 🧠 Active Lessons (YAML Structured)

```yaml
lessons:
  - {date: '2026-10-25', category: TOOLING, topic: 'clean deletes tracked sidecars, not just generated .py', lesson: '`qgis-manage clean` unlinks the .py next to every .qrc/.ui and every *.cpg/*.qpj; `--keep-generated` only protects the .py files, so tracked sample data disappears.', action: 'Use a project-owned clean or `clean --dry-run` first; never wire `qgis-manage clean` blindly into a Makefile.'}
  - {date: '2026-10-25', category: TOOLING, topic: 'package --require-docs hardcodes a single-language help layout', lesson: '0.12.0 checks `help/html/index.html`, but SecInterp ships `help/html/<lang>/index.html` with no root index, so the flag fails on a valid package.', action: 'Keep `make zip` dependent on `docs` and gate on `help/html/<lang>/index.html`; propose a configurable docs entry upstream.'}
  - {date: '2026-10-25', category: ENVIRONMENT, topic: 'Qt6 on KDE inherits the system dark palette even with UITheme=default', lesson: 'Qt 6.11 reads the KDE/portal color scheme; `UITheme=default` has no colors of its own, and clearing `QT_QPA_PLATFORMTHEME` or forcing Fusion still yields dark.', action: 'For a light UI/screenshots launch with `QT_QPA_PLATFORMTHEME=generic` (tested light palette); keep `UITheme=default` or use a complete QSS theme.'}
  - {date: '2026-10-25', category: ENVIRONMENT, topic: 'mypy sqlite metastore fails when the cache is outside the writable workspace', lesson: 'Running `make mypy` from the parent directory under the file sandbox made mypy fail with a sqlite database error, not a type error.', action: 'Set `MYPY_CACHE_DIR=$PWD/.mypy_cache` for local sandbox runs; CI needs no override.'}
  - {date: '2026-10-24', category: ARCHITECTURE, topic: dependency-free layers can still import QGIS through root helpers, lesson: 'core had no qgis imports but logger_config did, so the plain-venv import failed.', action: 'Prove dependency-free imports with a subprocess test; do not rely only on an import grep.'}
  - {date: '2026-10-24', category: ARCHITECTURE, topic: 'cache keys do not prove a parameter reaches the extractor', lesson: 'section_feature_id was in PreviewParams, the hash and every component cache key, but nine preview/export callers omitted it, so the first feature was always sampled.', action: 'After adding a selector input, pass it through every extraction path and assert the extractor call kwargs in tests; cache-key changes alone do not prove behavior.'}
  - {date: '2026-10-24', category: TESTING, topic: 'module-size refactors break tests that patch private methods unless wrappers stay', lesson: 'Moving renderer/exporter logic to helper modules changed the patch targets; keeping thin private wrappers on the original class preserved the existing tests and integration hooks without rewriting them.', action: 'Before splitting a module, list every monkeypatched method and keep a delegating wrapper at the original call site; only update tests when the public contract actually changes.'}
  - date: '2026-10-24'
    category: TOOLING
    topic: qgis-analyzer quality_score is a size-driven MI average, not a release gate
    lesson: 'The 56.5 quality score is the mean Maintainability Index per module; even a 100-line CC10 module scores ~55, so module_size_gate PASS, CC PASS and security 100 can coexist with a low score.'
    action: Report quality_score as Module Stability/diagnostic; use tests, CC, i18n, security and module-size gates for release decisions, and never chase a 100 score by splitting every file.
  - date: '2026-10-19'
    category: AGENTIC_SYSTEM
    topic: framework patch releases can move private helpers used by project adapters
    lesson: 'v1.4.1 split forge_metrics.py and moved the _check_* helpers to forge_metrics_checks, breaking sync_metrics imports and several project tests even though it was a minor release.'
    action: After every submodule bump run forge validate, sync_metrics --validate and the full suite; import documented modules or add a compatibility test around private helpers.
  - date: '2026-10-19'
    category: ARCHITECTURE
    topic: component caches must key on every input that changes the output
    lesson: 'ProfileController cached topography, geology, structures and drillholes with partial keys; changing the DEM/line, enabling Smooth or remapping drillhole fields reused stale data in export.'
    action: Hash every relevant input (layer IDs, section feature, band, smoothing, field mappings) and add a regression that asserts the extractor is called again when one input changes.
  - date: '2026-10-19'
    category: AGENTIC_SYSTEM
    topic: a validator that scans only its own root gives a false green
    lesson: 'forge validate checked only .agent/workflows, so the four QGIS workflows in .agent-state were never validated even though the command reported that all files passed.'
    action: Scan framework and overlay roots for skills, workflows and scripts; add a test where a broken overlay workflow must fail the gate.
  - date: '2026-10-18'
    category: TOOLING
    topic: qgis-manage deploy never prunes ignored entries, so dev artifacts stay installed
      forever
    lesson: '`deploy` and `package` share `.qgisignore`, and `_cleanup_destination`
      explicitly preserves destination entries that match an ignore pattern. Anything
      that once slipped through the ignore list (here `graphify-out/`, 23 MB) keeps
      being copied/preserved, so a local install silently bloats to 30 MB while the
      CI-built ZIP looks clean.'
    action: Before deploying, check `git status --ignored --short` against `.qgisignore`;
      after adding a new generated directory to the repo, add it to `.qgisignore` in
      the same commit and delete leftovers from existing QGIS profile installs by hand.
  - date: '2026-10-18'
    category: TOOLING
    topic: a dev directory must be excluded in three separate scopes, not one
    lesson: '`tools/` and `.agent/` were excluded from ruff, the analyzer and the ZIP,
      but `.bandit` kept scanning them, so `make security-scan` was red on 15 findings
      that never ship (fatal B404/B603/B108 in `install.py`). The three scope files
      (`.analyzerignore`, `[tool.ruff] exclude`, `.bandit` `exclude_dirs`) drift independently.'
    action: When adding a dev-only directory, update all three scope files plus `.qgisignore`
      and run `make security-scan`, not just `ruff check`.
  - date: '2026-10-18'
    category: TOOLING
    topic: a 3-way merge silently duplicates a helper when both branches applied the
      same fix
    lesson: The v3.11.0 train and main each cherry-picked the same Qt6 fix into `gui/ui/pages/dem_page.py`,
      so the 3-way merge (base without the fix) kept both copies of `_all_band_statistics`;
      tests stayed green because the second definition simply shadows the first.
    action: After merging branches that share cherry-picked fixes, diff the merged files
      against both parents and scan for duplicated top-level defs (AST) before trusting
      a green suite; an auto-merge with no conflict markers can still be wrong.
  - date: '2026-10-18'
    category: AGENTIC_SYSTEM
    topic: the scheduled release CI never runs the analyzer, so CC regressions ship
    lesson: v3.11.0 was published from the train branch while `PreviewLegendRenderer.draw_legend`
      had complexity 14; the release workflow runs tests, docs and packaging, not `qgis-analyzer
      --max-cc 10`, so the pre-push gate never saw it and the merge into main exposed
      it.
    action: Treat a release branch as CC-unverified until the analyzer runs; run `qgis-analyzer
      analyze . --max-cc 10` (or the pre-push hook) on the branch before tagging, and
      budget a refactor when merging a train that skipped it.
  - date: '2026-10-11'
    category: TOOLING
    topic: a Latin-1 CSV misread as UTF-8 silently corrupts parsed structural strikes
    lesson: The sample structural DB (`basedatosestruct.csv`) is Latin-1; reading it
      as UTF-8 turns the `°` into U+FFFD, so `parse_strike("N 15° W")` falls back to
      the bare number and returns 15 instead of 345 — a plausible-but-wrong azimuth
      with no error.
    action: Declare/verify the encoding of text data before parsing degrees (Latin-1
      vs UTF-8); harden quadrant parsers to refuse a token that lost its E/W instead
      of returning a bare-number fallback.
  - date: '2026-10-11'
    category: ARCHITECTURE
    topic: dip direction is strike ± 90, chosen by the source's dip-direction label
    lesson: SecInterp's StructureMeasurement keeps original_strike (an azimuth from
      quadrant notation) and original_dip but drops the dip direction the source text
      carries ("22 SW"). The dip direction is perpendicular to the strike (dip_dir =
      strike − 90) for the SW side (N15W -> 255) or strike + 90 for the NE side (->
      75). The cardinal label only names the side, so it is approximate, not an exact
      azimuth — reading "SW" as 225 was wrong.
    action: For any stereonet/attitude export, derive dip_dir = strike ± 90 from the
      source dip-direction label (or use a numeric dip-direction field when provided);
      never treat the cardinal label as an exact azimuth, and validate on a real dataset
      — not demo data.
  - date: '2026-10-11'
    category: ARCHITECTURE
    topic: QDialog.exec() in a socket-driven QGIS handler freezes the command server
    lesson: A command that opens the SecInterp dialog had to use show() (not exec()).
      exec() starts a nested Qt event loop, so the handler never returns while the window
      is open; the fork's server guards against re-entrant dispatch, so every later
      command would block until the dialog closed — useless for automation.
    action: In MCP/socket handlers that drive a QGIS plugin, open windows non-modally
      (show()) and mirror the plugin's own run() minus exec(); never call exec() from
      a handler. The same applies to any modal QFileDialog — call the underlying export
      method with an explicit path.
  - date: '2026-10-11'
    category: TOOLING
    topic: a whole-project analyzer run can silently under-report modules; cross-check
      the count
    lesson: qgis-plugin-analyzer 1.15.2 analysed only 135 modules on the whole project
      although the plugin has 171 (its real .py count minus 2 ignored root scripts);
      1.16.0 fixed the discovery bug. Analysing a sub-directory (core/validation) already
      listed all 12 files, so the loss happened only in whole-project aggregation, and
      every historical metric had been computed over ~79% of the code while looking
      "clean".
    action: After any analyzer run, sanity-check the reported module count against find
      <pkg> -name '*.py' (minus ignore rules); if it disagrees, the run is not trustworthy
      for gates. Re-baseline metrics when a tool version changes coverage.
  - date: '2026-10-11'
    category: TOOLING
    topic: an i18n rule flagging literal args cannot follow translation done inside
      a helper
    lesson: qgis-plugin-analyzer MISSING_I18N flagged strings that are already translated
      (e.g. _stats_edit(tooltip) -> self.tr(tooltip), _check_field(..., "Collar ID")
      -> self.tr(...).format(label)), and attribute docstrings such as the bare string
      after a module-level type alias (only the first module string is recognised as
      a docstring). All 167 new findings sat in the newly-covered modules, i.e. the
      rule did not change.
    action: For helper-wrapped translations, add the helper call name to the profile's
      rules.MISSING_I18N.extra_ignore_calls instead of tagging each string; keep in
      mind that Qt-free layers (core/) cannot wrap with tr() and their user-facing messages
      are English by design until a GUI-injected translator is wired.
  - date: '2026-10-11'
    category: TOOLING
    topic: analyzer rule ids can contain a colon and break naive issue-stats parsers
    lesson: qgis-plugin-analyzer 1.15.1 introduced security rule ids of the form `SECURITY:B102`
      (a colon inside the id), printed with their count in the "Issue Statistics" block.
      SecInterp's `scripts/sync_metrics.py` split each line on the FIRST colon, so the
      numeric parse failed and the entry was dropped (total_issues 32 instead of 34).
    action: When parsing key/value lines whose key may contain colons, split on the
      LAST colon (`rsplit`, 1) or read the authoritative total line or the `--json`
      output.
  - date: '2026-10-04'
    category: TOOLING
    topic: a CI packaging job that skips the docs step ships a plugin ZIP without the
      offline help
    lesson: The scheduled-release workflow ran only `qgis-manage package`, so the gitignored,
      build-generated `help/html` (the in-plugin manual, ~14 languages) was absent and
      the v3.9.1 ZIP came out ~0.4 MiB instead of ~3.9 MiB; `build_docs.sh` also guarded
      the help sync on `[ -d help ]`, which is false on a fresh checkout, so even running
      it would skip.
    action: Any job that packages the plugin must build the docs/help first; make the
      help generator create `help/` itself (never guard on a pre-existing dir); audit
      the ZIP against a known-good build size before publishing.
  - date: '2026-10-04'
    category: AGENTIC_SYSTEM
    topic: a GitHub cron schedule can silently never fire; keep a manual dispatch path
    lesson: The repo's `scheduled-release.yml` had run only via `workflow_dispatch`
      and never via `schedule` (0 cron runs in history); on the due Sunday it did not
      fire, so the incremental release would have been missed silently.
    action: Do not rely on the GitHub scheduler for releases; verify scheduled runs
      actually occur (`gh run list --event schedule`) and always keep a manual `workflow_dispatch`
      path with the version pinned.
  - date: '2026-09-27'
    category: TOOLING
    topic: pin CI linters to the project's lock, never run the moving latest
    lesson: The lint job used `uvx ruff check .` (latest = 0.16.9) while the project
      pins ruff via uv.lock (0.15.2); the newer ruff added ISC004/PLR0917 and turned
      `main` red on every push even though the locked linter passed locally and in pre-commit.
    action: In CI, run the project's locked tool (`uv run --frozen <tool>`) or the exact
      pinned version; adopt a new linter version deliberately, not implicitly via "latest".
  - date: '2026-09-27'
    category: TOOLING
    topic: a broad try/except can hide a flat-enum QGIS4 error; the checker log always
      has a header
    lesson: '`QgsRasterBandStats.All` (flat enum) raises on PyQt6 but was swallowed
      by the feature''s `try/except (AttributeError, ...)`, silently disabling DEM band
      statistics on QGIS 4; and the pyqgis4-checker always writes a log header, so `[
      -s log ]` fails even with zero findings.'
    action: Detect Qt6 findings by matching real lines (`grep "Enum error"`), not file
      size; and remember a caught AttributeError around a QGIS enum can mask a QGIS4
      break — verify enums against the checker / real QGIS.
  - date: '2026-09-23'
    category: ARCHITECTURE
    topic: profile statistics must deduplicate by raster cell, not by Z
    lesson: Densifying the section at the DEM resolution repeats samples within the
      same pixel; aggregating them biases min/max/mean. Also, the section mean legitimately
      differs from the raster's global band mean (a section covers a swath, not the
      whole DEM).
    action: Deduplicate consecutive samples by pixel cell (floor((x-xmin)/res)) before
      aggregating; report the section stats as such, and do not expect them to match
      the DEM band statistics.
  - date: '2026-09-23'
    category: TECHNICAL
    topic: cross-CRS raster sampling must reproject and bound densification
    lesson: Sampling a DEM from section-line coordinates without honoring CRS differences
      (normal with on-the-fly reprojection) returns 0 (structures and collars drawn
      at base 0) and, worse, using the raster pixel size as a densify interval explodes
      a long line into hundreds of millions of vertices and freezes QGIS. Layer names
      can lie about CRS (a `_3857.tif` was actually EPSG:4326).
    action: Always build a line->raster QgsCoordinateTransform and transform sample
      points; derive the sampling interval in the line CRS (or transform the pixel size);
      cap densification. Verify raster CRS with `gdalinfo`, never trust the filename.
  - date: '2026-09-23'
    category: ARCHITECTURE
    topic: page-internal signals must live in an idempotent connect_signals
    lesson: StructurePage wired layerChanged -> _on_layer_changed in _setup_ui, but
      SignalManager.connect_all calls disconnect_all first and then re-invokes each
      page's connect_signals(); with no connect_signals the wiring was lost, so structural
      field combos stayed empty.
    action: Put page-internal wiring only in an idempotent connect_signals() (disconnect
      specific slots first), never in _setup_ui. Add a regression test that mirrors
      the disconnect->connect cycle.
  - date: '2026-09-23'
    category: TESTING
    topic: a fabricated mock method turns a real-QGIS crash into a green suite
    lesson: To disable a QListWidgetItem I called item.setDisabled() and taught MockQListWidgetItem
      the same (non-existent) method, so 17 unit tests passed while real QGIS 4 crashed
      with "QListWidgetItem object has no attribute setDisabled". QListWidgetItem has
      no setDisabled — that is QWidget API; items use flags()/setFlags() with Qt.ItemFlag.ItemIsEnabled.
    action: Mocks must mirror the real API surface only; never invent methods to satisfy
      production code. When adding a widget interaction, verify the method exists on
      the exact Qt class (and on both Qt5/Qt6) before writing the mock, and smoke-test
      in real QGIS when the gating touches native widgets.
  - date: '2026-09-23'
    category: AGENTIC_SYSTEM
    topic: Prefer long, stable-prefix sessions to exploit provider prompt caching
    lesson: DeepSeek discounts already-seen input tokens heavily (up to ~97%), but only
      with a stable prefix (system prompt, AGENTS.md, tool schemas) inside a long single-thread
      session. Spawning many fresh subagent contexts (each with no shared cache) and
      reloading large files or huge tool outputs defeats that discount.
    action: Prefer one long session per task; keep the system prompt/AGENTS.md stable
      mid-task; batch corrections into complete upfront prompts; use targeted reads/greps
      instead of loading whole files; reserve subagents for genuinely parallel work
      (e.g. enriching dozens of notes), not for 2-3 items the main thread can do directly.
  - date: '2026-09-21'
    category: ARCHITECTURE
    topic: QDialog.accept() does not fire closeEvent — cleanup must cover it too
    lesson: A cleanup placed only in `closeEvent` (or a `close()` handler) is skipped
      when the dialog is closed via `accept()`, because Qt calls `done()` directly and
      never invokes `closeEvent`. SecInterp's OK/Save button routed through `accept_handler`
      → `self.accept()`, so preview memory layers leaked and triggered QGIS's "temporary
      scratch layers" warning on exit.
    action: For any QDialog resource that must be released on close, also hook the `accept()`/`accept_handler`
      path (or override `done()`), not just `closeEvent`.
  - date: '2026-09-21'
    category: TOOLING
    topic: Never run qgis-analyzer analyze and sync_metrics.py in parallel
    lesson: Both `qgis-analyzer analyze .` and `scripts/sync_metrics.py` write the same
      `analysis_results/project_context.json`. Running them concurrently (two bash calls
      in one message) made one process read a half-written file and fail with a JSON
      decode error, even though the file was valid afterwards.
    action: Run the analyzer and sync_metrics sequentially; treat their shared analysis_results/
      output as a mutual-exclusion region.
  - date: '2026-09-19'
    category: AGENTIC_SYSTEM
    topic: agent workflows/skills drift from repo reality (stale metrics and checklists)
    lesson: The /release-plugin workflow still required "640 tests" and missed docs/docsec/CHANGELOG.md
      and docs/source/conf.py; the skill used a stale release notes path. This drift
      hid real release gaps.
    action: When touching a workflow/skill, reconcile its numbers (test counts, scores)
      and file lists against the actual repo (grep the current version references).
  - date: '2026-09-19'
    category: TOOLING
    topic: pre-commit pins its own ruff, which can disagree with the installed one
    lesson: isinstance(value, (dict, list)) passed the project ruff (>=0.15.0) but the
      pre-commit hook (ruff v0.8.4) rejected it with UP038 and blocked the commit. The
      hook runs its own pinned ruff version, so lint must be checked against it, not
      just the project interpreter.
    action: Before committing, remember the pre-commit ruff rev (v0.8.4) may flag rules
      the installed ruff does not; fix to satisfy the hook (e.g. dict | list).
  - date: '2026-09-19'
    category: ARCHITECTURE
    topic: allowlist ratchet as an incremental migration driver
    lesson: A test that fails both on new violations and on stale allowlist entries
      turns a large decoupling effort into small, verifiable increments, forcing the
      list to shrink as files migrate.
    action: Use a bidirectional allowlist gate for gradual Extract-then-Compute migrations;
      each migrated file produces an immediate, testable gate shrink.
  - date: '2026-09-13'
    category: AGENTIC_SYSTEM
    topic: Harness assumptions go stale (the Bitter Lesson)
    lesson: The agentic system assumed a dual Antigravity/CodeWhale runtime, with a
      bridge (workflow_executor.py + .codewhale/) to translate between them. The real
      runtime had already moved to opencode, leaving the bridge as dead weight.
    action: Prefer runtime-native mechanisms (AGENTS.md, SKILL.md name+description,
      opencode.json subagents) over bespoke bridges. Any script that exists only to
      translate between runtimes is a liability.
  - date: '2026-09-12'
    category: AGENTIC_SYSTEM
    topic: Single Source of Truth for Workflow Tables
    lesson: Root AGENTS.md and .agent/AGENTS.md each had a manually-maintained workflow
      table that drifted (5 vs 15 workflows). Duplicated tables inevitably diverge.
    action: The workflow/skills tables now live only in the root AGENTS.md (single source
      of truth); .agent/AGENTS.md is a pointer. Update root AGENTS.md manually when
      adding/renaming a workflow or skill (skill_sync.py retired in Gen 8).
  - date: '2026-09-12'
    category: AGENTIC_SYSTEM
    topic: Release Timing vs Build/Upload Order
    lesson: The scoped-enum migration (commit 7ae8ac96) was committed AFTER the v3.7.1
      ZIP was built and uploaded, so the portal's Qt6 checker kept reporting 114 enum
      findings even though HEAD was clean. A fix that lives in git but never in a released
      artifact is invisible to the portal.
    action: When a compatibility fix lands, verify the built ZIP actually contains it
      (unzip -p on the artifact) and ship a patch release before declaring the portal
      issue resolved.
```

## 🗂️ Archived / consolidated index

The following lessons were consolidated into the project skills or archived because
they describe one-off incidents already covered by a gate or a skill:

- **Testing & mocks** → `testing-standards` (mixed-fidelity mocks, invented Qt methods,
  snapshot pruning, test discovery).
- **QGIS/CRS/geometry** → `qgis-core`, `geological-logic` (CRS reprojection, raster-cell
  deduplication, section resolver, dip/strike conventions).
- **Release/CI/tooling** → `release-management`, `commit-standards`, `documentation-standards`
  (pinned linters, docs/help build order, cron dispatch, artifact auditing).
- **Agentic system** → this file + `agentic-memory` (metric freshness, workflow drift,
  source-of-truth tables, runtime assumptions).

Full text: `.agent-state/history/memory/AGENT_LESSONS_2026-10-19_full.md`.

---

*Last update: 2026-10-19 — compacted from 98 to 27 active lessons.*
*Next review: 2027-01-19 — prune consolidated lessons older than 90 days.*
