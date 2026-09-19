# Informe de Fase — SecInterp v3.8.0

**Fecha:** 2026-09-19
**Versión actual publicada:** v3.7.2 (plugin portal + GitHub)
**Rama de trabajo:** `refactor/core-gui-decoupling` (34 commits por delante de `main`)
**Responsable:** jmbernales

---

## 1. Resumen ejecutivo

La fase v3.8.0 tuvo dos ejes: (1) la modernización del sistema agéntico/herramientas
y el cierre de la compatibilidad Qt6/QGIS 4, y (2) el **refactor estructural Core/GUI**
(patrón Extract-then-Compute) que es el entregable central de la fase.

Resultado principal: el núcleo `core/` pasó de **36 a 6 archivos** con acoplamiento
directo a QGIS, todos los servicios de negocio migrados a un núcleo 100% agnóstico y
una nueva capa de adapters (`gui/adapters/`) que concentra la interacción QGIS.

---

## 2. Cronología de la fase

| Fecha | Hito |
|---|---|
| 2026-09-12 | Cierre fase v3.7.0 (i18n gate, UX, enums Qt6) + hardening agéntico |
| 2026-09-12 | Release **v3.7.2** — parche de compatibilidad Qt6/QGIS 4 (114 enums scoped) |
| 2026-09-13 | Evolución del sistema agéntico **Gen 8** (fases A–E) + limpieza del root |
| 2026-09-14 | Actualización `qgis-plugin-analyzer` 1.14.0 |
| 2026-09-17 | Upstreaming de scripts propios → analyzer (retiro de `check_cc`/`verify_i18n`) |
| 2026-09-19 | **Refactor Core/GUI Decoupling** (Fases 0–5 completadas) |

---

## 3. Refactor Core/GUI (entregable central)

### 3.1 Patrón aplicado

**Extract-then-Compute**: la GUI extrae datos de QGIS y los convierte a DTOs/primitivas;
`core/` procesa con matemática pura (stdlib) y es testeable sin QGIS.

### 3.2 Servicios migrados

| Commit | Servicio/Capa | Resultado |
|---|---|---|
| `e00419d5` | `export_service` | desacoplado de `QgsProject.instance()` |
| `49de4b03` | `StructureService` | puro + `StructureExtractor` |
| `4b4a129a` | `GeologyService` | puro (`build_segments`) + `GeologyExtractor` |
| `5d47fe9f` | `ProfileService` | eliminado (100% Extract) → `ProfileExtractor` |
| `69e8a84f` | dominio `drillhole` | puro (`process_context`) + `DrillholeExtractor` |
| `9b1bcee9` | capa de validación | DTO `LayerMetadata` + `ValidationExtractor` |

### 3.3 Adapters creados (`gui/adapters/`)

`layer_resolver`, `feature_fetcher`, `geometry`, `structure_extractor`,
`geology_extractor`, `profile_extractor`, `drillhole_extractor`, `validation_extractor`.

### 3.4 DTOs nuevos

`GeologyContext`, `OutcropSegments`, `DrillholeContext`, `LayerMetadata`.

### 3.5 Archivos eliminados

`profile_service.py`, `profile_interface.py`, `drillhole_orchestrator.py`,
`geology/outcrop_processor.py`, `geology/profile_sampler.py`, `utils/geometry.py`,
`utils/geometry_utils/{extraction,filtering}.py`, `utils/qt6_compat.py`,
`utils/resource_manager.py`, `gui/lod_calculator.py`.

### 3.6 Bugs corregidos (pruebas manuales QGIS 4.x)

- `0bc44e92` — `QEvent.Resize` → `QEvent.Type.Resize` (`legend_widget.py`).
- `4671ac6` — exportación 3D habilitada por defecto (`AccessControlService`).

---

## 4. Herramientas y sistema agéntico

- **Gen 8**: root `AGENTS.md` como SSoT, subagentes nativos (`architect`/`qa_engineer`/`auditor`),
  skills registrados vía `skills.paths`, scripts consolidados (`scripts/` 27 → 15).
- **qgis-plugin-analyzer 1.14.0**: regla `MISSING_I18N` AST + gate `--max-cc` nativos.
- **Upstreaming**: retirados `check_cc.py`, `verify_i18n_hygiene.py` (absorbidos por el analyzer).
- **Limpieza root**: ~90 MB de artefactos eliminados.

---

## 5. Métricas de cierre

| Métrica | Valor |
|---|---|
| Tests (unittest) | 558/558 OK |
| `ruff check .` | PASS |
| Gate de arquitectura | 3/3 OK |
| Allowlist `core/` | **6** (inicial 36) |
| Compatibilidad QGIS 4 / Qt6 | `qgisMaximumVersion=4.99`, 0 enums planos, `qt6-check` en CI |
| Releases publicados | v3.7.0, v3.7.1, v3.7.2 |

---

## 6. Deuda restante

### 6.1 Áreas grises (6 archivos acoplados a QGIS — integración genuina)

| Archivo | Acoplamiento | Abordaje propuesto |
|---|---|---|
| `utils/i18n.py` | `QCoreApplication` (`TranslatableMixin`) | aceptar como shim o mecanismo `tr()` inyectable |
| `config.py` | `QgsSettings` | `SettingsStore` inyectable |
| `data_cache.py` | `qgis.PyQt` (tr) | ídem i18n |
| `services/access_control_service.py` | `QgsSettings` | `SettingsStore` inyectable |
| `services/export_service.py` | `QgsMapSettings`/`QgsRectangle` | mover render a GUI/adapter |
| `utils/io.py` | `QgsVectorFileWriter` | abstracción de escritor de vectores |

### 6.2 Deuda técnica (analyzer)

- `module_size_gate` FAIL: 7 módulos > 400 líneas (`sec_interp_plugin.py`,
  `dialog_preview_manager.py`, `dialog_settings_persistence.py`, `main_dialog.py`,
  `dialog_interpretation_manager.py`, `measure_tool.py`, `settings_page.py`).
- 2 `NON_PYTHONIC_LOOP`.
- 1 `SPATIAL_INDEX` en `dialog_interpretation_manager.py`.

### 6.3 Metas v3.8.0 no iniciadas

- **Goal 1 — 3D/Simbología**: live symbology preview, `VerticalExaggerationService`,
  toggle Auto/Manual, integración render, tests de proyección cartesiana.
- **Goal 2 — Deuda**: `NON_PYTHONIC_LOOP`, `SPATIAL_INDEX`, `module_size_gate`
  (retiro de `qt6_compat` ya ✅).

---

## 7. Recomendaciones

1. **Mergear** `refactor/core-gui-decoupling` → `main` (`git merge --ff-only`) tras
   validar `make docker-test` y `make qt6-check`.
2. **Documentar las 6 áreas grises como deuda aceptada** — no forzar el patrón
   Extract-then-Compute en integración QGIS genuina (`tr()`, `QgsSettings`, I/O de vectores).
3. **Release v3.8.0** tras el merge para capitalizar el refactor (ciclo cerrado).
4. **Priorizar Goal 1** (adaptive vertical exaggeration + symbology preview) en la
   siguiente fase, dado que son las features diferenciales pendientes.
5. **Atacar `module_size_gate`** en paralelo (refactorizar los 7 módulos > 400 líneas)
   como deuda técnica de bajo riesgo y alto valor de mantenibilidad.

---

**Filosofía**: una fase no termina cuando el código funciona, sino cuando el
conocimiento queda documentado y la visión del siguiente ciclo es clara.
