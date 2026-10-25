# Implementation Plan — Consolidate Code Walkthrough on v2

**Status**: MERGEADO en `main` en `30b90605`
**Created**: 2026-10-24
**Scope**: dejar `code_walkthrough_v2` (ES/EN) como única bóveda, archivar v1 y
reapuntar índices/enlaces
**Branch propuesta**: `docs/code-walkthrough-v2-consolidation`

---

## 1. Recomendación

Sí: **quedarse con v2** y archivar v1.

| Dato | v1 | v2 |
|---|---:|---:|
| Archivos | 98 | **189** |
| Notas | pocas decenas | **151 sustantivas + 23 hubs** |
| Cobertura | parcial | archivo por archivo, método por método |
| Estado | legado | índice y `sync_vault_mirrors.sh` ya v2-first |

La duplicación ya causó trabajo real: la actualización de arquitectura tuvo que
repetirse en cinco copias. Mantener dos bóvedas garantiza que vuelvan a divergir.

**No se borra v1 de inmediato**: se archiva después de mapear sus 24 notas exclusivas.

---

## 2. Estado actual

### Bóvedas

```text
docs/code_walkthrough/        v1 ES, 98 archivos, ~912 KB
docs/code_walkthrough_en/     v1 EN, 97 archivos
docs/code_walkthrough_v2/     v2 ES, 189 archivos, ~3.2 MB
docs/code_walkthrough_en_v2/  v2 EN, 189 archivos, ~3.1 MB
```

`docs/ARCHITECTURE_EN.md` es la arquitectura canónica; las copias
`ARCHITECTURE_EN.md` de las bóvedas son espejos generados por
`scripts/sync_vault_mirrors.sh` (ya solo v2).

### Referencias que todavía apuntan a v1

| Archivo | Referencia |
|---|---|
| `docs/DOCS_INDEX.md` | `code_walkthrough/Index.md` (ES/EN) |
| `README_DEV.md` | `docs/code_walkthrough/Index.md` |
| `docs/ARCHITECTURE_EN.md` | enlaces `[doc](code_walkthrough/<slug>.md)` |
| `docs/code_walkthrough_v2/Index.md` | “v1 se mantiene intacta” |
| `docs/code_walkthrough_en_v2/Index.md` | same |
| `scripts/sync_vault_mirrors.sh` | comentario “v1 frozen” (correcto, pero el script aún no elimina v1) |
| `.gitignore` | reglas de directorios fantasma de v1 |

### Notas exclusivas de v1 (24)

```text
access_control_service.md   adapters.md                 dialog_mixins.md
drillhole_tabs.md           export_package.md           export_service.md
i18n.md                     __init__.md                 input_manager.md
interpretation_manager.md   interpretation_mixins.md    plugin_mixins.md
preview_mixins.md           profile_service.md          projection_engine.md
renderers.md                settings_tabs.md            signal_manager.md
state_manager.md            survey_processor.md         tasks.md
tool_manager.md             ui_pages.md                 validation.md
```

### Notas nuevas que v2 aún no tiene

- `section_feature_selector.md` (selector 2 vértices).
- `interpretation_tab.md` (tab movida a Settings).

---

## 3. Mapeo propuesto v1 → v2

