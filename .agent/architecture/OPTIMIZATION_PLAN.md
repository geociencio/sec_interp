# Agentic System Optimization Plan (SecInterp)

This document outlines the roadmap for the continuous evolution of the agentic system in `.agent/`, ensuring it remains at the industry's cutting edge.

## 1. Current State Identification (Gen 4)

- ✅ **Strength**: Strict role separation (Senior Architect, QA, Auditor).
- ✅ **Strength**: Context partitioning via Markdown-based Skills.
- ✅ **Strength**: Episodic and procedural memory in `AGENT_LESSONS.md`.
- ⚠️ **Gap**: Manual maintenance of `agent_metrics.json`.
- ⚠️ **Automation Gap**: No workflow for mass cleanup (linting).
- ⚠️ **Future Readiness**: Missing specific knowledge for QGIS 4.x migration.

## 2. Evolution towards Generation 5 (Cutting Edge)

Based on 2024-2025 trends, the following evolutionary leaps are proposed:

### A. MCP (Model Context Protocol) Integration
- **Concept**: Standardize access to project resources and auxiliary tools under the Anthropic/Industry protocol.
- **Benefit**: Allows any AI (IDE-independent) to consume SecInterp's Skills and Context natively and structurally.

### B. Self-Evolving Memory (Recursive Reflection)
- **Concept**: Implement a workflow that analyzes `AGENT_LESSONS.md` and automatically updates the corresponding `SKILL.md`.
- **Action**: If there are >3 lessons on the same topic, the skill is "re-trained" or refactored to absorb that knowledge permanently.

### C. Predictive Context Injection
- **Concept**: Use semantic analysis to preload a "Dynamic Mix" of skills, surpassing the current static matrix.
- **Benefit**: Reduces noise in the context window by loading only the skill fragments truly relevant to the current prompt.

### D. Autonomous QA Gates (Quality Blocking)
- **Concept**: Integrate `qgis-analyzer` into the commit workflow to forbid pushes if cyclomatic complexity increases or typing scores drop.
- **Goal**: "Zero Technical Debt Injection".

### E. Cognitive Alignment (Full English Core)
- **Concept**: Migrate 100% of system files (`.agent/*`) to technical English to maximize model reasoning precision, keeping the user communication layer in Spanish.

## 3. Implementation Proposals

### A. New Skills

#### 1. `qgis-migration-4x`
- **Purpose**: Expert guide for API transition (v3 -> v4).
- **Content**: Deprecated class mapping, `PyQt5` replacements with `qgis.PyQt`, mandatory asynchronous patterns.

#### 2. `refactoring-patterns`
- **Purpose**: Specific design patterns to reduce cyclomatic complexity.
- **Content**: Strategies for decomposing "God Classes" (like `DrillholeService` used to be).

### B. New Workflows

#### 1. `/fix-linting`
- **Purpose**: Automate style and static issue correction.
- **Steps**: Aggressive execution of `ruff --fix`, `black`, import organization.

#### 2. `/migrate-qgis4`
- **Purpose**: Guided workflow to apply the `qgis-migration-4x` skill.

### C. Memory Improvement (Agentic Brain)

#### Metrics Automation
Update the script or `agentic-memory` skill so that upon session closure (`/close-session`):
1. It reads the `qgis-analyzer` report.
2. Extracts key metrics (Score, Passed Tests, CC Avg).
3. Adds a new historical entry in `agent_metrics.json`.

## 4. Roadmap

1. **Immediate**: Implement `/fix-linting` to clean up v3.0.1.
2. **Short Term**: Create `qgis-migration-4x` skill.
3. **Medium Term**: Automate `agent_metrics.json` updates.

---
*Roadmap updated on 2026-03-15.*
