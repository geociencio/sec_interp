# Sesión: Update ai-context-core v3.2.1
**Fecha**: 2026-02-08
**Tema**: `update_ai_core_v321`

## Objetivos Alcanzados
- Actualización de `ai-context-core` de v3.2.0 a v3.2.1.
- Verificación confirmada de los Bug 1, 2 y 3 relacionados con i18n scope.
- Formateo masivo del proyecto con `black` para asegurar consistencia.
- Documentación de los fallos encontrados en la v3.2.0 y su resolución.

## Detalles Técnicos
- El scope `gui_only` ahora reduce el ruido de 882 strings a 399 en `sec_interp`.
- Se corrigió la integración de la opción `--i18n-scope` en el CLI.
- Se actualizaron los archivos de traducción (`.ts` y `.qm`) para reflejar el estado actual del proyecto.

## QA
- Ruff y Black pasaron tras el formateo.
- `ai-ctx analyze` arrojó un score de 40.6 (esperado tras los cambios recientes y el cambio de herramienta).