| v1 | Destino v2 | Acción |
|---|---|---|
| `access_control_service.md` | `access_control_service.md` (nueva) | migrar contenido o crear nota |
| `adapters.md` | `layer_gui_adapters.md` | redirigir |
| `dialog_mixins.md` | `dialog_facade_mixin`, `dialog_lifecycle_mixin`, `dialog_message_mixin` | dividir referencia |
| `drillhole_tabs.md` | `collar_tab`, `survey_tab`, `interval_tab` | redirigir |
| `export_package.md` | `orchestrator`, `layer_core_services_export` | redirigir |
| `export_service.md` | `orchestrator` | redirigir / nota de shim |
| `i18n.md` | `layer_core_utils` | verificar y migrar detalle |
| `__init__.md` | `root`, `layer_plugin` | redirigir |
| `input_manager.md` | `dialog_input_manager` | redirigir |
| `interpretation_manager.md` | `dialog_interpretation_manager` | redirigir |
| `interpretation_mixins.md` | `interpretation_inheritance_mixin`, `interpretation_persistence_mixin` | dividir |
| `plugin_mixins.md` | `layer_plugin`, `lifecycle` | redirigir |
| `preview_mixins.md` | `preview_callbacks_mixin`, `preview_render_mixin` | dividir |
| `profile_service.md` | `topography`, `layer_core_services` | verificar; crear nota si falta |
| `projection_engine.md` | `layer_core_services_drillhole` | verificar y migrar |
| `renderers.md` | `layer_gui_renderers` | redirigir |
| `settings_tabs.md` | `default_tab`, `advanced_tab`, `symbology_tab`, `interpretation_tab` | dividir |
| `signal_manager.md` | `dialog_signal_manager` | redirigir |
| `state_manager.md` | `dialog_state_manager` | redirigir |
| `survey_processor.md` | `layer_core_services_drillhole` | verificar; crear nota si falta |
| `tasks.md` | `layer_gui_tasks` | redirigir |
| `tool_manager.md` | `dialog_tool_manager` | redirigir |
| `ui_pages.md` | `layer_gui_ui_pages` | redirigir |
| `validation.md` | `layer_core_validation`, `validation_helpers` | redirigir |

**Regla**: ninguna nota de v1 se elimina hasta que su contenido esté cubierto o su
destino exista. Las que no tengan equivalente exacto se migran como nota nueva en v2.

---

## 4. Trabajo de consolidación

### 4.1 Crear las notas que faltan en v2

- `section_feature_selector.md`:
  - filtro de 2 vértices, `fid — label`, campo de etiqueta;
  - propagación de `section_feature_id` a preview/export/LOD;
  - relación con `section_page`.
- `interpretation_tab.md`:
  - almacenamiento JSON/capa, campos personalizados, herencia;
  - ubicación en `SettingsPage`;
  - alias `page_interpretation`.
- Las 5 notas dudosas (`access_control_service`, `i18n`, `profile_service`,
  `projection_engine`, `survey_processor`) según auditoría de contenido.

### 4.2 Reapuntar índices y enlaces

- `docs/DOCS_INDEX.md`: v2 ES/EN.
- `README_DEV.md`: v2 ES/EN.
- `docs/code_walkthrough_v2/Index.md` y `_en_v2`: quitar “v1 intacta”; declarar
  v2 como única bóveda.
- `docs/ARCHITECTURE_EN.md`: cambiar `[doc](code_walkthrough/...)` por
  `[doc](code_walkthrough_v2/...)` y resolver slugs que solo existían en v1.
- `docs/DOCS_STYLE_GUIDE.md`: actualizar ejemplos.
- `scripts/sync_vault_mirrors.sh`: `transform()` debe aceptar
  `code_walkthrough_v2/` (y `_en_v2/`) además de `code_walkthrough/`.
- `docs/ARCHITECTURE_EN.md` y espejos: los enlaces Markdown deben apuntar a v2;
  los wikilinks `[[slug]]` no cambian.

### 4.3 Archivar v1

Mover, no borrar:

```text
docs/archive/code_walkthrough_v1/
docs/archive/code_walkthrough_v1_en/
```

- `git mv` para conservar historia.
- Añadir `README.md` en cada carpeta:
  “Archivado 2026-10-24; usar docs/code_walkthrough_v2/”.
- Añadir banner `> [!warning] DEPRECATED` en los `Index.md` de v1 **antes** de mover.
- Mantener `.obsidian` solo si el archivo histórico lo necesita; si no, excluirlo.

### 4.4 Limpieza

- `.gitignore`: conservar reglas fantasma solo si el archivo v1 sigue presente;
  documentar que v1 está archivada.
