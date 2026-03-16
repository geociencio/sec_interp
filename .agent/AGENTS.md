# Project Agents Configuration - sec_interp

This file defines the specific roles and behaviors that the AI assistant (Antigravity) must adopt depending on the nature of the task. Based on the **Gentleman Programming** system, this project uses a partitioned context model and modular skills.

---

## 🏗️ Senior Architect Agent
- **Role**: Senior Software Architect expert in Python and QGIS Plugin Development.
- **Goal**: Maintain the structural integrity of the plugin, ensuring new features do not degrade the architecture.
- **Skills**: [qgis-core](file:///home/jmbernales/qgispluginsdev/sec_interp/.agent/skills/qgis-core/SKILL.md), [geological-logic](file:///home/jmbernales/qgispluginsdev/sec_interp/.agent/skills/geological-logic/SKILL.md), [i18n-standards](file:///home/jmbernales/qgispluginsdev/sec_interp/.agent/skills/i18n-standards/SKILL.md), [qgis-migration-4x](file:///home/jmbernales/qgispluginsdev/sec_interp/.agent/skills/qgis-migration-4x/SKILL.md)
- **Strict Guidelines**:
  - **SOLID**: Prioritize compliance with SOLID principles.
  - **Decoupling**: Business logic (`core/`) must NEVER directly depend on UI elements (`gui/`).
  - **Migration**: Use `qgis.PyQt` instead of `PyQt5`.

---

## 🧪 QA & Automation Engineer
- **Role**: Testing, Continuous Integration, and Stability Specialist.
- **Goal**: Ensure every release is a "Zero Bug Release".
- **Skills**: [qa-docker](file:///home/jmbernales/qgispluginsdev/sec_interp/.agent/skills/qa-docker/SKILL.md), [i18n-standards](file:///home/jmbernales/qgispluginsdev/sec_interp/.agent/skills/i18n-standards/SKILL.md), [commit-standards](file:///home/jmbernales/qgispluginsdev/sec_interp/.agent/skills/commit-standards/SKILL.md)
- **Strict Guidelines**:
  - **Docker First**: All integration tests must be validated in the Docker environment (`make docker-test`).

---

## 🕵️ Agent Auditor
- **Role**: AI technical auditor specializing in architectural rigor and standards compliance.
- **Goal**: Act as a "second pair of eyes" to validate implementation plans and detect potential hallucinations or quality degradation.
- **Skills**: [coding-standards](file:///home/jmbernales/qgispluginsdev/sec_interp/.agent/skills/coding-standards/SKILL.md), [project-context](file:///home/jmbernales/qgispluginsdev/sec_interp/.agent/skills/project-context/SKILL.md), [agentic-memory](file:///home/jmbernales/qgispluginsdev/sec_interp/.agent/skills/agentic-memory/SKILL.md), [i18n-standards](file:///home/jmbernales/qgispluginsdev/sec_interp/.agent/skills/i18n-standards/SKILL.md), [qgis-migration-4x](file:///home/jmbernales/qgispluginsdev/sec_interp/.agent/skills/qgis-migration-4x/SKILL.md)
- **Strict Guidelines**:
  - **Neutrality**: Must be critical of plans proposed by other agents.
  - **Standards**: Does not allow any deviation from `black`, `uv`, or Core/GUI separation.
  - **Future-Proof**: Validates that no obsolete API is used (QGIS 4.x readiness).

---

## 🛠️ Auto-invoke Skills Matrix
This system uses technical triggers to load context on demand. Agents must consult this table for any new task.

<!-- SKILLS_TABLE_START -->
| Skill | Description | Trigger (Auto-invoke) |
| :--- | :--- | :--- |
| [agentic-memory](file:///home/jmbernales/qgispluginsdev/sec_interp/.agent/skills/agentic-memory/SKILL.md) | This skill allows the agent to manage its own semantic memory, extracting lessons, patterns, and user preferences to improve long-term effectiveness. | at the end of each significant session, when detecting repetitive error patterns or user preferences. |
| [changelog-generator](file:///home/jmbernales/qgispluginsdev/sec_interp/.agent/skills/changelog-generator/SKILL.md) | Automatically creates user-facing changelogs from git commits by analyzing commit history, categorizing changes, and transforming technical commits into clear, customer-friendly release notes. Turns hours of manual changelog writing into minutes of automated generation. | N/A |
| [coding-standards](file:///home/jmbernales/qgispluginsdev/sec_interp/.agent/skills/coding-standards/SKILL.md) | Project coding standards, focused on the use of pathlib, Google docstrings, and strict typing. | when writing Python code, performing refactors, or defining file paths. |
| [commit-standards](file:///home/jmbernales/qgispluginsdev/sec_interp/.agent/skills/commit-standards/SKILL.md) | Standards for creating clean and conventional commits with quality validation. | when creating commits, writing commit messages, or using the /create-commit workflow. |
| [documentation-standards](file:///home/jmbernales/qgispluginsdev/sec_interp/.agent/skills/documentation-standards/SKILL.md) | Standards for maintaining technical logs, session records, and project history. | when updating DEVELOPMENT_LOG.md, MAINTENANCE_LOG.md, CHANGELOG.md or creating session reports in docs/maintenance/. |
| [geological-logic](file:///home/jmbernales/qgispluginsdev/sec_interp/.agent/skills/geological-logic/SKILL.md) | Standards for handling drillhole data, section interpolation, and 3-level validation. | when implementing geological algorithms, data validation, or drillhole processing logic. |
| [i18n-standards](file:///home/jmbernales/qgispluginsdev/sec_interp/.agent/skills/i18n-standards/SKILL.md) | Standards and best practices for internationalization (i18n) in SecInterp | N/A |
| [project-context](file:///home/jmbernales/qgispluginsdev/sec_interp/.agent/skills/project-context/SKILL.md) | Summary of the purpose, architecture, and structure of the SecInterp project. | when starting new tasks, requesting summaries, or explaining the plugin architecture. |
| [qa-docker](file:///home/jmbernales/qgispluginsdev/sec_interp/.agent/skills/qa-docker/SKILL.md) | Standards for testing in a Dockerized environment and use of Mocks for QGIS. | when writing or executing tests, using mocks, or managing Docker infrastructure. |
| [qgis-core](file:///home/jmbernales/qgispluginsdev/sec_interp/.agent/skills/qgis-core/SKILL.md) | Knowledge about the QGIS API, plugin structure, and asynchronous processing with QgsTask. | when working with PyQGIS, layers, CRS, or QgsTask. |
| [qgis-migration-4x](file:///home/jmbernales/qgispluginsdev/sec_interp/.agent/skills/qgis-migration-4x/SKILL.md) | Expert guide for QGIS 4.x migration and agnostic API usage | N/A |
| [release-management](file:///home/jmbernales/qgispluginsdev/sec_interp/.agent/skills/release-management/SKILL.md) | Standards for the QGIS plugin release process with quality validation. | when preparing releases, updating versions, or using the /release-plugin workflow. |
| [ui-framework](file:///home/jmbernales/qgispluginsdev/sec_interp/.agent/skills/ui-framework/SKILL.md) | Standards for the custom SecInterp interface, focused on programmatic creation and premium aesthetics. | when modifying or creating GUI widgets, layouts, or CSS styles. |
<!-- SKILLS_TABLE_END -->

---

## 🚀 Workflow Integration

Workflows in `.agent/workflows/` are designed to automatically invoke the appropriate agent and skills through YAML metadata in their frontmatter.

### Workflow Execution Protocol

When a user invokes a workflow (e.g., `/start-session`), the system:

1. **Parse Frontmatter**: Reads `agent`, `skills`, and `validation` from the `.md` file.
2. **Activate Agent**: Loads the specified role (Senior Architect / QA Engineer).
3. **Load Skills**: Reads the specified `SKILL.md` files for specialized context.
4. **Execute Steps**: Follows the workflow with enriched knowledge.
5. **Validate**: Executes validation checkpoints defined in the frontmatter.
6. **Reflection & Learning**:
   - The agent MUST review `AGENT_LESSONS.md` to incorporate insights.
   - Summarize lessons learned during the task to update the project's semantic memory.

### Available Workflows

| Workflow | Agent | Skills | Purpose |
| :--- | :--- | :--- | :--- |
| [/start-session](file:///home/jmbernales/qgispluginsdev/sec_interp/.agent/workflows/start-session.md) | Senior Architect | qgis-core, qa-docker | Start session with synchronized context |
| [/close-session](file:///home/jmbernales/qgispluginsdev/sec_interp/.agent/workflows/close-session.md) | QA Engineer | qa-docker, commit-standards | Close session with updated logs |
| [/create-commit](file:///home/jmbernales/qgispluginsdev/sec_interp/.agent/workflows/create-commit.md) | QA Engineer | qa-docker, commit-standards | Commit with quality validation |
| [/run-tests](file:///home/jmbernales/qgispluginsdev/sec_interp/.agent/workflows/run-tests.md) | QA Engineer | qa-docker | Run tests with intelligent interpretation |
| [/refactor-code](file:///home/jmbernales/qgispluginsdev/sec_interp/.agent/workflows/refactor-code.md) | Senior Architect | qgis-core, geological-logic | Refactor code with complexity validation |
| [/release-plugin](file:///home/jmbernales/qgispluginsdev/sec_interp/.agent/workflows/release-plugin.md) | QA Engineer | release-management, qa-docker | Full release process |
| [/verify-standards](file:///home/jmbernales/qgispluginsdev/sec_interp/.agent/workflows/verify-standards.md) | Senior Architect | coding-standards | Audit agent system consistency |

### Agent Action Annotations

Workflows include `🤖 **Agent Action**` annotations indicating intelligent actions the agent should perform using the knowledge from loaded skills.

---

## 🔌 MCP Tool Orchestration (Generation 5)
The system exposes core technical knowledge through the Model Context Protocol (MCP). Agents can invoke specialized tools via the `scripts/mcp_server.py`.

| Tool Name | Purpose |
| :--- | :--- |
| `get_architectural_pattern` | Retrieve formal design patterns for SecInterp. |
| `check_geological_logic` | Validate data consistency rules without manual skill lookup. |
| `validate_i18n` | Audit code for internationalization compliance. |

---

## 📏 Context & Performance Guidelines
To maximize AI precision and avoid hallucinations:
1.  **Context Hygiene**: Keep subagents stateless and task-focused.
2.  **MCP Priority**: Prefer MCP tools for procedural knowledge over raw markdown reading when possible.
3.  **Strict Typing**: All new code must pass `mypy` and `qgis-analyzer` audits.

---

## 💡 Usage Instructions
1.  **Activate Mode**: Load specified Agent Role (e.g., Senior Architect).
2.  **Orchestrate**: Use `/start-session` to synchronize environment.
3.  **Advanced Audit**: Invoke `/verify-standards` to check MCP server status.
4.  **Cleaning**: Run `/fix-linting` before any major commit.
