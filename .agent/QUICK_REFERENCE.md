# Guía Rápida: Sistema de Workflows + Skills

**Fecha de creación**: 2026-01-22
**Versión**: 1.0

---

## 📋 Resumen Ejecutivo

El proyecto SecInterp cuenta con un sistema completo de **6 skills** y **10 workflows** integrados que automatizan la invocación de agentes especializados y conocimiento contextual.

---

## 🛠️ Skills Disponibles (6)

| Skill | Descripción | Cuándo Usar |
|:------|:------------|:------------|
| [commit-standards](file:///home/jmbernales/qgispluginsdev/sec_interp/.agent/skills/commit-standards/SKILL.md) | Estándares de Conventional Commits | Al crear commits, validar mensajes |
| [geological-logic](file:///home/jmbernales/qgispluginsdev/sec_interp/.agent/skills/geological-logic/SKILL.md) | Lógica geológica y validación 3-niveles | Al trabajar con drillholes, interpolación |
| [qa-docker](file:///home/jmbernales/qgispluginsdev/sec_interp/.agent/skills/qa-docker/SKILL.md) | Testing en Docker y mocks QGIS | Al escribir/ejecutar tests, usar mocks |
| [qgis-core](file:///home/jmbernales/qgispluginsdev/sec_interp/.agent/skills/qgis-core/SKILL.md) | QGIS API y estructura de plugins | Al trabajar con PyQGIS, QgsTask |
| [release-management](file:///home/jmbernales/qgispluginsdev/sec_interp/.agent/skills/release-management/SKILL.md) | Proceso de release QGIS | Al preparar releases, versionar |
| [ui-framework](file:///home/jmbernales/qgispluginsdev/sec_interp/.agent/skills/ui-framework/SKILL.md) | UI programática y estética premium | Al modificar GUI, layouts, CSS |

---

## 🔄 Workflows Disponibles (10)

### Desarrollo Diario

| Workflow | Agent | Skills | Propósito |
|:---------|:------|:-------|:----------|
| [/inicia-sesion](file:///home/jmbernales/qgispluginsdev/sec_interp/.agent/workflows/inicia-sesion.md) | Senior Architect | qgis-core, qa-docker | Iniciar sesión con contexto sincronizado |
| [/crea-commit](file:///home/jmbernales/qgispluginsdev/sec_interp/.agent/workflows/crea-commit.md) | QA Engineer | qa-docker, commit-standards | Commit con validación de calidad |
| [/run-tests](file:///home/jmbernales/qgispluginsdev/sec_interp/.agent/workflows/run-tests.md) | QA Engineer | qa-docker | Ejecutar tests con interpretación inteligente |
| [/cierra-sesion](file:///home/jmbernales/qgispluginsdev/sec_interp/.agent/workflows/cierra-sesion.md) | QA Engineer | qa-docker, commit-standards | Cerrar sesión con logs actualizados |

### Refactorización y Calidad

| Workflow | Agent | Skills | Propósito |
|:---------|:------|:-------|:----------|
| [/refactor-code](file:///home/jmbernales/qgispluginsdev/sec_interp/.agent/workflows/refactor-code.md) | Senior Architect | qgis-core, geological-logic | Refactorizar código con validación de complejidad |
| [/run-tests-in-qgis](file:///home/jmbernales/qgispluginsdev/sec_interp/.agent/workflows/run-tests-in-qgis.md) | QA Engineer | qa-docker | Tests de integración en QGIS real |

### Release Management

| Workflow | Agent | Skills | Propósito |
|:---------|:------|:-------|:----------|
| [/release-plugin](file:///home/jmbernales/qgispluginsdev/sec_interp/.agent/workflows/release-plugin.md) | QA Engineer | release-management, qa-docker, commit-standards | Release completo (español) |
| [/release-plugin-en](file:///home/jmbernales/qgispluginsdev/sec_interp/.agent/workflows/release-plugin-en.md) | QA Engineer | release-management, qa-docker, commit-standards | Release completo (inglés) |

### Gestión de Fases

| Workflow | Agent | Skills | Propósito |
|:---------|:------|:-------|:----------|
| [/inicia-fase](file:///home/jmbernales/qgispluginsdev/sec_interp/.agent/workflows/inicia-fase.md) | Senior Architect | qgis-core, geological-logic, qa-docker | Iniciar fase mayor con planificación |
| [/cierra-fase](file:///home/jmbernales/qgispluginsdev/sec_interp/.agent/workflows/cierra-fase.md) | Senior Architect | qgis-core, qa-docker | Cerrar fase con métricas y retrospectiva |

---

## 🎯 Casos de Uso Comunes

### Iniciar Sesión de Desarrollo
```bash
/inicia-sesion
```
**Qué hace**:
- Activa "Senior Architect Agent"
- Carga skills: qgis-core, qa-docker
- Sincroniza contexto (project_brain.md, next_steps.md)
- Ejecuta `make docker-test` (361 tests)
- Valida métricas de calidad

### Crear Commit con Validación
```bash
/crea-commit
```
**Qué hace**:
- Activa "QA Engineer Agent"
- Carga skills: qa-docker, commit-standards
- Ejecuta ruff/black
- Analiza métricas (ai-ctx analyze)
- Genera 2-3 opciones de mensaje siguiendo Conventional Commits
- Valida formato y scope

### Refactorizar Código Complejo
```bash
/refactor-code
```
**Qué hace**:
- Activa "Senior Architect Agent"
- Carga skills: qgis-core, geological-logic
- Analiza qgis-analyzer para CC > 15
- Aplica principios de qgis-core (QgsTask, separación UI/Core)
- Valida que complejidad bajó y tests pasan

### Preparar Release
```bash
/release-plugin
```
**Qué hace**:
- Activa "QA Engineer Agent"
- Carga skills: release-management, qa-docker, commit-standards
- Ejecuta 5 fases: Calidad → Versionamiento → Verificación → Git → Distribución
- Valida 361 tests, sincroniza versiones, genera ZIP
- Crea GitHub release draft

---

## 📊 Métricas del Sistema

**Estado Actual**:
- ✅ 6 skills sincronizadas
- ✅ 10 workflows con metadata completa (100%)
- ✅ 0 workflows legacy
- ✅ Todos los skills referenciados validados

**Tests**:
- 361 tests totales
- 100% success rate en Docker
- Cobertura completa de mocking QGIS

**Calidad**:
- Code Maintainability Score: 100/100
- Overall Plugin Score: 27.6/100 (qgis-analyzer)
- ai-ctx Quality Score: 54.6/100

---

## 🔧 Mantenimiento

### Sincronizar Skills y Workflows
```bash
uv run python3 scripts/skill_sync.py
```

### Añadir Nueva Skill
1. Crear directorio: `.agent/skills/[nombre-skill]/`
2. Crear `SKILL.md` con frontmatter YAML:
   ```yaml
   ---
   name: nombre-skill
   description: Descripción breve
   trigger: cuándo auto-invocar
   scope: root
   ---
   ```
3. Ejecutar `skill_sync.py`

### Añadir Nuevo Workflow
1. Crear archivo: `.agent/workflows/[nombre].md`
2. Añadir frontmatter YAML:
   ```yaml
   ---
   description: Descripción del workflow
   agent: Senior Architect | QA Engineer
   skills: [skill1, skill2]
   validation: |
     - Checkpoint 1
     - Checkpoint 2
   ---
   ```
3. Añadir anotaciones `🤖 **Agent Action**` en pasos clave
4. Ejecutar `skill_sync.py`

---

## 📚 Referencias

- [AGENTS.md](file:///home/jmbernales/qgispluginsdev/sec_interp/.agent/AGENTS.md) - Definición completa de agentes y skills
- [Walkthrough Completo](file:///home/jmbernales/.gemini/antigravity/brain/fe1d94d9-ce70-4d55-a314-e8970f56c6d4/walkthrough.md) - Documentación detallada de la integración
- [Implementation Plan](file:///home/jmbernales/.gemini/antigravity/brain/fe1d94d9-ce70-4d55-a314-e8970f56c6d4/implementation_plan.md) - Plan original de integración

---

**Última actualización**: 2026-01-22
**Versión del sistema**: 1.0 (Integración completa)
