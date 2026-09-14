# SecInterp Agentic System — Gen 7 → Gen 8 Improvement Plan

> **Created**: 2026-09-13
> **Status**: 📋 Proposal (not yet scheduled)
> **Scope**: `.agent/` system, `scripts/`, runtime integration, memory & metrics
> **Basis**: 2026 industry-standard research (Anthropic Engineering, MCP) benchmarked against the current Gen 6/7 implementation.

---

## 1. Executive Summary

SecInterp's agentic system (Gen 6/7) is **technically mature but architecturally misaligned with the 2026 industry standard**. It has grown to ~30 tooling scripts, a dual runtime bridge (Antigravity/CodeWhale), a custom MCP server, and 25 dedicated agentic tests — a level of harness complexity that the industry's own guidance now argues *against*.

The core problem is the **Bitter Lesson**, stated directly by Anthropic's 2026 work on Managed Agents:

> "Harnesses encode assumptions that go stale as models improve."

Gen 6/7 encodes many assumptions — `CC <= 10`, specific analyzer versions, a hard-coded dual-runtime bridge, hand-maintained metric provenance — that are already showing drift (documented in `AGENT_LESSONS.md`: metric staleness, multi-tool scope mismatch, table drift). The fix is not more scripts; it is to **decouple stable interfaces from changing implementations**, exactly as the industry did.

This document proposes a **Gen 8** that consolidates the tooling long-tail, replaces conceptual roles with runtime-native subagents, aligns skills to the standard `SKILL.md` format, and adopts a session-as-durable-object memory model.

---

## 2. Industry Standard Reference (2026)

Three authoritative sources define the current standard:

### 2.1 "Building Effective Agents" (Anthropic)
> "The most successful implementations use simple, composable patterns rather than complex frameworks… add multi-step agentic systems only when simpler solutions fall short."

- Distinguishes **workflows** (predefined code paths) from **agents** (model-directed).
- Five canonical patterns: prompt-chaining, routing, parallelization, orchestrator-workers, evaluator-optimizer.
- Three principles: **simplicity**, **transparency**, **good ACI** (tool documentation = docstrings for a junior dev).

### 2.2 "Scaling Managed Agents" (Anthropic, Apr 2026)
> "Decoupling the brain from the hands."

- **Session** = append-only log that lives *outside* the context window (`getEvents()`), not a compaction artifact.
- **Memory tool**: write to files to learn across sessions (semantic memory).
- **Harness / sandbox / session** as stable, independently replaceable interfaces.
- **MCP** for tools + a **vault** for credentials; narrow security scoping.
- Harness assumptions (e.g. "context resets") became dead weight as models improved.

### 2.3 MCP + Agent Skills
- **MCP** is the de-facto standard for tool/context integration ("USB-C for AI").
- **Agent Skills** (`SKILL.md` with `name` + `description`) is the standard for reusable capabilities; unknown frontmatter is ignored, and runtime-native skill discovery replaces bespoke context selectors.

---

## 3. Current State Assessment (Gen 6/7)

### 3.1 Strengths (keep)

| Area | Implementation | Verdict |
|:---|:---|:---|
| Evaluator-optimizer loop | `@auditor` + `/ia-critic` + Reflection in workflows | ✅ Aligned |
| Semantic memory | `AGENT_LESSONS.md` + `memory_prune.py` + `lesson_extractor.py` | ✅ Aligned |
| Quality gates | `check_cc.py`, `verify_i18n_hygiene.py`, `security_scan.py` | ✅ Aligned |
| MCP | `mcp_server.py` (Gen 5) | ✅ Aligned (evaluate scope) |
| Observability | `sync_metrics.py`, `metrics_report.py`, `validate_agent_metrics.py` | ✅ Aligned |
| Runtime-agnostic workflows | `workflow_executor.py` + `.codewhale/instructions.md` | ⚠️ See 4.3 |

### 3.2 Gaps vs. standard

| Standard pillar | Gen 6/7 status |
|:---|:---|
| Simplicity (tooling restraint) | ❌ ~30 scripts, overlapping responsibilities |
| Real subagents with scoped permissions | ❌ roles are text in `AGENTS.md` only |
| Standard skill format (`name`+`description`) | ⚠️ custom `trigger` field + bespoke `context_selector.py` |
| Session as durable object (`getEvents()`) | ❌ relies on compaction + file summaries |
| Single source of truth for metrics | ⚠️ multi-tool scope mismatch (known, partially fixed) |
| Stable harness interfaces | ❌ hard-coded analyzer/CC assumptions |

---

## 4. Key Findings

### 4.1 Tooling long-tail violates the simplicity principle

`scripts/` contains ~30 tools. Several overlap in responsibility:

- **Metrics**: `sync_metrics.py`, `validate_agent_metrics.py`, `metrics_report.py`, `update_testing_status.py`
- **Memory**: `memory_prune.py`, `lesson_extractor.py`, `session_index.py`
- **System consistency**: `skill_sync.py`, `check_skill_conflicts.py`, `validate_agent_system.py`, `workflow_graph.py`

