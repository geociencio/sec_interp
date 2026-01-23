# Walkthrough: Integración Workflows + AGENTS.md + Skills

**Fecha**: 2026-01-22
**Objetivo**: Integrar workflows existentes con el sistema de AGENTS.md y skills para crear un flujo de desarrollo coherente y potenciado por IA.

---

## 📋 Resumen de Cambios

### 1. Workflows Actualizados (3 archivos)

#### `/inicia-sesion` → [inicia-sesion.md](file:///home/jmbernales/qgispluginsdev/sec_interp/.agent/workflows/inicia-sesion.md)
- ✅ Añadido frontmatter YAML con `agent: Senior Architect` y `skills: [qgis-core, qa-docker]`
- ✅ Añadidos 3 checkpoints de validación
- ✅ Insertadas 3 anotaciones `🤖 Agent Action` para acciones inteligentes
- ✅ Actualizado número de tests (349 → 361)
- ✅ Actualizado plan maestro (v2.7.0 → v2.8.0)

#### `/crea-commit` → [crea-commit.md](file:///home/jmbernales/qgispluginsdev/sec_interp/.agent/workflows/crea-commit.md)
- ✅ Añadido frontmatter YAML con `agent: QA Engineer` y `skills: [qa-docker]`
- ✅ Añadidos 3 checkpoints de validación
- ✅ Insertada anotación `🤖 Agent Action` para análisis de métricas de calidad

#### `/run-tests` → [run-tests.md](file:///home/jmbernales/qgispluginsdev/sec_interp/.agent/workflows/run-tests.md)
- ✅ Añadido frontmatter YAML con `agent: QA Engineer` y `skills: [qa-docker]`
- ✅ Añadidos 2 checkpoints de validación
- ✅ Insertada anotación `🤖 Agent Action` para interpretación de fallos de tests

#### `/release-plugin` → [release-plugin.md](file:///home/jmbernales/qgispluginsdev/sec_interp/.agent/workflows/release-plugin.md)
- ✅ Añadido frontmatter YAML con `agent: QA Engineer` y `skills: [release-management, qa-docker, commit-standards]`
- ✅ Añadidos 4 checkpoints de validación
- ✅ Insertadas 10+ anotaciones `🤖 Agent Action` en las 5 fases de release
- ✅ Actualizado comando de tests (319 → 361 tests)
- ✅ Mejorado path de release notes

#### `/release-plugin-en` → [release-plugin-en.md](file:///home/jmbernales/qgispluginsdev/sec_interp/.agent/workflows/release-plugin-en.md)
- ✅ Añadido frontmatter YAML con `agent: QA Engineer` y `skills: [release-management, qa-docker, commit-standards]`
- ✅ Añadidos 4 checkpoints de validación (versión en inglés)
- ✅ Insertadas 10+ anotaciones `🤖 Agent Action` en las 5 fases de release
- ✅ Actualizado comando de tests (319 → 361 tests)
- ✅ Mejorado path de release notes

#### `/cierra-sesion` → [cierra-sesion.md](file:///home/jmbernales/qgispluginsdev/sec_interp/.agent/workflows/cierra-sesion.md)
- ✅ Añadido frontmatter YAML con `agent: QA Engineer` y `skills: [qa-docker, commit-standards]`
- ✅ Añadidos 3 checkpoints de validación
- ✅ Insertadas 5 anotaciones `🤖 Agent Action` en los 5 pasos
- ✅ Actualizado formato de commit a Conventional Commits
- ✅ Mejorado resumen final con referencia a `/inicia-sesion`

#### `/cierra-fase` → [cierra-fase.md](file:///home/jmbernales/qgispluginsdev/sec_interp/.agent/workflows/cierra-fase.md)
- ✅ Añadido frontmatter YAML con `agent: Senior Architect` y `skills: [qgis-core, qa-docker]`
- ✅ Añadidos 4 checkpoints de validación
- ✅ Insertadas 3 anotaciones `🤖 Agent Action` para análisis arquitectural
- ✅ Actualizado número de tests (361 tests)

#### `/inicia-fase` → [inicia-fase.md](file:///home/jmbernales/qgispluginsdev/sec_interp/.agent/workflows/inicia-fase.md)
- ✅ Añadido frontmatter YAML con `agent: Senior Architect` y `skills: [qgis-core, geological-logic, qa-docker]`
- ✅ Añadidos 4 checkpoints de validación
- ✅ Insertadas 2 anotaciones `🤖 Agent Action` para planificación arquitectural
- ✅ Actualizado criterio de éxito (361 tests)

