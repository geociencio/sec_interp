---
tags:
  - secinterp
  - code-walkthrough
  - moc
aliases:
  - SecInterp Code Walkthrough v2
  - Guía de Código SecInterp v2
cssclass: secinterp-moc
---

# 🗺️ SecInterp — Code Walkthrough v2 (MOC)

> [!abstract] Propósito
> Bóveda **completa y autónoma** (v2) que documenta archivo-por-archivo la
> implementación de SecInterp. Cada nota alcanza una profundidad de **400–500 líneas**
> (notas sustantivas) con recorrido método-por-método, flujo de datos, patrones,
> manejo de errores y tests. La bóveda v1 (`code_walkthrough/`) se mantiene intacta.

> [!info] Contexto
> - **Plugin**: SecInterp — QGIS ≥ 3.28, QGIS 4.x ready
> - **Arquitectura**: Clean Architecture (Core/GUI separation)
> - **Versión documentada**: 3.8.0
> - **Estado**: 🚧 Fase 0 (piloto) — 3 notas de referencia completas

---

## 📚 Índice de notas

### ✅ Piloto Fase 0 (referencia de profundidad)

| Nota | Tier | Fuente | Líneas |
|---|:---:|---|---:|
| [[drillhole]] | A | `core/utils/drillhole.py` | ~410 |
| [[core_interfaces]] | C | `core/interfaces/` (paquete) | ~400 |
| [[path_resolver]] | B | `core/services/export/path_resolver.py` | ~300 |

### ⏳ Resto de la bóveda (Fases 1–4)

Las 175 notas restantes se generarán y enriquecerán por capas:
- **Fase 1** — Core (`domain`, `interfaces`, `models`, `utils`, `validation`, `services/export`)
- **Fase 2** — GUI (`adapters`, `renderers`, `tasks`, `tools`, `ui/`, managers, `preview_*`)
- **Fase 3** — Exporters / Plugin / Raíz
- **Fase 4** — `layer_*` + `Index` + espejos

> [!warning] Convención de enlaces
> Los `[[...]]` pueden aparecer **sin resolver** hasta que se cree la nota. Es
> intencional: marcan el trabajo futuro.

---

## 🧭 Cómo leer estas notas

Cada nota sigue la plantilla v2 (`_template.md`):

1. **Frontmatter** — tags y aliases.
2. **Resumen + ¿por qué existe?** — problema/solución.
3. **Diagrama** — Mermaid de relaciones.
4. **Imports** — lectura arquitectónica.
5. **Inventario** — clases/funciones/constantes.
6. **Recorrido método-por-método** — el núcleo de profundidad.
7. **Flujo de datos** — entrada → transformación → salida.
8. **Patrones / API / Errores / Tests / Observaciones**.
9. **Notas relacionadas** — wikilinks.

> [!tip] Documentos de estructura
> Ver [[project_structure]] (árbol) y [[project_structure_table]] (vista tabular por
> profundidad) para el mapa completo del plugin.

---

## 🔖 Tags usados

`#secinterp` · `#code-walkthrough` · `#moc` · `#core` · `#gui` · `#exporters` · `#plugin` · `#interfaces` · `#services` · `#utils`

---

*Nota raíz de la bóveda v2 — actualizar al añadir cada nueva nota.*
