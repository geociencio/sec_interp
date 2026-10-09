# Next Steps (Updated 2026-10-08)

## ✅ Session 2026-10-08 — Unify Agentic Systems on agentic-forge (COMPLETADO)

- **Qué se hizo**: se unificaron los sistemas agénticos de los tres proyectos hermanos
  (`qgis-plugin-analyzer`, `ai-context-core`, `qgis-plugin-manager`) sobre **`agentic-forge`**
  `v1.2.0` (Codeberg). Sin cambios en el código de SecInterp; fue una sesión de coordinación
  entre repos. Plan: `docs/plans/implementation_plan_unify_agentic_systems.md`.
  - **Upstream (agentic-forge)**: núcleo genericizado (9 skills + 14 workflows), dominio QGIS a
    `scaffold/qgis/`, añadidas `testing-standards` + `release-package`/`audit-package`, tag `v1.2.0`.
  - **analyzer** / **ai-context-core** / **manager**: submódulo `.agent/` + `forge.toml` +
    `.agent-state/` + overlay skills; limpieza de sistemas legacy (`.ai-context/`, `skill_sync.py`).
- **Commits**: `agentic-forge` `2de22cf` · analyzer `4b10b11`+`fb080db` · ai-context-core `fb70feb`
  · manager `73586a2` (todos pusheados).
- **Calidad**: `forge validate` verde en los tres; `pytest` 126 / 299 / 190 OK.
- **Referencia**: `docs/maintenance/session_2026-10-08_unify_agentic_systems.md`.
- **Pendiente / cómo reanudar**:
  1. Gate cross-repo que confirme que los tres pinnean la misma versión del framework.
  2. Promover `geological-logic` a `scaffold/geology` en agentic-forge.
  3. Los pendientes propios de SecInterp (tren v3.10.0/v3.11.0, `legend_widget.py`, bóveda)
     siguen abajo sin cambios.

## ✅ Session 2026-10-04 — Offline Help (User Guide only) + graphify (COMPLETADO)

