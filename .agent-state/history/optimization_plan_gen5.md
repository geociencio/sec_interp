# Agentic System Optimization Plan (SecInterp)

This document tracks the continuous evolution of the `.agent/` system, comparing
completed work against industry standards and defining the next optimization targets.

**Last updated**: 2026-04-27 | **Current generation**: Gen 5 (complete)

---

## 1. Current State (Gen 5 — Complete)

### ✅ Strengths (Achieved)

| Capability | Implementation | Standard |
|---|---|---|
| Role separation (Architect / QA / Auditor) | `AGENTS.md` with 3 defined agents | AGENTS.md spec 2025 |
| Modular skills (on-demand context) | 13 `SKILL.md` files with triggers | AGENTS.md skills standard |
| Episodic memory | `history/sessions/` + `history/tasks/` (40+ records) | Multi-tier memory 2025 |
| Semantic memory | `AGENT_LESSONS.md` (pruned, YAML-structured) | Structured note-taking |
| Memory policy | `memory_policy.md` (3-tier, pruning rules, conflict resolution) | Memory lifecycle 2026 |
| Hierarchical AGENTS.md | `core/AGENTS.md` + `gui/AGENTS.md` | Nested AGENTS.md standard |
| Stop conditions | Defined in `build-feature.md` + `close-session.md` | Agentic safety 2025 |
| Observability metrics | `agent_metrics.json` schema v2.0 (TCR, retries, stop events) | Agentic observability 2025 |
| Cognitive English | 100% `.agent/` in English | Cognitive alignment |
| QA gates | `qgis-plugin-analyzer` integrated into commit workflow | Zero-debt injection |
| Fix linting workflow | `/fix-linting` automates ruff + black | Linting automation |
| QGIS 4.x readiness | `qgis-migration-4x` skill | Forward compatibility |
| MCP integration | `scripts/mcp_server.py` (JSON-RPC interface) | MCP standard 2025 |

### ⚠️ Remaining Gaps (Gen 5 → Gen 6 targets)

| Gap | Impact | Priority |
|---|---|---|
| Memory pruning is manual (no script) | Memory bloat risk over time | High |
| `agent_metrics.json` updated manually per session | Inconsistent observability | High |
| No semantic retrieval — all context loaded statically | Token waste on irrelevant skills | Medium |
| Docstring coverage < 80% in `core/` | Quality score penalized | Medium |
| `MISSING_I18N` warnings not systematically resolved | UX degradation for users | Medium |
| `SPATIAL_INDEX` warning in `dialog_interpretation_manager.py:123` | Performance risk | Low |

---

## 2. Evolution Toward Generation 6

Based on 2025–2026 agentic standards research, the following evolutionary leaps are proposed:

### A. Automated Memory Maintenance (Priority: High)

**Problem**: `AGENT_LESSONS.md` pruning and `agent_metrics.json` updates are done manually,
creating inconsistency risk and violating the "Memory as Dynamic Execution State" principle.

**Solution**:
- Extend `/close-session` to auto-extract key metrics from `qgis-analyzer` JSON output
  and append them to `agent_metrics.json` without human intervention.
- Create a `scripts/memory_prune.py` utility that:
  1. Reads `AGENT_LESSONS.md`
  2. Identifies entries older than 90 days with a `consolidated_in:` field
  3. Moves them to the `[PRUNED]` index section automatically

**Target**: Memory maintenance → 0 manual steps per session.

### B. Semantic Context Injection (Priority: Medium)

**Problem**: All 13 skills are listed in `AGENTS.md` statically. The agent loads
all triggers at once, increasing token overhead and "context noise."

**Solution**: Implement a `scripts/context_selector.py` that:
1. Reads the current task description (from `AI_CONTEXT.md`)
2. Returns only the 2–3 most relevant skills based on keyword matching
3. The output is injected as a "Dynamic Mix" in `/start-session`

**Target**: Reduce context tokens by ~40% for focused tasks.

### C. QA Gate Hardening (Priority: Medium)

**Problem**: `qgis-plugin-analyzer` is invoked manually. A commit can still introduce
complexity regressions if the developer skips the analysis step.

**Solution**:
- Add a `pre-push` hook (separate from `pre-commit`) that:
  1. Runs `qgis-analyzer analyze .`
  2. Checks that no function has CC > 10
  3. Blocks the push if any new hotspot is detected vs the baseline

**Target**: Zero CC regressions reach `main` branch.

### D. Observability Dashboard (Priority: Low)

**Problem**: `agent_metrics.json` is a JSON file — useful but not visual.
Tracking trends (TCR over sessions, quality score evolution) requires manual inspection.

**Solution**:
- Create `scripts/metrics_report.py` that reads `agent_metrics.json`
  and outputs a simple Markdown table with session trends.
- Embed this report in the `/close-phase` workflow output.

**Target**: Trend visibility without external tooling.

### E. Docstring Coverage Improvement (Priority: Medium)

**Problem**: `qgis-plugin-analyzer` quality score (41.7/100) is penalized by
docstring coverage gaps in `core/` modules, not by bugs or complexity.

**Solution**:
- Run `/fix-linting` variant focused on docstring insertion
- Prioritize `core/services/` and `core/utils/` (highest public API surface)
- Target: Coverage > 80% → expected score improvement to ~60/100

---

## 3. Implementation Proposals

### A. New Scripts

| Script | Purpose | Blocks |
|---|---|---|
| `scripts/memory_prune.py` | Auto-prune consolidated lessons | Gen 6.A |
| `scripts/context_selector.py` | Semantic skill selection | Gen 6.B |
| `scripts/metrics_report.py` | Markdown trend report from JSON | Gen 6.D |
| `.git/hooks/pre-push` | CC regression gate | Gen 6.C |

### B. Workflow Updates

| Workflow | Change |
|---|---|
| `/close-session` | Auto-call `memory_prune.py` + auto-update `agent_metrics.json` |
| `/start-session` | Use `context_selector.py` output to pre-load relevant skills |
| `/close-phase` | Embed `metrics_report.py` output in phase closure report |
| `/fix-linting` | Add `--docstrings` mode targeting Google-style insertion |

### C. Memory Improvements

#### Automated Metrics Extraction (Gen 6.A)
On `/close-session`, the workflow will:
1. Run `qgis-analyzer analyze . --output json`
2. Extract: `quality_score`, `tests_ok`, `cc_avg`, `hotspot_count`
3. Append structured entry to `agent_metrics.json` automatically

---

## 4. Roadmap

### ✅ Gen 5 Complete (2026-04-27)
- [x] Hierarchical AGENTS.md (`core/`, `gui/`)
- [x] Stop conditions in key workflows
- [x] Memory policy + YAML-structured lessons
- [x] Metrics schema v2.0 (TCR, retries, stop events)
- [x] 13 skills synchronized, 0 phantom references
- [x] 571 tests passing, 0 high-complexity hotspots

### 🚧 Gen 6 Targets (Next Phase)
1. **Immediate**: Create `scripts/memory_prune.py` → auto-prune on `/close-session`
2. **Short term**: Add `pre-push` CC regression gate
3. **Medium term**: `scripts/context_selector.py` for semantic skill injection
4. **Medium term**: Docstring coverage campaign in `core/` (target score: ~60/100)
5. **Long term**: `scripts/metrics_report.py` + `/close-phase` integration

---

*Last updated: 2026-04-27 — Gen 5 closure + Gen 6 roadmap definition.*
*Next review: On `/start-phase` for the next major development cycle.*
