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
- **Estado**: Bóveda v2 **COMPLETA y commiteada** — Core 56/56 + GUI 73/73 + Fase 3 22/22 +
  Fase 4 (23 hubs `layer_*` + Index final ES/EN) + mapa archivo→nota
  (`project_structure_links.md`, 178 ficheros → 151 notas, script regenerable).
  `check_notes.py --strict` PASS (302 notas, 0 placeholders, 0 enlaces rotos).
  Commits: `1d4af77d` `d5e8a82b` `b7d221f7` `dab9d27e` `26ada077` (+ cierre).
  Tooling: `resolve_group_slugs` + 23 hubs + `project_structure_links` en SKIP_STEMS.
- **Cómo reanudar**: `uv run python scripts/generate_vault_v2.py --layer <capa> --write`
  para generar esqueletos; enriquecer cada nota leyendo el fuente hasta 400–500 líneas;
  validar con `uv run python scripts/check_notes.py` (y `--strict` al finalizar).
- **Convenciones clave**: notas de paquete → tabla `Archivos del paquete` con self-anchors
  `[[#Sección\|archivo.py]]`; archivos con nota individual se enlazan en `layer_*`; tope
  500 por defecto, `note_lines` (máx 700) solo para la lista `HIGH_IMPORTANCE`.

### Pendiente bóveda v2
- [x] Enriquecer ~49 esqueletos de Core restantes — COMPLETO ✅ (49/49, `check_notes.py --strict` PASS).
- [x] Fase 2 GUI — COMPLETO ✅ (73/73: 63 individuales + 10 grupos, `check_notes.py --strict` PASS).
- [x] Fase 3 Exporters/Plugin/Raíz — COMPLETO ✅ (22/22: 19 individuales + 3 grupos, `--strict` PASS).
- [x] Fase 4 `layer_*` + Index final — COMPLETO ✅ (23 hubs + Index ES/EN, 0 enlaces rotos, `--strict` PASS).
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
- **QA MCP QGIS 4 (exploración)**: propuesta de un MCP de QA acotado para automatizar el
  smoke en QGIS 4 → `docs/plans/exploration_qgis4_qa_mcp.md` (no implementado; opción B).

## 🚀 How to Resume
1. Run `/start-session`.
2. Implementar `docs/plans/implementation_plan_dem_section_v3.9.0.md` en build mode
   (Fase 0 gating → Fase 1 → 2 → 3; decisión abierta #1: OK en S1 vs S2).
   Después: Goal 1.1 (symbology preview) o 1.5 (tests proyección).
