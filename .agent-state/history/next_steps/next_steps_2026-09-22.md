# Next Steps (Updated 2026-09-22)

## 🚧 Session 2026-09-22 — Code Walkthrough Vault v2 (EN PROGRESO)

**Handover de la bóveda v2** (docs-only; sin cambios en Python):

- **Qué se hizo**: nueva bóveda completa bilingüe v2 (`docs/code_walkthrough_v2/` ES +
  `docs/code_walkthrough_en_v2/` EN); la v1 queda intacta.
  - Tooling: `scripts/generate_vault_v2.py` (AST, tiering A/B/C, slugs sin colisión,
    enumeración de archivos de paquete, `HIGH_IMPORTANCE` → `note_lines: 700`),
    `scripts/check_notes.py` (gate 400–500, mínimos por tier A/C=400 B=300, tope 700,
    placeholders, paridad ES↔EN). `check_docs.py` + `sync_vault_mirrors.sh` actualizados.
  - `docs/structure/project_structure_table.md` (vista tabular Depth 1–5).
- **Estado**: 56 esqueletos de Core generados; **7 notas Core enriquecidas** (controller,
  drillhole, path_resolver, core_interfaces, dtos, entities, exceptions).
- **Cómo reanudar**: `uv run python scripts/generate_vault_v2.py --layer <capa> --write`
  para generar esqueletos; enriquecer cada nota leyendo el fuente hasta 400–500 líneas;
  validar con `uv run python scripts/check_notes.py` (y `--strict` al finalizar).
- **Convenciones clave**: notas de paquete → tabla `Archivos del paquete` con self-anchors
  `[[#Sección\|archivo.py]]`; archivos con nota individual se enlazan en `layer_*`; tope
  500 por defecto, `note_lines` (máx 700) solo para la lista `HIGH_IMPORTANCE`.

### Pendiente bóveda v2
- [ ] Enriquecer ~49 esqueletos de Core restantes (validation, services, utils, models, domain/__init__+task_inputs, grupo core_domain).
- [ ] Fase 2 GUI (adapters, renderers, tasks, tools, ui/, managers, preview_*).
- [ ] Fase 3 Exporters/Plugin/Raíz.
- [ ] Fase 4 `layer_*` notes + `Index.md` final + espejos re-sync.
- [ ] Referencia: `docs/maintenance/session_2026-09-22_code_walkthrough_v2.md`.

## ✅ Session 2026-09-21 — Adaptive Vertical Exaggeration + Preview fixes (COMPLETADO)

- Adaptive VE end-to-end (Goal 1.2), VE visible, fix scratch layers. 643 tests.
- Referencia: `docs/maintenance/session_2026-09-21_adaptive_ve_and_preview_fixes.md`.

## 🎯 Goals pendientes (post v3.8.0)

### Goal 1: 3D Interpretation & Symbology Enhancements
- [ ] **1.1** Live symbology/legend styling preview bajo el sidebar de Settings.
- [x] **1.2** Adaptive VE — COMPLETO 2026-09-21 ✅
- [ ] **1.5** Expandir tests de integración de proyección vertical cartesiana.

## 🧾 Deuda restante (documentada, no bloqueante)

- **6 áreas grises** (integración QGIS genuina): `i18n.py`, `config.py`, `data_cache.py`,
  `access_control_service.py`, `export/map_settings_factory.py`, `export/orchestrator.py`, `io.py`.
- **Analyzer**: 0 issues.
- **Docs i18n opcional**: traducir `USER_GUIDE` fr (28%) / de (18%); `make docs` para publicar.

## 🚀 How to Resume
1. Run `/start-session`.
2. Continuar **bóveda v2** (enriquecer Core restante) o **Goal 1.1** (symbology preview).
