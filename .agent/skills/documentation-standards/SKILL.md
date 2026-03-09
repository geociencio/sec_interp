---
name: documentation-standards
description: Standards for maintaining technical logs, session records, and project history.
trigger: when updating DEVELOPMENT_LOG.md, MAINTENANCE_LOG.md, CHANGELOG.md or creating session reports in docs/maintenance/.
---

# Skill: Documentation Standards

This skill defines the precise formats to ensure that all agents (human or AI) maintain consistent and professional documentation.

## 1. Session Log Maintenance

### 1.1. `docs/DEVELOPMENT_LOG.md`
This file is the reverse chronological record of **daily activity**.

**Format:**
```markdown
## [YYYY-MM-DD] [SHORT TOPIC]
- **Achievement**: A sentence summarizing the main impact.
- **Changes**:
    - Relevant technical detail 1 (mention modules if applicable).
    - Relevant technical detail 2.
- **Quality**: Test status (e.g., 535/535 OK) and ruff/black metrics.
- **Maintenance**: Link to the maintenance log [session_YYYY-MM-DD_topic.md](maintenance/session_YYYY-MM-DD_topic.md).
```

---

### 1.2. `docs/source/MAINTENANCE_LOG.md`
This file is the structural record of **infrastructure and releases**.

**Levels Rule:**
- **Recent Entries (Ongoing Phase)**: `##` (H2) levels.
- **Project History**: `###` (H3) levels under the main version header.

**Recent Entry Format:**
```markdown
## [YYYY-MM-DD] [INFRASTRUCTURE TITLE IN ALL CAPS]
- **Changes**: Summary of changes in infrastructure or engine.
- **Metrics/Impact**: What improved after this session.
```

**History Format (Project History):**
```markdown
### [vX.Y.Z] - YYYY-MM-DD
- **Summary**: General description of the release.
- **Key Achievements**:
    - Achievement 1
    - Achievement 2
- **Reference**: Link to the phase closure or implementation plan.
```

---

### 1.3. `docs/maintenance/session_*.md`
Detailed technical report of the session.

**Required Structure:**
1. **Title**: `# Maintenance Session: YYYY-MM-DD - [Title]`
2. **Technical Summary**: Brief paragraph of the objective.
3. **Changes Made**: Categorized list.
4. **Verification Results**: Status of tests and linting.
5. **Impact**: Technical consequence of the change.

---

## 2. Writing Rules
1. **Language**: Content must be in **English** (standardized).
2. **Commit Style**: Commits remain in **English**.
3. **Markdown**: Use bolding to highlight key terms and backticks for file or function names.
4. **Dates**: Always in `YYYY-MM-DD` format.

## 3. Audit Checklist
- [ ] Did I use the `## [YYYY-MM-DD]` header correctly?
- [ ] Did I include the link to the corresponding maintenance file?
- [ ] Is the tone technical and precise without redundancies?
- [ ] Did I update the "Project History" section if it's a phase closure?
