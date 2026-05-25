# Agent Memory Policy (SecInterp)

> Defines what the agent remembers, when it forgets, and how conflicts are resolved.
> This is the authoritative document for memory lifecycle management in the `.agent/` system.

---

## 1. Memory Tiers

The system uses a **3-tier cognitive architecture** aligned with 2025/2026 agentic standards:

| Tier | File | Purpose | Retention |
|---|---|---|---|
| **Short-term** (Working) | `AI_CONTEXT.md` | Current session state, active tasks, decisions in progress | Per session (reset on start) |
| **Episodic** (Event History) | `docs/maintenance/` (100+ session logs), `history/tasks/`, `next_steps.md` | Records of past sessions, outcomes, and decisions | 6 months → archived |
| **Semantic** (Long-term) | `AGENT_LESSONS.md`, `SKILL.md` files | Distilled patterns, user preferences, reusable procedures | Permanent (with pruning) |

---

## 2. What Is Worth Remembering

A lesson is worth adding to `AGENT_LESSONS.md` if it meets **at least one** of these criteria:

- ✅ The agent made the same mistake more than once
- ✅ The lesson prevents a class of errors that isn't obvious from the code itself
- ✅ It captures a user preference that affects all future interactions
- ✅ It documents a non-obvious QGIS API behavior or gotcha
- ✅ It resolves an architectural decision that was debated

A lesson is **NOT** worth adding if:
- ❌ It's already explicit in the codebase (e.g., a comment in the source)
- ❌ It duplicates a rule already in a `SKILL.md`
- ❌ It's specific to a single throwaway task with no recurrence potential

---

## 3. When Is a Lesson Forgotten (Pruned)

A lesson in `AGENT_LESSONS.md` should be **promoted to `[consolidated]` status** when:

| Condition | Action |
|---|---|
| Lesson is > 90 days old AND already covered by a `SKILL.md` | Mark as `[PRUNED]` in the index, remove the full entry |
| Lesson contradicts a newer lesson on the same topic | Keep the newer one, mark the older as `[SUPERSEDED]` |
| Lesson is no longer relevant (e.g., removed feature) | Mark as `[OBSOLETE]` and remove within 30 days |

**Review cadence**: Memory pruning should occur once per quarter, during `/close-phase`.

---

## 4. Conflict Resolution Policy

When two lessons contradict each other (e.g., different approaches to the same problem):

1. **Date wins**: The newer lesson takes precedence.
2. **Specificity wins**: A lesson about a specific module overrides a general guideline.
3. **User preference wins**: If the user explicitly stated a preference, it overrides any agent-generated lesson.
4. **Document the resolution**: Add a `supersedes:` field referencing the older lesson.

---

## 5. Memory Escalation Path

```
Session observation → AGENT_LESSONS.md (raw lesson)
        ↓ (when pattern repeats 2+ times)
   Relevant SKILL.md (absorbed into procedural knowledge)
        ↓ (when lesson applies to all agents globally)
        AGENTS.md or AGENTS.md constraint
```

---

## 6. Context Compaction Strategy

To avoid **memory bloat** (a primary cause of agent performance degradation):

- `AGENT_LESSONS.md` must stay **under 350 lines** of active content.
- If the file exceeds this limit, run `uv run python scripts/prune_consolidated.py` to move `consolidated_in` lessons to the `[PRUNED]` index. If still over, consolidate the oldest lessons into their respective `SKILL.md` files.
- Pruned entries are retained as a one-line comment index (e.g., `# [PRUNED] 2026-01-15 TESTING/topic → qa-docker/SKILL.md`).
- `AI_CONTEXT.md` is **reset at the start of every session** — it is never a long-term store.

---

## 7. Prohibited Memory Content

The following must **never** appear in `AGENT_LESSONS.md`:

- ❌ Secrets, credentials, or access tokens
- ❌ Personally identifiable information (PII)
- ❌ Raw stack traces or full error logs (summarize instead)
- ❌ More than 5 lines of code (link to file instead)
- ❌ Content in languages other than English (agentic system is English-only)

---

## 8. Review Schedule

| Review Type | Cadence | Owner | Triggered By |
|---|---|---|---|
| **Memory Pruning** | Quarterly | Agent (auto) | `/close-phase` workflow |
| **Skill Promotion** | On demand | Agent | Pattern repeats 2+ times |
| **Policy Review** | Biannually | Human | Major framework version upgrade |

---

*Created: 2026-04-27 — Gen 5 Memory Policy v1.0*
*Next review: 2026-10-27*
