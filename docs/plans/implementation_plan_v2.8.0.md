# Plan de Implementación - Fase v2.8.0 (Reducción de Deuda y Mejoras de UI)

## Objetivo General
Iniciar la Fase v2.8.0 con un enfoque en la reducción de deuda técnica heredada y la implementación de controles de visibilidad para la leyenda en la visualización previa.

- [x] Reducción de Deuda Técnica: Refactorizar `GeologyService` (métodos largos).
- [x] Implementar checkbox de visibilidad de leyenda en Preview (con persistencia).
- [x] Corregir build de documentación API (Mocks y Annotations).
- [ ] Mejorar cobertura de tests de integración para proyección 3D.

---

## Proposed Changes

### [Componente] Core Logic & Models

#### [MODIFY] [settings_model.py](file:///home/jmbernales/qgispluginsdev/sec_interp/core/models/settings_model.py)
- Añadir campo `show_legend: bool = True` a la dataclass `PreviewSettings`.

---

### [Componente] UI Implementation

#### [MODIFY] [preview_page.py](file:///home/jmbernales/qgispluginsdev/sec_interp/gui/ui/pages/preview_page.py)
- Añadir el checkbox `chk_legend` en la sección de controles de visualización.
- Conectar la señal `stateChanged` del checkbox para actualizar el preview.

#### [MODIFY] [main_dialog_settings.py](file:///home/jmbernales/qgispluginsdev/sec_interp/gui/main_dialog_settings.py)
- Actualizar `_load_preview_settings` y `_save_preview_settings` para persistir el estado de `chk_legend`.
- Actualizar `reset_to_defaults` para incluir el estado inicial de la leyenda.

---

### [Componente] Rendering Engine

#### [MODIFY] [preview_renderer.py](file:///home/jmbernales/qgispluginsdev/sec_interp/gui/preview_renderer.py)
- Modificar el método `draw_legend` para verificar el estado de la configuración `show_legend` antes de delegar el renderizado al `legend_renderer`.

---

### [Componente] Technical Debt Reduction (SecInterp v2.8.0 Initiation)

#### [MODIFY] [geology_service.py](file:///home/jmbernales/qgispluginsdev/sec_interp/core/services/geology_service.py)
- Refactorización de métodos largos (50+ líneas) identificados en el cierre de la v2.7.0.
- Extracción de lógica de procesamiento de geometrías a métodos privados más granulares.

#### [NEW] [test_3d_integration.py](file:///home/jmbernales/qgispluginsdev/sec_interp/tests/integration/test_3d_integration.py)
- Implementar suite de pruebas de integración para la exportación 3D, cubriendo casos de trazas e intervalos con coordenadas proyectadas.

---

## Verification Plan

### Automated Tests
- Ejecutar suite completa con Docker:
  ```bash
  make docker-test
  ```
- Pruebas específicas para el modelo de settings:
  ```bash
  uv run python3 -m unittest tests/core/test_settings_model.py
  ```

### Manual Verification
1. Abrir el plugin en QGIS.
2. Navegar a la pestaña de **Preview**.
3. Activar/Desactivar el nuevo checkbox de **Legend**.
4. Verificar que la leyenda aparece/desaparece instantáneamente en el canvas de preview.
5. Cerrar y reabrir el plugin para confirmar que el estado del checkbox persiste.