- **Qué se hizo**: el botón **Help** del plugin ahora muestra un manual offline con **solo la
  User Guide** (navegación limpia, sin enlaces muertos) en 14 idiomas, **sin tocar el código del
  plugin** y **sin afectar al sitio publicado**. Se evaluó **graphify** (grafo de código local,
  ignorado en git).
  - **Help**: `docs/source/help_index.rst` (master doc solo `USER_GUIDE`); `conf.py` excluye el
    resto de docs con `SECINTERP_DOCS_HELP=1` y oculta `help_index.rst` del build web;
    `build_docs.sh` separa builds **web**/**help** (`root_doc=help_index`) y renombra
    `help_index.html` → `index.html` (parcheando enlaces) para no tocar `open_help()`.
  - **Higiene**: `.gitignore` ignora `graphify-out/`.
  - **graphify** (dev): 192 ficheros / 2929 nodos / 5216 aristas; `benchmark` 13.7× menos tokens.
- **Commits**: `92e5eabd`, `81d1f39d`.
- **Calidad**: ruff/format limpios · pre-commit PASS · `unittest discover tests` **714 OK** ·
  build help 14 locales verificado (`index.html` + `USER_GUIDE.html`) · build web intacto.
- **Referencia**: `docs/maintenance/session_2026-10-04_help_userguide_only.md`.
- **Pendiente / cómo reanudar**:
  1. **Opcional**: `make docs-i18n-update` para traducir el título “SecInterp Help”. Para añadir
     una página al manual offline, listarla en `help_index.rst`.
  2. El resto de pendientes (tren v3.10.0/v3.11.0, `legend_widget.py`, bóveda, Goal 1.1/1.5)
     siguen abajo sin cambios.

## ✅ Session 2026-10-04 — Agentic Forge Extraction (F1–F5) (COMPLETADO)

- **Qué se hizo**: se extrajo el framework agéntico reutilizable (skills/workflows/tooling) del
  estado del proyecto y se publicó en **Codeberg** como **`agentic-forge`** (MIT), consumido
  como **submódulo** en `.agent/`. Plan: `docs/plans/implementation_plan_agentic_forge_extraction.md`.
  - **F1**: estado → `.agent-state/` + `forge.toml` + `scripts/forge_paths.py` (tooling path-aware).
  - **F2**: overlay de skills de proyecto; docs genéricos; **MIT**; `export_agentic_forge.sh`;
    publicado en Codeberg (export sin historial, público).
  - **F3**: `.agent/` → submódulo; CI con `submodules: recursive`.
  - **F4**: gobernanza — tag `v1.0.0`, `update_agentic_forge.sh`, guía de sync reescrita.
  - **F5**: CLI `forge` + tools genéricos en `.agent/tools/`; `sync_metrics` partido en core
    genérico (`forge_metrics.py`) + colector de proyecto; umbrales a `forge.toml`.
  - **Fix**: `AGENTS.md` del framework (era un puntero roto) → config propia.
- **Commits**: `be5baa9f`, `a0241127`, `1a0290e4`, `a5a6a281`, `43a4aa64`, `2e7940c7`, `3ee51a5c`.
- **Framework**: https://codeberg.org/geociencio/agentic-forge (`main` `a77548b`, tags `v1.0.0`/`v1.1.0`).
- **Calidad**: Docker verde (23/237/40/323/76) · `forge validate` · `sync_metrics --validate` ·
  `check_docs` · pre-commit.
- **Pendiente / cómo reanudar**:
  1. **Codeberg**: poner **description + topics** al repo `agentic-forge` (UI).
  2. **Opcional**: genericizar menciones residuales a `SecInterp` en skills; promover
     `geological-logic` a `scaffold/geology`.
  3. **Plugin (sin cambios)**: `legend_widget.py` (divergencia al mergear el tren), bóveda
     v3.11.0 y deuda funcional (Goal 1.1/1.5, selector multi-línea).

## ✅ Session 2026-10-04 — v3.9.1 Released · Docs/Vault v2-First · ZIP & CI Fixes (COMPLETADO)

- **Qué se hizo**: se publicó **v3.9.1** y se cerró una sesión de saneamiento de docs, release
  y empaquetado.
  - **v3.9.1 publicado**: el cron de las 15:00 UTC **no disparó** (tampoco lo había hecho nunca);
    se publicó por **`workflow_dispatch`** (tag + GitHub release + ZIP). Merge
    `release/v3.9.1 → main` (`11806511`): `main` ya tiene el **perfil suavizado**.
  - **Docs v2-first**: `README` + `ARCHITECTURE_EN` / `MONOLITHIC_VS_CLEAN` / `PLUGIN_REPORT`
    actualizados a **v3.9.1** (módulos 177, tests 745→**763** tras el merge, features v3.9);
    **v1 congelado** (excluido de `sync_vault_mirrors.sh`); espejos v2 regenerados; bóveda a
    v3.9.1 (footers 356 notas + Index) y structure docs con `vertical_exaggeration_service` /
    `crs_plausibility`.
  - **Quick wins `.agent/`**: `black`→`ruff format`, refs fantasma
    (`prune_consolidated.py`, `COMMIT_GUIDELINES`), conteos (745/763, 15 workflows), Gen 8
    marcado implementado, `qgis-migration-4x` referenciado, contador del validador.
  - **Versión**: `metadata.txt`/`pyproject.toml` → **3.9.1**; `make docs-version` (7 docs);
    CHANGELOG [3.9.1].
  - **Ayuda/ZIP**: el CI empaquetaba **sin `help/`** (0.4 vs 3.9 MiB). Arreglado el workflow
    (`mkdir -p help` + build de docs) y `build_docs.sh`. **Optimización**: dedup de `_static`
    (22 assets) + PNG lossless (`pyoxipng`) → ayuda 8.5→**3.7 MiB**; ZIP 3.76→**2.38 MiB**.
    Excluido `.release-queue.json` del paquete. Asset del release v3.9.1 **reemplazado**.
- **Commits**: `314a4f34`, `654ead62`, `cd6838ab`, `11806511`, `3c31e322`, `fb7918e5`,
  `48a73ca6`, `b7c52db3`.
- **Calidad**: suite Docker verde (23/237/40/323/76) · ruff PASS · gates docs/vault/agentes PASS ·
  analyzer 0 issues.
- **Pendiente / cómo reanudar**:
  1. **Portal QGIS**: ~~subir `dist/sec_interp.3.9.1.zip`~~ ✅ **HECHO** — v3.9.1
     (2.38 MiB, con ayuda en 14 idiomas) ya está en el repositorio de plugins de QGIS.
  2. **Tren**: v3.10.0 (11 oct) / v3.11.0 (18 oct) publican solos; el workflow ahora usa el
     `build_docs.sh` optimizado de `main` → incluirán la ayuda optimizada. Verificar cada uno.
  3. **⚠️ Divergencia `legend_widget.py`**: las ramas del tren **eliminaron**
     `gui/legend_widget.py` (commit `1d82db0f`, panel lateral de leyenda); `main` lo
     **conserva**. Al mergear el tren en `main` (v3.11.0): eliminar las refs a
     `legend_widget.py` en `docs/ARCHITECTURE_EN.md`, `docs/structure/project_structure*.md`
     y resolver el conflicto (por esto el backport directo a las ramas quedó bloqueado por el
     doc-gate).
  4. **Bóveda completa v3.11.0**: refresco completo cuando `main` consolide el tren.
  5. **Deuda funcional**: Goal 1.1 Fase 4 (presets), selector multi-línea, Goal 1.5.

## ✅ Session 2026-09-27 — Release Train, CI Hardening & Vault Refresh (COMPLETADO)

- **Qué se hizo**: se liberó **v3.9.0** y se preparó el **tren incremental** v3.9.1 /
  v3.10.0 / v3.11.0 con publicación **programada** (domingos 4 / 11 / 18 oct). Se reparó el
  **CI** (llevaba rojo en cada push) y se refrescó la **bóveda v2** a v3.9.0.
  - **v3.9.0**: merge boundary `76908843` en `main`, versión, CHANGELOG, notas de release,
    dev-log; **bug bloqueante** de aislamiento de mocks en `tests/gui` corregido; gates
    (696 locales / 681 Docker, analyzer 0, security PASS); ZIP auditado; tag + **GitHub
    release publicado**. Commits `e00604e`, `664d775`. **Portal: manual, omitido por decisión.**
  - **Tren v3.9.1/3.10.0/3.11.0**: ramas `release/v3.9.1|v3.10.0|v3.11.0` (acumulativas) con
    merge + versión + notas (714 / 729 / 743 tests). Workflow programado
    `.github/workflows/scheduled-release.yml` + `.release-queue.json`; validado con
    `dry_run` de v3.9.1 (checkout + Docker tests + build, sin publicar).
  - **CI**: lint fijado al ruff del lock (`ISC004`/`PLR0917` de ruff 0.16); detección real
    de hallazgos Qt6; job de tests migrado al **Docker** del proyecto; deploy de docs
    omitido si falta `DOCS_DEPLOY_TOKEN`; eliminado `release.yml` legado. `main` **en verde**.
  - **Qt6/QGIS4**: `QgsRasterBandStats.All` → `.Stats.All` y `Qgis.RasterBandStatistic.All`
    (con fallback 3.28–3.39) en `dem_page.py`; aplicado a `main` + las 3 ramas.
  - **Bóveda v2 → v3.9.0**: notas `preview_param_hasher`/`ui_status_manager` a tier A,
    nuevas `crs_plausibility`/`layer_metadata`/`topo_renderer`, footers a v3.9.0 (346),
    Index/hubs/mapa actualizados. `check_notes --strict` PASS (308).
- **Referencia**: `docs/maintenance/session_2026-09-27_release_train_and_vault_refresh.md`.
- **Pendiente / cómo reanudar**:
  1. **Portal QGIS**: ~~subir el ZIP del release que se publique (v3.9.1 el 4 oct)~~ ✅
     **HECHO** — v3.9.1 ya está en el repositorio de plugins de QGIS.
  2. **v3.9.0**: no se sube al portal (decisión); v3.9.1+ ya traen los fixes de Qt6.
  3. **Tren**: los domingos 4/11/18 oct el workflow publica solo; sincronizar `main`
     manualmente al final (`git merge --ff-only release/v3.11.0`).
  4. **Bóveda completa v3.11.0**: refresco completo cuando `main` consolide el tren.
  5. **Deuda funcional**: Goal 1.1 Fase 4 (presets), selector multi-línea, Goal 1.5.

## ✅ Session 2026-09-23 — Optional Smoothed Topography Profile (COMPLETADO)

- **Qué se hizo**: perfil suavizado opcional — checkbox **Smooth** + ventana (m)
  en Controls que superpone una línea roja suave y exporta `*_smoothed.csv` +
  `profile_line_smoothed.<ext>`; filtro de media móvil por distancia (core, puro).
- **Commits**: `3094a1f1`, `76fc6206`.
- **Calidad**: suite verde · ruff/format limpios · analyzer 0 issues · gates
  CC/Module Size/i18n PASS · smoke QGIS 4 OK.
- **Referencia**: `docs/maintenance/session_2026-09-23_smoothed_profile.md`.
- **Sin bugs abiertos**. Diferidos: remuestreo bilineal, Savitzky-Golay,
  selector multi-línea, editor por unidad (Goal 1.1), leyenda.

## ✅ Session 2026-09-23 — DEM/Section v3.9.0 Phases (1.5, 1.6, 2, 3) (COMPLETADO)

- **Qué se hizo**: se completó el plan v3.9.0 — resolver central de la sección
  (Fase 1.5, neutro), stats de banda del DEM + combo ancho/unidades abreviadas
  (Fase 1.6), modo de color del perfil gradiente/simple (Fase 2) y stats
  perfil-vs-DEM (Fase 3).
- **Commits**: `2a14767b`, `2352f031`, `008b18ad`, `b978e4ee`, `6d342189` (5) +
  cierre.
- **Calidad**: suite verde · ruff/format limpios · analyzer 0 issues · smoke QGIS 4
  OK (stats DEM, colores, stats de perfil, export).
- **Referencia**: `docs/maintenance/session_2026-09-23_dem_section_v390_phases.md`.
- **Sin bugs abiertos**. Queda deuda: **selector multi-línea** (infra lista),
  remuestreo bilineal, editor por unidad (Goal 1.1), leyenda, y reimportar el CSV
  de geología como UTF-8.

## ✅ Session 2026-09-23 — CRS Sampling Hardening + Structure/Section Fixes (COMPLETADO)

- **Qué se hizo**: se corrigió un cuelgue del sistema al muestrear un DEM
  geográfico (EPSG:4326, mal nombrado `..._3857.tif`) con línea proyectada
  (32614, OTF). También elevaciones 0 en estructuras/collares por CRS, se añadió
  detección **bloqueante** de CRS mal etiquetado, y se arreglaron los combos de
  campo estructurales. Se commitó el gating S0/S1/S2 previo.
- **Commits**: `baf11d8c`, `98758e92`, `02d9cd65`, `1e44c658`, `ef88acf7`,
  `eb9ffa20` (6).
- **Calidad**: suite verde (unittest discover 666; tooling ground truth 715) ·
  ruff/format limpios · smoke manual QGIS 4 completo
  (sin cuelgue; 430 pts/6109 m = 14.24 m; estructuras sobre el perfil; collar Z
  correcto; interpretaciones heredadas + persistencia; export GPKG/PNG OK).
- **Referencia**: `docs/maintenance/session_2026-09-23_crs_sampling_hardening.md`.
- **Sin bugs abiertos**. Diferidos: leyenda (tamaño/jerarquía), remuestreo
  bilineal, selector multi-línea (Fase 1.5), y reimportar el CSV de geología como
  UTF-8 (acentos se perdieron en el origen).

## 🚧 Session 2026-09-22 — Code Walkthrough Vault v2 (COMPLETO)

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
2. `docs/plans/implementation_plan_dem_section_v3.9.0.md`: **completo** (Fase 0 ✅,
   1 ✅, 1.5 ✅, 1.6 ✅, 2 ✅, 3 ✅) + **perfil suavizado** ✅ (extra). Opciones:
   - **Geología sobre el perfil suavizado (v3.9.1)** → plan aprobado (Opción A),
     pendiente: `docs/plans/implementation_plan_smoothed_geology_v3.9.1.md`.
   - **Selector multi-línea** (deuda; resolver + `section_feature_id` ya listos).
   - **Goal 1.1** (symbology/legend preview) o **Goal 1.5** (tests proyección).
   - Preparar **release v3.9.0/v3.9.1** (`/release-plugin`).
