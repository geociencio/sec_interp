# SecInterp Agentic System — Gen 7 → Gen 8 (Corrected for opencode)

> **Created**: 2026-09-13
> **Status**: 📋 Proposal (not yet scheduled)
> **Target runtime**: opencode (deepseek-v4-pro)
> **Basis**: empirical audit of current state (34 scripts, 13 skills, 16 workflows, 25 agentic tests).

---

## 0. Premise correction (critical)

The GEN7 plan assumed a dual Antigravity/CodeWhale runtime. The real runtime is **opencode**. The entire bridge layer — `workflow_executor.py` (`RUNTIME_TOOLS`), `.codewhale/instructions.md`, `detect_runtime()` — is already one generation stale. The "Bitter Lesson" the plan cites has materialized in this very repo: **the bridge is now the debt, not the solution.**

**Gen 8 governing principle**: stop bridging runtimes; use opencode-native mechanisms — `AGENTS.md`, `SKILL.md` (`name`+`description`), `opencode.json` (subagents). Any script that exists only to translate between runtimes is retired.

---

## 1. Verified baseline

| Dimension | Reality | GEN7 said |
|---|---|---|
| Scripts | **34** (20 py root + 7 sh + 7 py in `i18n/`/`research/`) | ~30 |
| Skills | 13, all with custom `trigger` | same |
| Workflows | 16 (15 with `runtimes:`) | 15 |
| `agent:` labels | 4 inconsistent labels → 3 ids | not detected |
| Agentic tests | 25 | same |
| Episodic memory | 159 Markdown logs in `docs/maintenance/`, no `sessions/` JSONL | same |
| AGENTS.md | **duplicated**: root + `.agent/` | root cause unattacked |

---

## 2. Roadmap (ordered by ROI)

### Phase A — Unify AGENTS.md (🔴 HIGH, low effort)
- [ ] Consolidate root `AGENTS.md` (read by opencode) and `.agent/AGENTS.md` into one source of truth.
- [ ] Remove duplicated skill/workflow tables (true SSoT).
- [ ] **Effect**: `skill_sync.py` and `context_selector.py` become unnecessary (opencode discovers skills natively). Retire both + their tests.
- [ ] Update `.qgisignore`: exclude `.opencode/` and `opencode.json` (currently only excludes `.agent/` and `.codewhale/`).

### Phase B — Consolidate tooling (🔴 HIGH)
- [ ] **Metrics → one entry point**: fold `metrics_report.py`, `validate_agent_metrics.py`, `update_testing_status.py` into `sync_metrics.py` subcommands (`--report`, `--validate`, `--testing-status`).
- [ ] **Consistency**: fold `workflow_graph.py` and `check_skill_conflicts.py` into `validate_agent_system.py` (`--graph`, `--conflicts`).
- [ ] **i18n**: fold `i18n_diagnostic.py` into `verify_i18n_hygiene.py`; retire 2 of 3 shell scripts (`sync-i18n.sh`, `apply-all-i18n.sh`; keep `update-strings.sh`).
- [ ] **Test-runners → fuse**: merge `run_tests_in_qgis.py` + `run_benchmarks.py` into one `run_in_qgis.py` parameterized by suite (`integration` | `benchmarks`), adopting the `exitQgis()` headless behavior.
- [ ] **Retire bridge**: `workflow_executor.py` + `.codewhale/instructions.md`.
- [ ] **Tests**: retire orphaned tests in `tests/agentic/` in the same commit.
- **Goal**: 34 → ~13 scripts.

### Phase C — Externalize thresholds correctly (🟡 MEDIUM)
- [ ] `check_cc.py --threshold N` flag (not `CC_THRESHOLD = 10` hard-coded).
- [ ] One wrapper (`sync_metrics.py`) as the consumer; **no** passive JSON nobody reads.
- [ ] Record analyzer versions in a single place (`agent_metrics.json` header).

### Phase D — Native opencode subagents (🟡 MEDIUM)
- [ ] Create `opencode.json` with `agent` definitions: `architect` (`edit: allow`), `qa_engineer` (`edit: ask`), `auditor` (`edit: deny`).
- [ ] Normalize workflow `agent:` frontmatter to the 3 ids ("Architect"/"Senior Architect" → `architect`).
- [ ] Remove obsolete `runtimes:` frontmatter field.

### Phase E — Standard skill format (🟢 LOW)
- [ ] Drop `trigger` from all 13 `SKILL.md`; fold "when to use" into `description`.

### Phase F — Session-as-durable-object (📋 PROPOSAL ONLY, out of scope)
- [ ] Document as a separate proposal (159 Markdown logs → JSONL requires its own migration plan). Not scheduled.

---

## 3. Success criteria

| Criterion | Now | Target Gen 8 |
|---|---|---|
| Scripts | 34 | ~13, no overlap |
| Runtimes modeled | antigravity+codewhale (stale) | opencode native |
| Roles | prose | subagents with permission gradient |
| AGENTS.md | duplicated | single SSoT |
| Skill format | custom `trigger` | `name`+`description` |
| Thresholds | hard-coded | flag + single consumer |
| Bridge files | `workflow_executor.py`, `.codewhale/` | retired |

---

## 4. Decisions (confirmed)

1. `skill_sync.py` → **eliminate** (opencode indexes skills natively).
2. Test-runners → **fuse** into `run_in_qgis.py`.
3. Phase F (session log) → **proposal only**.
4. Document language → **English**.

---

## 5. References

- Anthropic — [Building Effective Agents](https://www.anthropic.com/engineering/building-effective-agents)
- Anthropic — [Scaling Managed Agents: Decoupling the brain from the hands](https://www.anthropic.com/engineering/managed-agents)
- [Model Context Protocol (MCP)](https://modelcontextprotocol.io/)
- opencode — [Agent Skills](https://opencode.ai/docs/skills/)
- Supersedes: `.agent/architecture/IMPROVEMENT_PLAN_GEN7.md` (kept as reference)

---

*Proposal drafted 2026-09-13. Not yet scheduled against a phase release.*