The **Agentic Memory** lesson "Single Source of Truth for Workflow Tables" already documents drift caused by duplicated tables. The proliferation of consistency *tools* is the same disease at the tool layer: each new tool is a new assumption to keep synchronized.

**Recommendation**: collapse to a single `sync.py` (or `validate.py`) with subcommands, and retire the long tail.

### 4.2 Harness assumptions go stale

- `check_cc.py` hard-codes `CC <= 10` — a threshold chosen for a specific model/tool era.
- `qgis-analyzer` and `ai-ctx` versions are referenced in metrics but measure *different* things (the documented "Multi-Tool Scope Mismatch").
- The dual-runtime bridge (Antigravity ↔ CodeWhale) is a harness assumption about *which runtime* runs the agent.

Per the Bitter Lesson, these must become **inputs to a stable interface**, not hard-coded in script bodies.

### 4.3 Conceptual roles, not runtime subagents

`AGENTS.md` defines `@architect`, `@qa_engineer`, `@auditor` as prose. The runtime (CodeWhale, or opencode) has no knowledge of them, so they cannot enforce permission scoping. The auditor's "read-only" constraint is advisory only.

**Recommendation**: register each role as a native subagent (`mode: subagent`) with a permission gradient: architect `edit: allow`, QA `edit: ask`, auditor `edit: deny`.

### 4.4 No session-as-durable-object

Gen 6/7 stores session state in `docs/maintenance/session_*.md` + `AI_CONTEXT.md` (reset per session) + `next_steps.md`. This is episodic *memory*, not a **durable, queryable session log**. The 2026 standard's `getEvents()` model would let the agent rewind/re-read context without irreversible compaction decisions.

### 4.5 Skill format diverges from the standard

Skills use `name`, `description`, **`trigger`**. The industry standard (`SKILL.md`) uses `name` + `description` and ignores unknown fields; discovery is runtime-native. The bespoke `context_selector.py` reimplements what the runtime already provides.

---

## 5. Gen 8 Roadmap

### Phase 1 — Tooling consolidation 🔴 HIGH
- [ ] Merge metrics tools into `sync_metrics.py` (retire `metrics_report.py`, `validate_agent_metrics.py`, `update_testing_status.py`).
- [ ] Merge consistency tools into `validate_agent_system.py` (retire `workflow_graph.py`, `check_skill_conflicts.py`, `skill_sync.py` → make `skill_sync` a subcommand).
- [ ] Externalize thresholds: move `CC_MAX=10` and analyzer versions to a config block (e.g. `agent_metrics.json` or a `thresholds:` section) instead of hard-coding.
- **Goal**: `scripts/` shrinks from ~30 to ~15.

### Phase 2 — Runtime-native subagents 🔴 HIGH
- [ ] Register `architect`, `qa_engineer`, `auditor` as native subagents with scoped permissions.
- [ ] Map the workflow frontmatter `agent:` field to real subagent ids.
- [ ] Keep the auditor `edit: deny` (true read-only).

### Phase 3 — Session & memory alignment 🟡 MEDIUM
- [ ] Adopt a session log outside the context window: append-only `history/sessions/<id>.jsonl` with a `get_events()` interface.
- [ ] Wire `next_steps.md` / `task.md` as *views* over that log, not as hand-maintained files.
- [ ] Keep `AGENT_LESSONS.md` as the semantic (memory-tool) layer.

### Phase 4 — Skill format standardization 🟡 MEDIUM
- [ ] Drop the custom `trigger` frontmatter; fold "when to use" into `description`.
- [ ] Retire `context_selector.py` in favor of runtime-native skill discovery.
- [ ] Keep `skill_sync.py` only to regenerate the `AGENTS.md` tables (anti-drift), or retire it once tables become generated-on-demand.

### Phase 5 — Observability simplification 🟢 LOW
- [ ] Declare ONE canonical metric source per dimension (already partially done); remove `ai-ctx` aggregation from the reporting path.
- [ ] Add a trend report that consumes the session log (replaces `session_index.py`).

---

## 6. Success Criteria

| Criterion | Now (Gen 6/7) | Target (Gen 8) |
|:---|:---|:---|
| Tooling scripts | ~30 | ~15, no overlapping responsibility |
| Roles enforced | advisory text | native subagents, auditor `edit: deny` |
| Skill format | custom `trigger` | standard `name`+`description` |
| Session memory | compaction + files | durable append-only log |
| Metric provenance | multi-tool | single canonical source per dimension |
| Thresholds | hard-coded | externalized config |

---

## 7. References

- Anthropic — [Building Effective Agents](https://www.anthropic.com/engineering/building-effective-agents) (2024, updated 2026)
- Anthropic — [Scaling Managed Agents: Decoupling the brain from the hands](https://www.anthropic.com/engineering/managed-agents) (Apr 2026)
- Anthropic — [Effective Context Engineering for AI Agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
- [Model Context Protocol (MCP)](https://modelcontextprotocol.io/)
- opencode — [Agent Skills](https://opencode.ai/docs/skills/)

---

*Proposal drafted 2026-09-13. Not yet scheduled against a phase release.*
