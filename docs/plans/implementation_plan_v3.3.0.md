# Plan de Implementación - Fase v3.3.0 (Refactorización Cautelosa)

## Objetivo General

Reiniciar las refactorizaciones de la v3.3.0 tras una regresión a un estado estable. El foco principal es la **Estabilidad de Memoria (Ciclo de Vida de Señales)** y la **Seguridad de Tipos**, aplicando un enfoque de "Cambio-Validación" granular.

---

## User Review Required

> [!IMPORTANT]
> **Estrategia Cautelosa (Cambio-Validación)**
> En lugar de una refactorización masiva, se propone:
> 1. Modificar un solo componente/módulo a la vez.
> 2. Ejecutar `make docker-test` inmediatamente después de cada cambio.
> 3. No proceder al siguiente componente si los tests fallan o hay regresiones de estabilidad.
> 4. Eliminar el uso de `contextlib.suppress` inseguro, reemplazándolo por logging explícito y manejo de errores.

---

## Proposed Changes

### Fase 1: Estabilidad de Recursos y Ciclo de Vida (Prioridad P0)

Basado en los hallazgos críticos de `DEVELOPER_ANALYSIS.md`.

##### [MODIFY] [gui/dialog_signal_manager.py](file:///home/jmbernales/qgispluginsdev/sec_interp/gui/dialog_signal_manager.py)
- Implementar `_disconnect_known_page_signals` para asegurar que las páginas sin método `disconnect_signals` se limpien.
- Mejorar el logging de desconexión.

##### [MODIFY] [gui/tools/measure_tool.py](file:///home/jmbernales/qgispluginsdev/sec_interp/gui/tools/measure_tool.py)
- Implementar `cleanup_finalized` para limpiar elementos gráficos (rubber bands, markers) al cerrar el diálogo, incluso si la medición está finalizada.

##### [MODIFY] [gui/main_dialog.py](file:///home/jmbernales/qgispluginsdev/sec_interp/gui/main_dialog.py)
- Orquestar la limpieza completa en `closeEvent` llamando a los nuevos métodos de limpieza de herramientas y managers.

##### [MODIFY] [gui/preview_renderer.py](file:///home/jmbernales/qgispluginsdev/sec_interp/gui/preview_renderer.py)
- Corregir `_cleanup_layers` para realizar `rb.reset()` y `rb = None` en los rubber bands de interpretación.

---

### Fase 2: Calidad Core y Typed Orchestrators (Prioridad P1)

##### [MODIFY] [core/services/drillhole_service.py](file:///home/jmbernales/qgispluginsdev/sec_interp/core/services/drillhole_service.py)
 - **Evolución a Orquestador**: Eliminar el uso de tuplas indexadas (`result[0]`) y forzar el uso de Dataclasses (`DrillholeProjection`).
 - **Limpieza de Delegación**: Eliminar métodos de "pasamanería" que solo delegan sin lógica adicional, exponiendo los procesadores necesarios o simplificando la interfaz.
 - **Validación Centralizada**: Mover validaciones de parámetros de entrada de los procesadores al inicio del servicio.

##### [MODIFY] core/services/ (Otros)
- Incrementar Return Type Hints en:
  - `geology_service.py`
  - `structure_service.py`
- Eliminar `contextlib.suppress` inseguro en `controller.py` y mejorar el reporte de errores en la desconexión de capas.

---

### Fase 3: Auditoría i18n GUI-Focus

##### [MODIFY] gui/
- Aplicar `tr()` a los strings detectados en la capa `gui/` y `SecInterpDialog`.
- Evitar tocar scripts de tests para no contaminar el análisis de i18n.

---

## Verification Plan

### Flujo de Trabajo Mandatorio
Para cada cambio realizado:
1. **Linting**: `/fix-linting` (enfocado solo en el archivo modificado).
2. **Unit Tests**: `uv run python3 -m unittest tests/gui/test_[modulo].py` (si existe).
3. **Integrity Scan**: `make docker-test` (Validación completa de 450 tests).
4. **Analysis**: `uv run qgis-analyzer summary` para verificar mejora en métricas.

### Pruebas Manuales Específicas
- **Prueba de Stress de Señales**: Abrir y cerrar el diálogo principal 10 veces seguidas manteniendo QGIS abierto, verificando en los logs que todas las desconexiones fueron exitosas.
- **Prueba de Medición Huérfana**:
  1. Activar herramienta de medición.
  2. Finalizar una medición (doble click).
  3. Cerrar el plugin.
  4. Verificar visualmente que el "Rubber Band" rojo y los vértices han desaparecido del canvas de QGIS.

## Métricas de Éxito
- **Estabilidad**: 450/450 tests OK tras cada commit.
- **Type Hints (Returns)**: Incrementar de 45.0% hacia la meta del 70%.
- **Signal Leaks**: Reducir de 14 a 0 hallazgos detectados por `qgis-analyzer`.
