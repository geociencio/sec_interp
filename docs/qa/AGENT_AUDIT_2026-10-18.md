# Auditoría de `.agent` — Agentic Forge v1.2

> Análisis del subsistema agéntico: framework, skills, workflows, herramientas, memoria, métricas y su integración con `.agent-state`.
> **Fecha:** 2026-10-18 · **Submódulo:** `96a70d9` (`v1.2.0-1-g96a70d9`) · **Remoto:** `codeberg.org/geociencio/agentic-forge` · **Licencia:** MIT
> **Alcance:** `.agent/` (56 archivos, 464 KB) + `.agent-state/` (61 archivos, 740 KB) + `forge.toml`, `opencode.json` y scripts de integración.
> **Estado del submódulo:** limpio, sin cambios locales; el superproyecto apunta a `96a70d9`.

---

## Resumen ejecutivo

| Dimensión | Valoración | Hallazgo clave |
|---|---|---|
| Diseño y estructura | 🟢 Buena | Separación framework/estado, skills on-demand, CLI único y path model sólido |
| Validación estructural | 🟡 Media | `forge validate` pasa, pero **no valida los 4 workflows del overlay** |
| Memoria | 🔴 Débil | **1.057 líneas / 98 lecciones** frente al límite de 350; poda de lecciones inoperante |
| Métricas | 🔴 Débil | `tests_ok=792` es un conteo estático, no tests ejecutados; 36 issues vs 37 del analizador |
| Handoff (`task.md`) | 🔴 Débil | Sigue indicando v3.9.1, v3.10/v3.11 “programadas” y `legend_widget` pendiente |
| Calidad del código de herramientas | 🟡 Media | 1.855 líneas, **21 errores de ruff**, 4 archivos sin formatear, sin CI propio |
| Portabilidad / genericidad | 🟡 Media | PyYAML no declarado; valores y rutas de SecInterp hardcodeados en el “core genérico” |
| Submódulo | 🟢 Bueno | Limpio, fijado, con scripts de actualización/exportación y gate anti-`/home/` |

**Valoración global:** el framework está **bien diseñado** como arquitectura de agentes, pero sus dos mecanismos de fiabilidad a largo plazo —**memoria** y **métricas**— son precisamente los que están degradados. El mensaje “todo pasa” es engañoso: el validador ignora parte del sistema y la “verdad” contra la que valida está desactualizada.

---

## 1. Composición

### 1.1 Framework (`.agent/`)

| Elemento | Cantidad |
|---|---:|
| Skills genéricas | 9 |
| Workflows genéricos | 14 (+ `index.md`) |
| Herramientas Python | 6 (`forge.py`, `forge_paths.py`, `forge_metrics.py`, `validate_agent_system.py`, `memory_prune.py`, `lesson_extractor.py`) |
| Líneas de herramientas | 1.855 |
| Documentación Markdown | 3.155 líneas |
| Planes de arquitectura | 3 (`IMPROVEMENT_PLAN`, `GEN7`, `GEN8`) |
| Tests propios del framework | 0 |
| CI propio | 0 |

### 1.2 Estado del proyecto (`.agent-state/`)

| Elemento | Cantidad |
|---|---:|
| Skills overlay | 5 (`geological-logic`, `project-context`, `qgis-core`, `qgis-migration-4x`, `ui-framework`) |
| Workflows overlay | 4 (`audit-plugin`, `release-plugin`, `run-tests-in-qgis`, `smoke-qgis4`) |
| Lecciones | 98 |
| Entradas de historial | 49 (34 fechas distintas) |
| Snapshots de `next_steps` | 33 |
| Documentación Markdown | 9.353 líneas |

El pack QGIS de `.agent/scaffold/qgis/` y las copias de `.agent-state/skills|workflows` son **idénticas** hoy (`diff` limpio). No hay symlink ni sincronización automática: son copias.

---

## 2. Lo que funciona bien

- **Path model sólido:** `forge_paths.py` descubre `forge.toml` caminando hacia arriba y resuelve framework/estado sin rutas absolutas. Funciona desde cualquier cwd.
- **CLI único y coherente:** `forge.py validate|memory|lesson|metrics`; los workflows usan el CLI en lugar de scripts sueltos.
- **Validación de skills:** 14 skills verificadas (9 framework + 5 overlay), con frontmatter `name`/`description`, detección de nombres/descripciones duplicadas y conflictos. `validate --conflicts` → sin conflictos.
- **Diseño de workflows:** frontmatter `description`/`agent`/`skills`, stop conditions y validación en los workflows críticos; grafo de dependencias entre workflows.
- **Memoria episódica:** poda de snapshots `next_steps` > 90 días implementada y testeada.
- **Tests de integración:** 23 tests en `tests/agentic/` cubren el validador de conflictos, la poda de snapshots, el adaptador de métricas y la consistencia de issues.
- **Submódulo bien gestionado:** limpio, fijado a un commit, con `scripts/update_agentic_forge.sh` y `scripts/export_agentic_forge.sh`; este último bloquea fugas de rutas `/home/`.
- **Licencia MIT** compatible con el proyecto GPL y con el objetivo de reutilización.

