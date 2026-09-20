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
| 10 | `core/controller.py` | ⏳ | `ProfileController` — orquestador de servicios |
| 11 | `core/domain/` | ⏳ | DTOs: `PreviewParams`, `ProfileData`, `GeologySegment`… |
| 12 | `core/exceptions.py` | ⏳ | Jerarquía `SecInterpError` |
| 13 | `core/services/profile_service.py` | ⏳ | Extracción de topografía |
| 14 | `core/services/geology_service.py` | ⏳ | Intersecciones geológicas |
| 15 | `core/services/drillhole_service.py` | ⏳ | Proyección de sondajes |
| 16 | `core/validation/` | ⏳ | Pipeline de validación |
| 17 | `core/utils/safe_loader.py` | ⏳ | Carga lazy y tolerante a fallos |
| 18 | `core/utils/i18n.py` | ⏳ | `TranslatableMixin` |

### Capa GUI (`gui/`)
| # | Módulo | Estado | Descripción breve |
|---|--------|:------:|-------------------|
| 20 | `gui/main_dialog.py` | ⏳ | `SecInterpDialog` — orquestador de managers |
| 21 | `gui/dialog_preview_manager.py` | ⏳ | Ciclo de preview y canvas |
| 22 | `gui/dialog_export_manager.py` | ⏳ | UI de exportación |
| 23 | `gui/renderers/` | ⏳ | Renderers especializados |
| 24 | `gui/tasks/` | ⏳ | `QgsTask` en background |
| 25 | `gui/adapters/` | ⏳ | Fase "Extract" (QGIS → DTOs) |

### Capa Exporters (`exporters/`)
| # | Módulo | Estado | Descripción breve |
|---|--------|:------:|-------------------|
| 30 | `exporters/base_exporter.py` | ⏳ | Contrato `BaseExporter` |
| 31 | `exporters/vector_exporter.py` | ⏳ | GPKG/SHP/DXF |

> [!tip] Leyenda
> ✅ documentado · ⏳ pendiente · 🔄 en revisión

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
