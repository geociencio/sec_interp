---
description: Procedimiento formal para iniciar una nueva fase de desarrollo mayor
agent: Senior Architect
skills: [qgis-core, geological-logic, qa-docker]
validation: |
  - Verificar que implementation_plan está creado y completo
  - Confirmar que 361 tests pasan antes de iniciar
  - Validar que objetivos están claros y priorizados
  - Verificar que next_steps.md está actualizado
---

# Workflow: Apertura de Fase

Este workflow documenta el proceso completo para iniciar formalmente una nueva fase de desarrollo mayor (ej: v2.7.0 → v2.8.0).

## 1. Revisión del Cierre de Fase Anterior

🤖 **Agent Action**: Analizar documento de cierre y extraer deuda técnica priorizada.

Lee el documento de cierre de la fase anterior:

```bash
cat docs/maintenance/phase_closure_v[ANTERIOR].md
```

Identifica:
- Deuda técnica heredada (priorizada)
- Recomendaciones para la nueva fase
- Métricas base para comparación

## 2. Definición de Objetivos de la Nueva Fase

Crea un documento de planificación en `docs/plans/implementation_plan_vX.Y.Z.md`:

```markdown
# Plan de Implementación - Fase vX.Y.Z ([Nombre de la Fase])

## Objetivo General
[Descripción clara del propósito de esta fase]

---

## User Review Required

> [!IMPORTANT]
> **Decisiones Críticas**
>
> [Lista de decisiones arquitectónicas o de diseño que requieren aprobación]

---

## Proposed Changes

### Objetivo 1: [Nombre del Objetivo]

#### Contexto
[Por qué es necesario este objetivo]

#### Componentes a Implementar

##### [NEW/MODIFY] [archivo](file:///ruta/absoluta)
[Descripción de cambios]

#### Estimación Detallada

| Componente | Esfuerzo | Fase |
|-----------|----------|------|
| ... | X horas | Sprint Y |

---

## Verification Plan

### 1. [Tipo de Verificación]
[Comandos y criterios de éxito]

---

## Estimación de Esfuerzo Total

| Objetivo | Esfuerzo | Prioridad |
|----------|----------|-----------|
| ... | X días | Alta/Media/Baja |
```

## 3. Análisis del Estado Actual

Ejecuta el análisis completo del proyecto:

// turbo
```bash
uv run ai-ctx analyze --path .
```

Documenta el estado base:
- Número de archivos Python
- Tests totales
- Métricas de calidad (Pylint, Type Hints, Docstrings)
- Complejidad ciclomática promedio

## 4. Verificación de Estabilidad

🤖 **Agent Action**: Usar skill **qa-docker** para validar estabilidad base.

Asegura que el proyecto está en estado estable antes de comenzar:

// turbo
```bash
make docker-test
```

**Criterio de Éxito**: 361 tests unitarios pasando (100% success rate).

## 5. Sincronización de Entorno

Actualiza las dependencias y herramientas:

// turbo
```bash
uv sync
```

Verifica que el entorno local está limpio:

```bash
git status
```

Si hay cambios sin commitear, evalúa si deben ser parte de la fase anterior o descartados.

## 6. Creación de Estructura de Seguimiento

Crea el archivo de tareas en `.agent/task.md` (si usas artifacts de IA):

```markdown
# Tareas - Fase vX.Y.Z

## Objetivo 1: [Nombre]
- [ ] Sub-tarea 1 <!-- id: 1 -->
- [ ] Sub-tarea 2 <!-- id: 2 -->

## Objetivo 2: [Nombre]
- [ ] Sub-tarea 1 <!-- id: 3 -->
```

## 7. Actualización de CHANGELOG

Prepara la sección `[Unreleased]` en `docs/CHANGELOG.md`:

```markdown
## [Unreleased]

### Added
- [Pendiente de documentar durante la fase]

### Changed
- [Pendiente de documentar durante la fase]

### Fixed
- [Pendiente de documentar durante la fase]
```

## 8. Comunicación de Inicio

Documenta el inicio de fase en `docs/DEVELOPMENT_LOG.md`:

```markdown
## [YYYY-MM-DD] Inicio de Fase vX.Y.Z
- **Objetivo**: [Descripción breve]
- **Duración Estimada**: X semanas
- **Prioridades**: [Lista de objetivos principales]
```

## 9. Configuración de Workflows de IA (si aplica)

Actualiza `.agent/next_steps.md` con el contexto de la nueva fase:

```markdown
# Siguientes Pasos - SecInterp vX.Y.Z

La **Fase vX.Y.Z ([Nombre])** ha iniciado. Los objetivos principales son:

1. [Objetivo 1]
2. [Objetivo 2]
3. [Objetivo 3]

## Cómo Retomar
Para iniciar una sesión de desarrollo:
```bash
/inicia-sesion
```

**Estado Actual**: Estable. Plan de implementación aprobado.
```

## 10. Primer Commit de Fase

Crea un commit inicial marcando el inicio de la fase:

```bash
git add docs/plans/implementation_plan_vX.Y.Z.md docs/DEVELOPMENT_LOG.md .agent/next_steps.md
git commit -m "chore: initialize phase vX.Y.Z - [Nombre de la Fase]

- Created implementation plan with [N] objectives
- Updated development log with phase start
- Prepared tracking structure"
```

---

**Filosofía**: Una fase bien iniciada es una fase medio completada. La claridad en los objetivos y la documentación del estado base son fundamentales para el éxito.
