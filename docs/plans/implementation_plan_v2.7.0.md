# Plan de Implementación - Fase v2.7.0 (Excelencia Operativa y Documentación)

## Objetivo General

Consolidar la infraestructura de soporte del plugin SecInterp mediante la automatización de la documentación, la centralización de logs para facilitar el debugging y la adopción de Pydantic para una validación de datos más robusta.

---

## User Review Required

> [!IMPORTANT]
> **Eliminación de Pydantic**
>
> Siguiendo tu sugerencia, hemos **descartado** `pydantic`. Utilizaremos `dataclasses` y validaciones manuales nativas para mantener el proyecto sin dependencias externas adicionales.

> [!NOTE]
> **Estrategia de Documentación Sphinx**
>
> 1.  **Limpieza:** Eliminaremos los archivos HTML rastreados que polucionan las estadísticas del repo (59.8% HTML).
> 2.  **Salida Externa:** El proceso de construcción generará la documentación en un directorio fuera del proyecto (ej: `../sec_interp_docs`) para su despliegue en un repositorio alterno.

---

## Proposed Changes

### Objetivo 1: Documentación Sphinx Automatizada (Salida Externa)

#### Contexto
Generar referencias de API automáticas y limpiar el repositorio de archivos HTML estáticos.

#### [MODIFY] [.gitignore](file:///home/jmbernales/qgispluginsdev/sec_interp/.gitignore)
Añadir `docs/build/` y `help/html/` para evitar rastrear binarios de documentación.

#### [NEW] [conf.py](file:///home/jmbernales/qgispluginsdev/sec_interp/docs/source/conf.py)
Configuración de Sphinx con soporte para `autodoc` y `napoleon`.

#### [NEW] [build_docs.sh](file:///home/jmbernales/qgispluginsdev/sec_interp/scripts/build_docs.sh)
Script para construir la documentación y moverla automáticamente al directorio externo definido por el usuario.

---

### Objetivo 2: Centralización del Sistema de Logging

#### [MODIFY] [logger_config.py](file:///home/jmbernales/qgispluginsdev/sec_interp/logger_config.py)
Refactorizar para integrar un sistema de rotación de archivos y mejor integración con `QgsMessageLog`.

---

### Objetivo 3: Validación Nativa de Configuraciones (Sin Dependencias)

#### [NEW] [settings_model.py](file:///home/jmbernales/qgispluginsdev/sec_interp/core/models/settings_model.py)
Uso de `dataclasses` con `@property` y setters para validación de rangos y tipos (reemplazo de Pydantic).

#### [MODIFY] [config.py](file:///home/jmbernales/qgispluginsdev/sec_interp/core/config.py)
Integrar el nuevo modelo de datos para validar los valores de `QgsSettings` al cargar.

---

### Objetivo 4: Reducción de Deuda Técnica (Arquitectura)

#### [MODIFY] [main_dialog.py](file:///home/jmbernales/qgispluginsdev/sec_interp/gui/main_dialog.py)
Continuar la fragmentación de la lógica del diálogo principal hacia componentes especializados (sidebar, status bar, etc.).

---

### Objetivo 5: Exportación 3D de Trazas de Sondajes (Original y Proyectada)

#### Contexto
Exportar las trayectorias 3D reales (`LineStringZ`) y su representación proyectada sobre el plano de sección en el espacio 3D.

#### [NEW] [drillhole_3d_exporter.py](file:///home/jmbernales/qgispluginsdev/sec_interp/exporters/drillhole_3d_exporter.py)
Implementar exportador con dos modos:
- **Original**: Coordenadas (X, Y, Z) reales del sondaje.
- **Proyectada**: Coordenadas (X', Y', Z) proyectadas sobre el plano de la sección pero re-mapeadas al CRS global.

---

### Objetivo 6: Exportación 3D de Intervalos de Sondajes (Original y Proyectada)

#### [NEW] [drillhole_3d_interval_exporter.py](file:///home/jmbernales/qgispluginsdev/sec_interp/exporters/drillhole_3d_interval_exporter.py)
Exportar intervalos geológicos en ambos modos:
- **Original**: Segmentos 3D reales con atributos de litología.
- **Proyectada**: Segmentos proyectados sobre el plano de sección en el espacio 3D.

#### [MODIFY] [drillhole_service.py](file:///home/jmbernales/qgispluginsdev/sec_interp/core/services/drillhole_service.py)
Asegurar que el servicio preserve y entregue las coordenadas 3D originales para el motor de exportación.

#### [MODIFY] [settings_page.py](file:///home/jmbernales/qgispluginsdev/sec_interp/gui/ui/pages/settings_page.py)
Añadir controles (Checkboxes) en la pestaña **Advanced** para habilitar/deshabilitar las exportaciones 3D (Original y Proyectada) de sondajes.

#### [MODIFY] [main_dialog_settings.py](file:///home/jmbernales/qgispluginsdev/sec_interp/gui/main_dialog_settings.py)
Gestionar la persistencia de las nuevas preferencias de exportación 3D en `QgsSettings`.

### Objetivo 7: Infraestructura de Testing Robusta (Dockerización)

#### Contexto
Eliminar los errores de "ModuleNotFoundError: No module named 'qgis'" al ejecutar tests localmente, centralizando la ejecución en contenedores que replican el entorno real.

#### [MODIFY] [Makefile](file:///home/jmbernales/qgispluginsdev/sec_interp/Makefile)
Añadir objetivos para automatizar el ciclo de Docker:
- `docker-build`: Construir la imagen localmente.
- `docker-test`: Ejecutar la suite completa de tests dentro del contenedor.

#### [MODIFY] [README.md](file:///home/jmbernales/qgispluginsdev/sec_interp/README.md)
Actualizar las instrucciones de desarrollo para recomendar el uso de Docker o Dev Containers como estándar de oro para evitar problemas de dependencias.

---

## Verification Plan

### 1. Verificación de Modelos
Nuevos tests en `tests/core/test_settings_model.py` para validar la lógica de tipos y rangos sin dependencias externas.

### 2. Test de Integración de Logging
Verificar que los mensajes llegan correctamente al `QgsMessageLog` de QGIS.

### 3. Simulación de Construcción Externa
Validar que `build_docs.sh` genera archivos en la ruta esperada fuera del workspace actual.

### 4. Pruebas de Exportación 3D y UI
- Validar que los Checkboxes aparecen en **Settings/Advanced** y persisten los cambios.
- Validar que los Shapefiles generados por los nuevos exportadores (Trazas e Intervalos) se visualizan correctamente en la vista 3D de QGIS.

### 5. Verificación de Docker
Ejecutar `make docker-test` y confirmar que todos los tests (incluyendo integración y benchmarks) pasan correctamente sin errores de importación de QGIS.

---

## Estimación de Esfuerzo

| Objetivo | Esfuerzo | Prioridad |
|----------|----------|-----------|
| Documentación Sphinx/Limpieza | 3 días | Alta |
| Logging Centralizado | 2 días | Media |
| Modelos de Validación (Dataclasses) | 3 días | Media |
| **Exportación 3D Sondajes (Original/Proy)** | **4 días** | **Alta** |
| **Infraestructura Docker (Testing)** | **2 días** | **Alta** |
| Refactor Main Dialog | 2 días | Baja |
| **TOTAL** | **16 días** | |

---

**Fecha:** 2026-01-09
**Autor:** Antigravity
**Estado:** Propuesto para inicio de fase v2.7.0.
