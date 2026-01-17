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

### [COMPLETADO] Objetivo 1: Documentación Sphinx Automatizada (Salida Externa)


#### Contexto
Generar referencias de API automáticas y limpiar el repositorio de archivos HTML estáticos.

#### [MODIFY] [.gitignore](file:///home/jmbernales/qgispluginsdev/sec_interp/.gitignore)
Añadir `docs/build/` y `help/html/` para evitar rastrear binarios de documentación.

#### [NEW] [conf.py](file:///home/jmbernales/qgispluginsdev/sec_interp/docs/source/conf.py)
Configuración de Sphinx con soporte para `autodoc` y `napoleon`.

#### [NEW] [build_docs.sh](file:///home/jmbernales/qgispluginsdev/sec_interp/scripts/build_docs.sh)
#### [NEW] [build_docs.sh](file:///home/jmbernales/qgispluginsdev/sec_interp/scripts/build_docs.sh)
Script para construir la documentación y moverla automáticamente al directorio externo definido por el usuario.

> [!NOTE]
> **Finalizado el 2026-01-16**
>
> Infraestructura implementada. `conf.py` configurado con temas y extensiones. `build_docs.sh` genera documentación en `../sec_interp_docs` y sincroniza `help/html` para uso local, pero manteniendo el repo limpio (archivos HTML eliminados de git).


---

### [COMPLETADO] Objetivo 2: Centralización del Sistema de Logging
> [!NOTE]
> Finalizado el 2026-01-13. Implementado logger raíz "SecInterp" con propagación jerárquica y rotación de archivos.

---

### [COMPLETADO] Objetivo 3: Arquitectura de Validación de 3 Niveles

> [!NOTE]
> **Finalizado el 2026-01-15**
>
> Implementación de arquitectura de validación robusta basada en 3 niveles jerárquicos (Tipos, Lógica de Negocio y Dominio de QGIS) sin dependencias externas. Validada con suites de pruebas dedicadas para cada nivel.

#### Arquitectura Propuesta

- [x] **Nivel 1: Type Validation (Dataclass Layer)**
    - Crear `core/validation/validators.py` con validadores reusables (range, type, etc).
    - Refactorizar `settings_model.py` para usar estos validadores en `__post_init__`.
    - Sanitización automática de inputs (clamping) en lugar de errores duros.

- [x] **Nivel 2: Business Logic Validation**
    - Refactorizar `core/validation/project_validator.py`.
    - Implementar `ValidationContext` para acumular errores (evitar "fail-fast").
    - Validar dependencias entre capas (ej: Si hay Drillholes, checks de Collar/Survey).

- [x] **Nivel 3: Domain Validation (Service Layer)**
    - **GeologyService**:
        - `band_number`: Validar > 0 y existencia en raster.
        - `outcrop_name_field`: Validar existencia en capa de afloramientos.
        - `line_lyr`: Validar layer validity explícita.
    - **DrillholeService**:
        - `buffer_width`: Validar > 0.
        - `section_azimuth`: Validar rango [0, 360].
        - `fields`: Validar existencia de campos requeridos (id, x, y, z, depth) en sus respectivas capas.
    - **Tests**: Crear `tests/core/validation/test_service_validation.py` para cubrir casos borde.

#### Componentes a Implementar

##### [NEW] [validators.py](file:///home/jmbernales/qgispluginsdev/sec_interp/core/validation/validators.py)
Módulo con validadores reutilizables: `validate_range`, `validate_positive`, `validate_non_empty`, `coerce_type`, `FieldValidator`.

##### [MODIFY] [settings_model.py](file:///home/jmbernales/qgispluginsdev/sec_interp/core/models/settings_model.py)
Integrar validadores declarativos con metadatos de clase y aplicación en `__post_init__`.

##### [MODIFY] [project_validator.py](file:///home/jmbernales/qgispluginsdev/sec_interp/core/validation/project_validator.py)
Implementar `ValidationContext` y `RichValidationError` para errores con contexto enriquecido y sugerencias automáticas.

##### [NEW] [validation_helpers.py](file:///home/jmbernales/qgispluginsdev/sec_interp/core/validation/validation_helpers.py)
Helpers para validaciones cross-field: `DependencyRule`, `validate_dependencies`.

##### [MODIFY] Services (geology_service.py, drillhole_service.py)
Implementar cláusulas de guarda usando `core/validation/validators.py` al inicio de los métodos públicos principales (`generate_geological_profile`, `project_collars`, `prepare_task_input`).

##### [NEW] [test_service_validation.py](file:///home/jmbernales/qgispluginsdev/sec_interp/tests/core/validation/test_service_validation.py)
Suite de pruebas dedicada a verificar que los servicios rechacen configuraciones inválidas (Fail Fast pattern).

