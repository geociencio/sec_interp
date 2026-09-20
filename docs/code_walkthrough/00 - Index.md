---
tags:
  - secinterp
  - code-walkthrough
  - moc
aliases:
  - SecInterp Code Walkthrough
  - Guía de Código SecInterp
cssclass: secinterp-moc
---

# 🗺️ SecInterp — Code Walkthrough (MOC)

> [!abstract] Propósito
> Esta bóveda documenta **archivo por archivo** la implementación de SecInterp.
> Cada nota explica el rol, los patrones y las relaciones de un módulo del código.
> Se irá ampliando progresivamente.

> [!info] Contexto del proyecto
> - **Plugin**: SecInterp (Section Interpreter) — QGIS ≥ 3.28, QGIS 4.x ready
> - **Arquitectura**: Clean Architecture (Core/GUI separation)
> - **Versión documentada**: 3.8.0
> - Ver también: [[ARCHITECTURE_EN]] · [[ARCHITECTURE_MONOLITHIC_VS_CLEAN_EN]] · [[PLUGIN_REPORT_AND_COMPARISON_EN]]

---

## 📚 Índice de notas

### Nivel raíz (entry point)
| # | Módulo | Estado | Descripción breve |
|---|--------|:------:|-------------------|
| 01 | [[01 - sec_interp_plugin]] | ✅ | Clase raíz `SecInterp`: ciclo de vida del plugin, toolbar, DI |
| 02 | [[02 - __init__]] | ✅ | Factory `classFactory` que QGIS invoca |
| 03 | [[03 - logger_config]] | ✅ | Logging centralizado + handler QGIS |

### Capa Core (`core/`)
| # | Módulo | Estado | Descripción breve |
|---|--------|:------:|-------------------|
| 10 | [[10 - controller]] | ✅ | `ProfileController` — orquestador de servicios |
| 11 | [[11 - domain]] | ✅ | DTOs: `PreviewParams`, `ProfileData`, `GeologySegment`… |
| 12 | [[12 - exceptions]] | ⏳ | Jerarquía `SecInterpError` |
| 13 | [[13 - profile_service]] | ⏳ | Extracción de topografía |
| 14 | [[14 - geology_service]] | ⏳ | Intersecciones geológicas |
| 15 | [[15 - drillhole_service]] | ⏳ | Proyección de sondajes |
| 16 | [[16 - validation]] | ⏳ | Pipeline de validación |
| 17 | [[17 - safe_loader]] | ✅ | Carga lazy y tolerante a fallos |
| 18 | [[18 - i18n]] | ⏳ | `TranslatableMixin` |

### Capa GUI (`gui/`)
| # | Módulo | Estado | Descripción breve |
|---|--------|:------:|-------------------|
| 20 | [[20 - main_dialog]] | ⏳ | `SecInterpDialog` — orquestador de managers |
| 21 | [[21 - dialog_preview_manager]] | ⏳ | Ciclo de preview y canvas |
| 22 | [[22 - dialog_export_manager]] | ⏳ | UI de exportación |
| 23 | [[23 - renderers]] | ⏳ | Renderers especializados |
| 24 | [[24 - tasks]] | ⏳ | `QgsTask` en background |
| 25 | [[25 - adapters]] | ⏳ | Fase "Extract" (QGIS → DTOs) |

### Capa Exporters (`exporters/`)
| # | Módulo | Estado | Descripción breve |
|---|--------|:------:|-------------------|
| 30 | [[30 - base_exporter]] | ⏳ | Contrato `BaseExporter` |
| 31 | [[31 - vector_exporter]] | ⏳ | GPKG/SHP/DXF |

> [!tip] Leyenda
> ✅ documentado · ⏳ pendiente · 🔄 en revisión

> [!note] Documentos espejo
> Los archivos `ARCHITECTURE_EN.md`, `ARCHITECTURE_MONOLITHIC_VS_CLEAN_EN.md` y `PLUGIN_REPORT_AND_COMPARISON_EN.md` dentro de esta bóveda son **copias espejo** de `docs/` (fuente de verdad). Se mantienen aquí para que los wikilinks resuelvan en Obsidian. Si actualizas el original en `docs/`, re-sincroniza estas copias.

---

## 🧭 Cómo leer estas notas

Cada nota sigue la misma plantilla:

1. **Frontmatter** — tags y aliases para búsqueda.
2. **Resumen** — qué hace y por qué existe.
3. **Diagrama** — Mermaid de relaciones.
4. **Recorrido del código** — método por método.
5. **Patrones** — qué patrones de diseño aplica.
6. **Relaciones** — wikilinks a módulos relacionados.
7. **Observaciones** — notas, riesgos y mejoras.

> [!warning] Convención de enlaces
> Los enlaces `[[...]]` pueden aparecer **sin resolver** hasta que se cree la nota.
> Eso es intencional: marcan el trabajo futuro.

---

## 🔖 Tags usados

`#secinterp` · `#code-walkthrough` · `#moc` · `#core` · `#gui` · `#exporters` · `#entry-point` · `#di` · `#i18n` · `#qgstask`

---

*Nota raíz de la bóveda — actualizar al añadir cada nueva nota.*
