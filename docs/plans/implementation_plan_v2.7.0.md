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

### Objetivo 1: Documentación Sphinx Automatizada (Salida Externa) [PENDIENTE]

#### Contexto
Generar referencias de API automáticas y limpiar el repositorio de archivos HTML estáticos.

#### [MODIFY] [.gitignore](file:///home/jmbernales/qgispluginsdev/sec_interp/.gitignore)
Añadir `docs/build/` y `help/html/` para evitar rastrear binarios de documentación.

#### [NEW] [conf.py](file:///home/jmbernales/qgispluginsdev/sec_interp/docs/source/conf.py)
Configuración de Sphinx con soporte para `autodoc` y `napoleon`.

#### [NEW] [build_docs.sh](file:///home/jmbernales/qgispluginsdev/sec_interp/scripts/build_docs.sh)
Script para construir la documentación y moverla automáticamente al directorio externo definido por el usuario.

---

### [COMPLETADO] Objetivo 2: Centralización del Sistema de Logging
> [!NOTE]
> Finalizado el 2026-01-13. Implementado logger raíz "SecInterp" con propagación jerárquica y rotación de archivos.

---

### Objetivo 3: Validación Nativa de Configuraciones (Sin Dependencias) [PENDIENTE]

#### [NEW] [settings_model.py](file:///home/jmbernales/qgispluginsdev/sec_interp/core/models/settings_model.py)
Uso de `dataclasses` con `@property` y setters para validación de rangos y tipos (reemplazo de Pydantic).

#### [MODIFY] [config.py](file:///home/jmbernales/qgispluginsdev/sec_interp/core/config.py)
Integrar el nuevo modelo de datos para validar los valores de `QgsSettings` al cargar.

---

### Objetivo 4: Reducción de Deuda Técnica (Arquitectura) [EN PROGRESO]

#### [MODIFY] [main_dialog.py](file:///home/jmbernales/qgispluginsdev/sec_interp/gui/main_dialog.py)
Continuar la fragmentación de la lógica del diálogo principal hacia componentes especializados (sidebar, status bar, etc.).

---

### [COMPLETADO] Objetivo 5 & 6: Exportación 3D de Sondajes (Original y Proyectada)
> [!NOTE]
> Finalizado el 2026-01-12. Implementados `DrillholeTrace3DExporter` y `DrillholeInterval3DExporter`. Controles añadidos a Settings/Advanced.

---

### Objetivo 7: Infraestructura de Testing Robusta (Dockerización) [PENDIENTE]

#### Contexto
Eliminar los errores de "ModuleNotFoundError: No module named 'qgis'" al ejecutar tests localmente, centralizando la ejecución en contenedores que replican el entorno real.

#### [MODIFY] [Makefile](file:///home/jmbernales/qgispluginsdev/sec_interp/Makefile)
Añadir objetivos para automatizar el ciclo de Docker:
- `docker-build`: Construir la imagen localmente.
- `docker-test`: Ejecutar la suite completa de tests dentro del contenedor.

#### [MODIFY] [README.md](file:///home/jmbernales/qgispluginsdev/sec_interp/README.md)
Actualizar las instrucciones de desarrollo para recomendar el uso de Docker o Dev Containers como estándar de oro para evitar problemas de dependencias.

---

### [COMPLETADO] Objetivo 8: Estabilización Masiva de Mocks (Infrastructure Fix)
> [!IMPORTANT]
> Finalizado el 2026-01-15. Lograda estabilidad de 347/347 tests mediante `ModuleProxy`, `MockSignal` y reseteo preservativo de estado en `base_test.py`.

---

## Verification Plan

### 1. Verificación de Modelos (Pendiente)
Nuevos tests en `tests/core/test_settings_model.py` para validar la lógica de tipos y rangos sin dependencias externas.

### 2. Test de Integración de Logging [PASADA]
Verificar que los mensajes llegan correctamente al `QgsMessageLog` de QGIS.

### 3. Simulación de Construcción Externa (Pendiente)
Validar que `build_docs.sh` genera archivos en la ruta esperada fuera del workspace actual.

### 4. Pruebas de Exportación 3D y UI [PASADA]
- Validar que los Checkboxes aparecen en **Settings/Advanced** y persisten los cambios.
- Validar que los Shapefiles generados por los nuevos exportadores (Trazas e Intervalos) se visualizan correctamente en la vista 3D de QGIS.

### 5. Verificación de Docker (Pendiente)
Ejecutar `make docker-test` y confirmar que todos los tests pasan correctamente dentro del contenedor.

---

## Estimación de Esfuerzo Restante

| Objetivo | Esfuerzo | Prioridad |
|----------|----------|-----------|
| Documentación Sphinx/Limpieza | 3 días | Alta |
| Modelos de Validación (Dataclasses) | 3 días | Media |
| Infraestructura Docker (Testing) | 2 días | Alta |
| Refactor Main Dialog | 2 días | Baja |
| **TOTAL RESTANTE** | **10 días** | |

---

**Fecha Última Actualización:** 2026-01-15
**Autor:** Antigravity
**Estado:** Fase v2.7.0 en ejecución. Infraestructura de pruebas estabilizada.