#### Estimación Detallada

| Componente | Esfuerzo | Fase |
|-----------|----------|------|
| validators.py | 4 horas | Sprint 1 |
| settings_model.py refactor | 3 horas | Sprint 1 |
| Tests Level 1 | 2 horas | Sprint 1 |
| project_validator.py refactor | 5 horas | Sprint 2 |
| validation_helpers.py | 2 horas | Sprint 2 |
| Tests Level 2 | 3 horas | Sprint 2 |
| Services (domain validation) | 4 horas | Sprint 3 |
| Tests Level 3 | 2 horas | Sprint 3 |
| Documentation (ADR + Guides) | 3 horas | Sprint 3 |
| Walkthrough | 2 horas | Sprint 3 |
| **TOTAL** | **30 horas (~4 días)** | |



---

### Objetivo 4: Reducción de Deuda Técnica (Arquitectura) [EN PROGRESO]

#### [MODIFY] [main_dialog.py](file:///home/jmbernales/qgispluginsdev/sec_interp/gui/main_dialog.py)
Continuar la fragmentación de la lógica del diálogo principal hacia componentes especializados (sidebar, status bar, etc.).

---

### [COMPLETADO] Objetivo 5 & 6: Exportación 3D de Sondajes (Original y Proyectada)
> [!NOTE]
> Finalizado el 2026-01-12. Implementados `DrillholeTrace3DExporter` y `DrillholeInterval3DExporter`. Controles añadidos a Settings/Advanced.

---

### [COMPLETADO] Objetivo 7: Infraestructura de Testing Robusta (Dockerización)

#### Contexto
Eliminar los errores de "ModuleNotFoundError: No module named 'qgis'" al ejecutar tests localmente, centralizando la ejecución en contenedores que replican el entorno real.

#### [MODIFY] [Makefile](file:///home/jmbernales/qgispluginsdev/sec_interp/Makefile)
Añadir objetivos para automatizar el ciclo de Docker:
- `docker-build`: Construir la imagen localmente.
- `docker-test`: Ejecutar la suite completa de tests dentro del contenedor.

#### [MODIFY] [README.md](file:///home/jmbernales/qgispluginsdev/sec_interp/README.md)
Actualizar las instrucciones de desarrollo para recomendar el uso de Docker o Dev Containers como estándar de oro para evitar problemas de dependencias.

> [!NOTE]
> **Finalizado el 2026-01-16**
>
> Infraestructura Docker implementada exitosamente. Se unificó el motor de pruebas a `unittest discover` y se automatizó la ejecución en contenedor con `make docker-test`. Los 349 tests pasan correctamente en el entorno aislado.

---

### [COMPLETADO] Objetivo 8: Estabilización Masiva de Mocks (Infrastructure Fix)
> [!IMPORTANT]
> Finalizado el 2026-01-15. Lograda estabilidad de 347/347 tests mediante `ModuleProxy`, `MockSignal` y reseteo preservativo de estado en `base_test.py`.

---

## Verification Plan

### 1. Verificación de Modelos (Pendiente)
Nuevos tests en `tests/core/test_settings_model.py` para validar la lógica de tipos y rangos sin dependencias externas.

### 2. Verificación de Servicios (Validación)
Ejecutar nueva suite de tests:
```bash
env PYTHONPATH=.. uv run python3 -m unittest tests/core/validation/test_service_validation.py
```

### 2. Test de Integración de Logging [PASADA]
Verificar que los mensajes llegan correctamente al `QgsMessageLog` de QGIS.

### 3. Simulación de Construcción Externa (Pendiente)
Validar que `build_docs.sh` genera archivos en la ruta esperada fuera del workspace actual.

### 4. Pruebas de Exportación 3D y UI [PASADA]
- Validar que los Checkboxes aparecen en **Settings/Advanced** y persisten los cambios.
- Validar que los Shapefiles generados por los nuevos exportadores (Trazas e Intervalos) se visualizan correctamente en la vista 3D de QGIS.

### 5. Verificación de Docker [PASADA]
Ejecutar `make docker-test` y confirmar que todos los tests pasan correctamente dentro del contenedor.

---

## Estimación de Esfuerzo Restante

| Objetivo | Esfuerzo | Prioridad |
|----------|----------|-----------|
| Documentación Sphinx/Limpieza | 3 días | Alta |
| **Arquitectura de Validación 3 Niveles** | **4 días** | **Alta** |
| [x] Infraestructura Docker (Testing) | 2 días | Alta |
| Refactor Main Dialog | 2 días | Baja |
| **TOTAL RESTANTE** | **9 días** | |

---

**Fecha Última Actualización:** 2026-01-15
**Autor:** Antigravity
**Estado:** Fase v2.7.0 en ejecución. Infraestructura de pruebas estabilizada.