#### `/run-tests-in-qgis` → [run-tests-in-qgis.md](file:///home/jmbernales/qgispluginsdev/sec_interp/.agent/workflows/run-tests-in-qgis.md)
- ✅ Añadido frontmatter YAML con `agent: QA Engineer` y `skills: [qa-docker]`
- ✅ Añadidos 3 checkpoints de validación
- ✅ Insertada anotación `🤖 Agent Action` para determinar tipo de testing necesario

### 2. Nuevo Workflow Creado

#### `/refactor-code` → [refactor-code.md](file:///home/jmbernales/qgispluginsdev/sec_interp/.agent/workflows/refactor-code.md)
- ✅ Workflow completo para refactorización guiada por skills
- ✅ Agent: Senior Architect
- ✅ Skills: qgis-core, geological-logic
- ✅ 6 pasos detallados con Agent Actions
- ✅ Ejemplo de refactorización (CC: 21 → 8)
- ✅ Validación de complejidad ciclomática

### 3. Nueva Skill Creada

#### `commit-standards` → [SKILL.md](file:///home/jmbernales/qgispluginsdev/sec_interp/.agent/skills/commit-standards/SKILL.md)
- ✅ Estándares de Conventional Commits
- ✅ Checklist de validación pre-commit (código, métricas, tests, QGIS compliance)
- ✅ Templates de mensajes por tipo (feat, fix, refactor, docs, etc.)
- ✅ Guía de scopes del proyecto (core, gui, export, ui, tests, docs, build)
- ✅ Integración con herramientas (ruff, black, ai-ctx, qgis-analyzer)
- ✅ Ejemplos buenos y malos de commits
- ✅ Referencia a [COMMIT_GUIDELINES.md](file:///home/jmbernales/qgispluginsdev/sec_interp/docs/docsec/COMMIT_GUIDELINES.md)

**Impacto**: Workflow `/crea-commit` ahora usa esta skill para generar mensajes de commit inteligentes y validar formato.

#### `release-management` → [SKILL.md](file:///home/jmbernales/qgispluginsdev/sec_interp/.agent/skills/release-management/SKILL.md)
- ✅ Proceso completo de release en 5 fases
- ✅ Checklist de validación pre-release (calidad, tests, documentación)
- ✅ Sincronización de versiones (metadata.txt, pyproject.toml, README.md)
- ✅ Generación de release notes estructuradas
- ✅ Empaquetado y distribución (GitHub + QGIS Plugin Repository)
- ✅ Troubleshooting de problemas comunes
- ✅ Integración con otras skills (commit-standards, qa-docker, qgis-core)

**Impacto**: Workflows `/release-plugin` y `/release-plugin-en` podrán usar esta skill para releases consistentes y validados.

### 4. AGENTS.md Actualizado

#### Nueva Sección: "Workflow Integration"
- ✅ Protocolo de ejecución de workflows (5 pasos)
- ✅ Tabla de workflows disponibles (4 workflows)
- ✅ Ejemplo de invocación con explicación
- ✅ Documentación de anotaciones `🤖 Agent Action`

### 4. skill_sync.py Mejorado

#### Nueva Función: `sync_workflows()`
- ✅ Lee metadata YAML de todos los workflows
- ✅ Valida que workflows tienen `agent` y `skills`
- ✅ Verifica que todos los skills referenciados existen
- ✅ Reporta workflows sin metadata (6 workflows legacy detectados)

---

## 🧪 Validación Ejecutada

### Ejecución de skill_sync.py

```bash
$ uv run python3 scripts/skill_sync.py
🔄 Syncing Skills and Workflows...

Scanning skills in /home/jmbernales/qgispluginsdev/sec_interp/.agent/skills...
✅ Successfully synchronized 6 skills into AGENTS.md

Scanning workflows in /home/jmbernales/qgispluginsdev/sec_interp/.agent/workflows...
✅ Validated 10 workflows
   All referenced skills exist: {'qgis-core', 'release-management', 'qa-docker', 'ui-framework', 'geological-logic', 'commit-standards'}

✨ Synchronization complete!
```

**Resultados Finales**:
- ✅ 6 skills sincronizados correctamente
- ✅ **10 workflows validados con metadata completa** (100% de workflows)
- ✅ Todos los skills referenciados existen
- ✅ **0 workflows legacy** - Integración completa

---

## 📊 Estructura Final

```
.agent/
├── AGENTS.md                    # ✨ Actualizado con Workflow Integration
├── skills/
│   ├── commit-standards/        # ✨ NUEVA skill
│   │   └── SKILL.md
│   ├── geological-logic/
│   │   └── SKILL.md
│   ├── qa-docker/
│   │   └── SKILL.md
│   ├── qgis-core/
│   │   └── SKILL.md
│   ├── release-management/      # ✨ NUEVA skill
│   │   └── SKILL.md
│   └── ui-framework/
│       └── SKILL.md
└── workflows/
    ├── inicia-sesion.md         # ✅ Actualizado
    ├── crea-commit.md           # ✅ Actualizado
    ├── run-tests.md             # ✅ Actualizado
    ├── refactor-code.md         # ✅ NUEVO
    ├── release-plugin.md        # ✅ Actualizado
    ├── release-plugin-en.md     # ✅ Actualizado
    ├── cierra-sesion.md         # ✅ Actualizado
    ├── cierra-fase.md           # ✅ Actualizado
    ├── inicia-fase.md           # ✅ Actualizado
    └── run-tests-in-qgis.md     # ✅ Actualizado
```

---

## 💡 Cómo Usar el Sistema Integrado (Actualizado)

### Ejemplo 1: Iniciar Sesión de Desarrollo

```bash
# Usuario invoca:
/inicia-sesion

# Sistema automáticamente:
# 1. Lee frontmatter: agent=Senior Architect, skills=[qgis-core, qa-docker]
# 2. Activa el rol "Senior Architect"
# 3. Carga conocimiento de qgis-core y qa-docker
# 4. Ejecuta pasos con contexto especializado:
#    - Analiza project_brain.md buscando deuda técnica QGIS
#    - Verifica dependencias PyQGIS
#    - Interpreta fallos de tests usando estándares de qa-docker
# 5. Valida: 361 tests OK + métricas actualizadas
```

### Ejemplo 2: Refactorizar Código Complejo

```bash
# Usuario invoca:
/refactor-code

# Sistema automáticamente:
# 1. Activa "Senior Architect Agent"
# 2. Carga skills: qgis-core, geological-logic
# 3. Analiza qgis-analyzer para identificar métodos con CC > 15
# 4. Aplica principios de qgis-core (QgsTask, separación UI/Core)
# 5. Valida que complejidad bajó y tests pasan
```

### Ejemplo 3: Crear Commit con Validación

```bash
# Usuario invoca:
/crea-commit

# Sistema automáticamente:
# 1. Activa "QA Engineer Agent"
# 2. Carga skill: qa-docker
# 3. Ejecuta ruff/black
# 4. Analiza métricas y alerta si:
#    - Complejidad aumentó
#    - Docstring coverage bajó
#    - Nuevas violaciones QGIS
# 5. Sugiere mensaje de commit siguiendo Conventional Commits
```

---

## 🎯 Beneficios Logrados

1. **Contexto Automático**: Workflows cargan automáticamente el conocimiento especializado necesario
2. **Validación Inteligente**: Checkpoints usan skills para validar correctamente
3. **Trazabilidad**: Cada workflow documenta qué agente y skills usa
4. **Mantenibilidad**: `skill_sync.py` mantiene AGENTS.md sincronizado automáticamente
5. **Escalabilidad**: Fácil añadir nuevos workflows con metadata estándar
6. **Detección de Problemas**: Script valida que skills referenciados existen

---

## 📝 Próximos Pasos (Opcional)

### Workflows Legacy a Actualizar

Los siguientes workflows pueden beneficiarse de metadata en el futuro:

1. **cierra-sesion.md** → Agent: QA Engineer, Skills: [qa-docker]
2. **cierra-fase.md** → Agent: Senior Architect, Skills: [qgis-core]
3. **inicia-fase.md** → Agent: Senior Architect, Skills: [qgis-core]
4. **release-plugin.md** → Agent: QA Engineer, Skills: [qa-docker, qgis-core]
5. **release-plugin-en.md** → Agent: QA Engineer, Skills: [qa-docker, qgis-core]
6. **run-tests-in-qgis.md** → Agent: QA Engineer, Skills: [qa-docker]

---

## ✅ Conclusión

La integración entre workflows, AGENTS.md y skills está **completa y funcional**. El sistema ahora:

- ✅ Invoca automáticamente el agente apropiado
- ✅ Carga contexto especializado de skills
- ✅ Ejecuta validaciones inteligentes
- ✅ Mantiene sincronización automática

**Estado**: ✅ Listo para uso en producción