- `docs/DOCUMENTATION_PROCESS.md`: actualizar la nota de directorios fantasma.
- `scripts/sync_vault_mirrors.sh`: eliminar comentarios “v1 frozen” obsoletos.
- Comprobar que `docs/source/index.rst` no incluye las bóvedas (no debería).

---

## 5. Auditoría de enlaces

Antes de archivar:

1. Extraer todos los `[[wikilinks]]` de v2 y comprobar que resuelven a un `.md`.
2. Extraer todos los `[doc](code_walkthrough/...)` de `docs/ARCHITECTURE_EN.md` y
   comprobar que el slug existe en v2.
3. Revisar enlaces externos a v1 (`README_DEV`, `DOCS_INDEX`, mantenimiento).
4. Ejecutar:

```bash
bash scripts/sync_vault_mirrors.sh --check
make docs-check
python3 scripts/check_docs.py
```

5. Añadir un test/script de verificación de wikilinks si no existe; mínimo, un
   `grep` de slugs inexistentes en CI.

---

## 6. Tests / gates

- `check_docs`: PASS.
- `sync_vault_mirrors.sh --check`: PASS (arquitectura y estructura).
- `docs-check`: PASS.
- `forge validate`: PASS.
- Suite normal: sin cambios de código, pero ejecutar ≥829 por higiene.
- Búsqueda de referencias activas a `code_walkthrough/` fuera del archivo:
  solo permitidas en `docs/archive/` y notas históricas.

---

## 7. Fases

1. **Fase 0 — Auditoría**: mapear las 24 notas, decidir destino exacto, listar enlaces
   v1 en arquitectura/índices.
2. **Fase 1 — Completar v2**: crear `section_feature_selector`, `interpretation_tab`
   y las notas que falten; migrar contenido único.
3. **Fase 2 — Reapuntar**: índices, README, arquitectura, `sync_vault_mirrors.sh` y
   estilo; verificar enlaces.
4. **Fase 3 — Archivar v1**: banners, `git mv`, README de archivo, `.gitignore`.
5. **Fase 4 — Gates/cierre**: docs-check, mirror-check, suite, changelog/devlog.

Cada fase es un commit atómico; v1 no se mueve hasta que la Fase 2 esté verde.

---

## 8. Riesgos y mitigación

| Riesgo | Mitigación |
|---|---|
| Perder contenido único de v1 | auditoría nota por nota; archivar, no borrar |
| Enlaces `[doc](code_walkthrough/...)` rotos | script de comprobación + actualización a v2 |
| Wikilinks de Obsidian rotos | validar slugs v2 antes de mover |
| `sync_vault_mirrors.sh` copia mal | ampliar `transform()` y probar `--check` |
| Pérdida de historia Git | `git mv`, no `rm` |
| Confusión de dos bóvedas durante la transición | banner DEPRECATED + README de archivo |
| El sitio Sphinx dependa de v1 | comprobar `docs/source/index.rst` y `docs-check` |

---

## 9. Criterios de aceptación

- Solo hay una bóveda activa: `docs/code_walkthrough_v2/` + `_en_v2/`.
- `docs/DOCS_INDEX.md` y `README_DEV.md` apuntan a v2.
- `docs/ARCHITECTURE_EN.md` no tiene enlaces a `code_walkthrough/` (v1).
- Las 24 notas v1 están cubiertas o migradas.
- Existen `section_feature_selector.md` e `interpretation_tab.md` en v2.
- `sync_vault_mirrors.sh --check` y `docs-check` pasan.
- v1 está en `docs/archive/` con README de redirección.
- No hay cambios de código funcional.

---

## 10. Resultado

Implementado y mergeado en `main` en `30b90605`:

- v2 ES/EN es la única bóveda activa;
- 4 notas migradas y 2 nuevas (`section_feature_selector`, `interpretation_tab`);
- arquitectura, índices, README y `sync_vault_mirrors.sh` apuntan a v2;
- v1 archivada en `docs/archive/code_walkthrough_v1*`;
- `sync_vault_mirrors.sh --check`, `docs-check` y `check_docs` PASS.
