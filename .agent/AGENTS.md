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
- **Goal**: Ensure every release v2.8.x+ is a "Zero Bug Release".
- **Skills**: [qa-docker](file:///home/jmbernales/qgispluginsdev/sec_interp/.agent/skills/qa-docker/SKILL.md), [i18n-standards](file:///home/jmbernales/qgispluginsdev/sec_interp/.agent/skills/i18n-standards/SKILL.md)
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
| [coding-standards](file:///home/jmbernales/qgispluginsdev/sec_interp/.agent/skills/coding-standards/SKILL.md) | Estándares de codificación del proyecto, enfocados en el uso de pathlib, docstrings de Google y tipado estricto. | al escribir código Python, realizar refactorizaciones o definir rutas de archivos. |
| [commit-standards](file:///home/jmbernales/qgispluginsdev/sec_interp/.agent/skills/commit-standards/SKILL.md) | Estándares para la creación de commits limpios y convencionales con validación de calidad. | al crear commits, escribir mensajes de commit o usar el workflow /crea-commit |
| [documentation-standards](file:///home/jmbernales/qgispluginsdev/sec_interp/.agent/skills/documentation-standards/SKILL.md) | Estándares para el mantenimiento de logs técnicos, registros de sesión e historial del proyecto. | al actualizar DEVELOPMENT_LOG.md, MAINTENANCE_LOG.md, CHANGELOG.md o crear reportes de sesión en docs/maintenance/. |
| [geological-logic](file:///home/jmbernales/qgispluginsdev/sec_interp/.agent/skills/geological-logic/SKILL.md) | Estándares para el manejo de datos de sondajes, interpolación de secciones y validación de 3 niveles. | al implementar algoritmos geológicos, validación de datos o lógica de procesamiento de sondajes. |
| [i18n-standards](file:///home/jmbernales/qgispluginsdev/sec_interp/.agent/skills/i18n-standards/SKILL.md) | Standards and best practices for internationalization (i18n) in SecInterp | N/A |
| [project-context](file:///home/jmbernales/qgispluginsdev/sec_interp/.agent/skills/project-context/SKILL.md) | Resumen del propósito, arquitectura y estructura del proyecto SecInterp. | al iniciar nuevas tareas, solicitar resúmenes o explicar la arquitectura del plugin. |
| [qa-docker](file:///home/jmbernales/qgispluginsdev/sec_interp/.agent/skills/qa-docker/SKILL.md) | Estándares para pruebas en entorno Dockerizado y uso de Mocks para QGIS. | al escribir o ejecutar tests, usar mocks o manejar infraestructura Docker. |
| [qgis-core](file:///home/jmbernales/qgispluginsdev/sec_interp/.agent/skills/qgis-core/SKILL.md) | Conocimiento sobre la API de QGIS, estructura de plugins y procesamiento asíncrono con QgsTask. | al trabajar con PyQGIS, capas, CRS o QgsTask. |
| [qgis-migration-4x](file:///home/jmbernales/qgispluginsdev/sec_interp/.agent/skills/qgis-migration-4x/SKILL.md) | Expert guide for QGIS 4.x migration and agnostic API usage | N/A |
| [release-management](file:///home/jmbernales/qgispluginsdev/sec_interp/.agent/skills/release-management/SKILL.md) | Estándares para el proceso de liberación del plugin QGIS con validación de calidad. | al preparar lanzamientos, actualizar versiones o usar el workflow /release-plugin |
| [ui-framework](file:///home/jmbernales/qgispluginsdev/sec_interp/.agent/skills/ui-framework/SKILL.md) | Estándares para la interfaz personalizada de SecInterp, enfocados en creación programática y estética premium. | al modificar o crear widgets de GUI, layouts o estilos CSS. |
<!-- SKILLS_TABLE_END -->

---

## 🚀 Workflow Integration

Workflows in `.agent/workflows/` are designed to automatically invoke the appropriate agent and skills through YAML metadata in their frontmatter.

### Workflow Execution Protocol

When a user invokes a workflow (e.g., `/inicia-sesion`), the system:

1. **Parse Frontmatter**: Reads `agent`, `skills`, and `validation` from the `.md` file.
2. **Activate Agent**: Loads the specified role (Senior Architect / QA Engineer).
3. **Load Skills**: Reads the specified `SKILL.md` files for specialized context.
4. **Execute Steps**: Follows the workflow with enriched knowledge.
5. **Validate**: Executes validation checkpoints defined in the frontmatter.

### Available Workflows

| Workflow | Agent | Skills | Purpose |
| :--- | :--- | :--- | :--- |
| [/inicia-sesion](file:///home/jmbernales/qgispluginsdev/sec_interp/.agent/workflows/inicia-sesion.md) | Senior Architect | qgis-core, qa-docker | Start session with synchronized context |
| [/crea-commit](file:///home/jmbernales/qgispluginsdev/sec_interp/.agent/workflows/crea-commit.md) | QA Engineer | qa-docker | Commit with quality validation |
| [/run-tests](file:///home/jmbernales/qgispluginsdev/sec_interp/.agent/workflows/run-tests.md) | QA Engineer | qa-docker | Run tests with intelligent interpretation |
| [/refactor-code](file:///home/jmbernales/qgispluginsdev/sec_interp/.agent/workflows/refactor-code.md) | Senior Architect | qgis-core, geological-logic | Refactor code with complexity validation |

### Agent Action Annotations

Workflows include `🤖 **Agent Action**` annotations indicating intelligent actions the agent should perform using the knowledge from loaded skills.

---

## 📏 Context & Performance Guidelines
To maximize AI precision and avoid hallucinations:
1.  **Keep it Small**: Instruction files (`SKILL.md`, `AGENTS.md`) should be kept between 250 and 500 lines.
2.  **Explicit Triggers**: When a task matching a trigger is detected, the agent MUST announce that it is applying that Skill.
3.  **Modular Context**: If functionality grows too large, a specific `AGENTS.md` should be created in its subdirectory (e.g., `gui/AGENTS.md`).

---

## 💡 Usage Instructions
1.  **Invoke the Agent**: *"Activate the Architect Agent"*.
2.  **Load a Skill**: *"Use the qgis-core skill to review this QgsTask"*.
3.  **Synchronization**: When adding skills, run `python3 scripts/skill_sync.py` to update this guide.