---

## 3. Hallazgos críticos

### 3.1 La memoria está fuera de política y la poda de lecciones no puede funcionar

**Evidencia:**

- `AGENT_LESSONS.md` tiene **1.057 líneas** y **98 lecciones** ([`.agent-state/memory/AGENT_LESSONS.md`](../../.agent-state/memory/AGENT_LESSONS.md)).
- La política exige **< 350 líneas** de contenido activo ([`memory_policy.md:78`](../../.agent-state/memory/memory_policy.md#L78)).
- **0 lecciones** tienen el campo `consolidated_in`.
- `memory_prune.prune_lessons()` solo poda lecciones con `consolidated_in` y fecha > 90 días ([`memory_prune.py:72`](../../.agent/tools/memory_prune.py#L72)). Sin ese campo, **no poda ninguna**.
- 24 lecciones tienen fecha anterior al corte de 90 días (2026-07-20) y siguen activas.
- El test de poda solo cubre snapshots de `next_steps`, no lecciones ([`tests/agentic/test_memory_prune.py`](../../tests/agentic/test_memory_prune.py)).
- El pie del archivo dice **“Next review: 2026-07-27”** ([`AGENT_LESSONS.md:1057`](../../.agent-state/memory/AGENT_LESSONS.md#L1057)): la revisión está vencida hace casi tres meses.
- `start-session.md` ordena leer `AGENT_LESSONS.md` completo, mientras el mismo workflow pide “no precargar todas las skills para evitar token bloat”. Con 1.057 líneas, el propio sistema se contradice.

**Impacto:** el “cerebro” del agente crece sin control; las lecciones viejas no se consolidan en skills y el contexto de arranque se infla. La poda parece existir, pero es un no-op para lecciones.

**Recomendación:**

1. Consolidar las 24 lecciones > 90 días en las skills correspondientes y marcarlas `consolidated_in`.
2. Cambiar `prune_lessons()` para podar por antigüedad + consolidación, y añadir un modo `--dry-run`.
3. Añadir un test que verifique que una lección consolidada y vieja desaparece.
4. Convertir el límite de 350 líneas en un gate de `forge.py validate` (falla si se excede).
5. Actualizar la fecha de revisión y el pie del archivo.

### 3.2 El validador ignora los workflows del overlay

**Evidencia:**

- `validate_workflows()` recorre únicamente `WORKFLOW_DIR` = `.agent/workflows` ([`validate_agent_system.py:144-150`](../../.agent/tools/validate_agent_system.py#L144), [`forge_paths.py:53`](../../.agent/tools/forge_paths.py#L53)).
- Los 4 workflows de `.agent-state/workflows/` **nunca** se validan: `release-plugin`, `audit-plugin`, `run-tests-in-qgis`, `smoke-qgis4`.
- `forge.py validate` informa “Validated 14 skills, 14 workflows” y “All .agent/ files pass”; los workflows del proyecto no están incluidos en esa cuenta.
- `validate --graph` también usa solo el directorio del framework: reporta 14 workflows, marca como “unreferenced” las 5 skills del overlay y dice “Scripts: 13 (0 referenced, 13 unreferenced)”, lo cual es ruido: el grafo no ve los workflows QGIS que sí usan esas skills.
- Los workflows del overlay **sí tienen** frontmatter correcto hoy (verificado manualmente), pero nada impide que se rompan en el futuro sin que el gate lo detecte.

**Impacto:** el comando que el proyecto presenta como “auditoría del sistema agéntico” da luz verde sin revisar la mitad específica de QGIS, incluido el workflow de release.

**Recomendación:**

1. Generalizar `validate_workflows()` para recorrer `framework/workflows` + `state/workflows`.
2. Incluir ambos roots en el grafo y en `validate --conflicts`.
3. Añadir un test de regresión con un workflow overlay roto (skill inexistente) que deba fallar.
4. Corregir el mensaje final: “All agentic files pass” solo si ambos roots están limpios.

### 3.3 La “verdad” de las métricas está desactualizada y es semánticamente incorrecta

**Evidencia:**

| Campo | Valor actual | Problema |
|---|---|---|
| `summary.tests_ok` | **792** | Es el conteo estático de `def test_` en 5 categorías (23+301+40+352+76), **no** tests ejecutados. La ejecución local real es **743** |
| `tests_ok_note` | “615 = static count…” | Nota obsoleta: no coincide ni con 792 ni con 743 |
| `ground_truth_sources.tests_local` | “92 ran, 84 errors (QGIS env not available locally)”, 2026-05-24 | Registro de mayo; hoy la suite local pasa completa con mocks |
| `summary.total_issues` | **36** | El analizador vigente reporta **37**: falta `UNPRECISE_LAYER` |
| `issue_breakdown` | 20+9+4+2+1 = 36 | Omite `UNPRECISE_LAYER` (1), por eso cuadra artificialmente |
| `summary.total_sessions` | **18** | El historial tiene **49 entradas** y **34 fechas distintas** |
| `meta.last_updated_by` | “close-phase v3.7.0 metric reconciliation” | Procedencia obsoleta |
| `quality_score_latest_note` | “synced 2026-09-20” | El score es del análisis del 2026-10-18 |

`forge.py metrics validate` **pasa** porque compara los documentos contra `agent_metrics.json`, y `agent_metrics.json` contra sí mismo; no compara contra `analysis_results/project_context.json` ni verifica frescura. Es una validación de coherencia interna, no de verdad externa.

**Impacto:** los documentos, workflows y decisiones se calibran contra una fuente que ya no representa el estado real. Un “✅ All agentic files are metric-consistent” da falsa confianza.

**Recomendación:**

1. Separar `tests_static` (conteo de `def test_`) de `tests_executed` (resultado real de la suite).
2. Parsear **todos** los tipos de issue desde `project_context.json`; no depender de un bloque Markdown parcial.
3. Añadir una comprobación de frescura: si `analysis_results/project_context.json` es más nuevo que `agent_metrics.json`, fallar.
4. Recalcular `total_sessions` desde el historial (o renombrarlo a `sessions_with_scores`).
5. Actualizar `last_updated_by` y las notas de sincronización.

### 3.4 Los conteos de tests y los gates del release se contradicen

**Evidencia:**

| Fuente | Conteo |
|---|---:|
| `AGENTS.md:79` | 763 |
| `.agent-state/workflows/release-plugin.md:11` | 792 |
| `.agent-state/workflows/release-plugin.md:92` | 763 |
| `.agent-state/memory/agent_metrics.json` | 792 |
| Ejecución local real (`unittest discover tests`) | **743** |

Además, `release-plugin.md` exige “Docstring coverage < 100% → Block release” ([línea 7](../../.agent-state/workflows/release-plugin.md#L7)) y “100% docstring/return-type coverage” ([línea 29](../../.agent-state/workflows/release-plugin.md#L29)), mientras el analizador reporta **99,0 %** de docstrings. Si el gate se aplicara literalmente, v3.11.0 no habría podido publicarse; el release se publicó, así que el gate no se verificó de verdad.

**Impacto:** el workflow de release no es reproducible ni auditable; cada documento cita una cifra distinta.

**Recomendación:**

1. Eliminar los números manuales: generarlos desde un único comando y sustituirlos en los documentos.
2. Alinear el gate de docstrings con la métrica real (o medir solo API pública).
3. Hacer que `release-plugin` ejecute los mismos gates que CI y falle si no coinciden los conteos.

### 3.5 `task.md` está desactualizado y contradice `next_steps.md`

**Evidencia:**

- `task.md:189` sigue marcando como pendiente **“1.1 Implement a live symbology/legend styling preview”**, feature que v3.11.0 ya entregó.
- `task.md:222-232` (“Resume Point”) afirma que `main` está en **v3.9.1**, que v3.10.0 y v3.11.0 están **programadas**, y que queda resolver la **divergencia `legend_widget.py`**. La realidad: `main` está en **3.11.0**, ambas releases se publicaron y `legend_widget.py` fue eliminado.
- `next_steps.md` sí está actualizado a 2026-10-18.

**Impacto:** el tablero activo —que `start-session` lee como fuente de tareas— induce a un agente nuevo a trabajar sobre problemas ya resueltos o a reabrir una divergencia cerrada.

**Recomendación:**

1. Reescribir `task.md` desde `next_steps.md` y cerrar las tareas obsoletas.
2. Añadir una comprobación de coherencia: `task.md` no puede citar una versión anterior a `metadata.txt` ni un blocker marcado como resuelto en `next_steps.md`.
3. Archivar el histórico ya completado en `.agent-state/history/tasks/`.

### 3.6 Los workflows genéricos usan `pytest`; el proyecto usa `unittest`

**Evidencia:**

- `run-tests.md` propone `pytest` y `FORCE_MOCKS=0 pytest tests/integration` ([líneas 16 y 21](../../.agent/workflows/run-tests.md#L16)); luego admite “pytest o unittest” ([línea 32](../../.agent/workflows/run-tests.md#L32)).
- `start-session.md:91` y `close-session.md:54` usan `pytest` como opción local.
- El estándar del proyecto es **unittest mock-first** (`AGENTS.md`, `pyproject.toml`, CI y `tests/base_test.py`).

**Impacto:** un agente que siga el workflow al pie de la letra ejecuta un comando que no es el del proyecto y puede obtener resultados distintos o fallos por discovery.

**Recomendación:**

1. Parametrizar el comando de test en `forge.toml` (`test_command = "..."`) y que los workflows lo referencien.
2. Mover las particularidades de QGIS/unittest al workflow overlay del proyecto.
3. Actualizar `run-tests.md`, `start-session.md` y `close-session.md`.

---

## 4. Hallazgos secundarios

### 4.1 El framework no aplica su propio estándar de calidad

- `ruff` sobre `.agent/tools/` (con configuración aislada) reporta **21 errores**: `F402`, `F541`, `E501`, `I001`, `F401`, `SIM103`, `B007`, `UP045`.
- **4 de 6** archivos no están formateados (`ruff format --check`).
- `validate_agent_system.py` tiene imports duplicados (`dataclass` y `dc`, `field` y `dc_field`) y variables de loop que sombrean imports.
- El `ruff` del proyecto **excluye `.agent`**, así que nada de esto se ve en el gate normal.
- El framework **no tiene CI ni tests propios**; sus 23 tests viven en el proyecto consumidor (`tests/agentic/`), y no cubren `prune_lessons`, el CLI ni `forge_paths`.

**Recomendación:** añadir un `ruff`/`format --check` para `.agent` en `make`/CI y un pequeño job de tests del framework; o un `pyproject.toml` propio en el repo del framework.

### 4.2 “Genérico” solo a medias: quedan valores de SecInterp hardcodeados

- `forge_metrics.py` incluye `STALE_MAPPINGS = {"test_count": {535: 620, 572: 620}, "quality_score": {40.8: 52.3, 41.7: 52.3}}` ([línea 310](../../.agent/tools/forge_metrics.py#L310)) y marcadores de versiones `v3.6.0`, `v3.5.0`, etc. ([línea 317](../../.agent/tools/forge_metrics.py#L317)).
- `lesson_extractor.py` contiene patrones para `qgis-analyzer`, `scripts/sync_metrics.py` y números históricos concretos ([líneas 36-37](../../.agent/tools/lesson_extractor.py#L36)).
- `forge_metrics.py` usa el campo `i18n_issues_qgis_analyzer`, específico de QGIS.

Esto contradice el objetivo declarado de “generic core” y explica por qué el framework solo funciona bien con este proyecto.

**Recomendación:** mover esos mapeos y patrones a configuración del proyecto (`forge.toml` o un adapter), y dejar en el core solo mecanismos genéricos.

### 4.3 Dependencias no declaradas

- `memory_prune.py` importa **PyYAML** ([línea 12](../../.agent/tools/memory_prune.py#L12)).
- El framework **no tiene `pyproject.toml` ni `requirements.txt`**; PyYAML funciona aquí solo porque llega de forma transitiva (pre-commit/detect-secrets).
- `forge_paths.py` usa `tomllib`, que requiere **Python ≥ 3.11**; el README no declara versión mínima.

**Recomendación:** declarar `PyYAML` y `python >= 3.11` en el repo del framework; añadir un mensaje claro si falta la dependencia.

### 4.4 Duplicación `scaffold/qgis` ↔ `.agent-state` sin sincronización

- Las copias son idénticas hoy, pero son **archivos independientes**.
- `scripts/update_agentic_forge.sh` solo actualiza el submódulo y ejecuta `forge validate` + `sync_metrics --validate` ([líneas 49-50](../../scripts/update_agentic_forge.sh#L49)); **no copia** `scaffold/qgis` a `.agent-state`.
- Si el framework actualiza una skill QGIS, el proyecto seguirá usando la copia vieja sin aviso.

**Recomendación:** decidir el modelo: symlink, script de sincronización explícito con `--check`, o declarar `.agent-state` como dueño y `scaffold` como referencia. Añadir un test de drift.

### 4.5 El gate de `pre-push` no es reproducible

- `.agent/README.md:17` afirma que un hook `pre-push` impone complejidad y estilo.
- El hook existe **solo en `.git/hooks/pre-push` local**, no está versionado, no hay instalador y el CI no ejecuta `qgis-analyzer --max-cc 10`.
- `AGENT_LESSONS.md:664` ya documenta la lección “Untracked git hooks drift when a CLI flag contract changes”; el framework conoce el riesgo y aun así lo presenta como característica.

**Recomendación:** versionar el hook (o un `make install-hooks`), añadir el gate de CC al CI y quitar la afirmación absoluta del README.

### 4.6 Deriva documental menor

- `memory_policy.md` referencia `scripts/memory_prune.py` ([líneas 79 y 123](../../.agent-state/memory/memory_policy.md#L79)), ruta que ya no existe; ahora es `.agent/tools/memory_prune.py` / `forge.py memory prune`.
- `IMPROVEMENT_PLAN.md` se basa en `check_cc.py` y `verify_i18n_hygiene.py` ([líneas 4, 14-15](../../.agent/architecture/IMPROVEMENT_PLAN.md#L4)), ambos eliminados.
- `IMPROVEMENT_PLAN_GEN7.md` sigue marcado “not yet scheduled” aunque GEN8 lo reemplazó.
- `audit-plugin.md` dice “qgis-plugin-analyzer v1.9.0+” cuando el proyecto usa 1.16.0.
- El `AGENTS.md` raíz lista 16 comandos; omite `/release-package` y `/audit-package` del core (posible sustitución deliberada por los QGIS, pero no está explicado).
- Las dos únicas “referencias rotas” detectadas en Markdown son plantillas ilustrativas (`relative/path`, `session_YYYY-MM-DD_topic.md`), no enlaces reales.

### 4.7 Endurecimiento menor

- `lesson_extractor.py` pasa el valor de `--since` directamente a `git diff` sin separador `--`; un valor que empiece por `--` podría interpretarse como opción de git. Riesgo bajo (herramienta local, no input no confiable), pero conviene validarlo.

---

## 5. Plan priorizado

### P0 — recuperar la fiabilidad del sistema

1. **Memoria:** consolidar las 24 lecciones > 90 días, marcar `consolidated_in`, arreglar `prune_lessons()` y añadir el gate de 350 líneas.
2. **Métricas:** separar tests estáticos/ejecutados, parsear todos los issue types, recalcular `total_sessions` y añadir chequeo de frescura contra `analysis_results/`.
3. **`task.md`:** reescribirlo desde `next_steps.md`; cerrar 1.1, la divergencia `legend_widget` y las releases ya publicadas.
4. **Release:** eliminar los conteos contradictorios (763/792/743) y alinear el gate de docstrings con la métrica real.

### P1 — cerrar los puntos ciegos

5. **Validador:** incluir `.agent-state/workflows` en `validate`, `--graph` y `--conflicts`; añadir test de workflow overlay roto.
6. **Workflows:** parametrizar el comando de test y dejar de asumir `pytest`.
7. **Calidad del framework:** `ruff`/`format --check` para `.agent` y job de tests del framework.
8. **Dependencias:** declarar PyYAML y Python ≥ 3.11.

### P2 — limpieza y portabilidad

9. Mover los valores de SecInterp de `forge_metrics.py`/`lesson_extractor.py` a configuración del proyecto.
10. Resolver la duplicación `scaffold/qgis` ↔ `.agent-state` con un mecanismo de sincronización verificable.
11. Versionar el hook `pre-push` o mover el gate de CC al CI.
12. Corregir la deriva documental (`memory_policy`, `IMPROVEMENT_PLAN`, `audit-plugin`, `AGENTS.md` raíz).
13. Etiquetar el commit actual del submódulo (`v1.2.1`) o documentar que se sigue `main`.

---

## 6. Conclusión

`.agent` es un framework **bien pensado**: separa framework y estado, carga skills bajo demanda, tiene CLI, validador, grafo, métricas y memoria episódica. El problema no es la arquitectura, sino la **operación**: la memoria creció 3× por encima de su propia política y su poda de lecciones es inoperante; las métricas contra las que se valida todo están desfasadas y cuentan cosas distintas de las que dicen contar; y el validador da luz verde sin mirar los workflows QGIS del overlay.

La buena noticia es que casi todo se corrige sin rediseñar: consolidar lecciones, arreglar el parser de issues, ampliar el validador a ambos roots y reescribir `task.md`. Con esas cuatro acciones, el sistema vuelve a ser confiable para las siguientes sesiones.
