# Plan de Implementación - Fase v2.9.0 (Análisis Avanzado y Geometría)

## Objetivo General
Evolucionar las capacidades geométricas de SecInterp para soportar perfiles no lineales (polilíneas/túneles) y consolidar la suite de verificación 3D, priorizando el saneamiento crítico de calidad del código base.

---

## Proposed Changes

### Objetivo 0: Saneamiento Crítico de Calidad (Inmediato)

#### Contexto
El análisis de calidad identificó un déficit crítico en type hints de retorno y alta complejidad ciclomática en métodos clave.

#### Componentes a Implementar

##### [MODIFY] Type Hints en Return Values
Incrementar cobertura de return type hints al >80% en:
- `core/services/drillhole_service.py`
- `core/services/geology_service.py`
- `core/validation/project_validator.py`
- `gui/main_dialog_preview.py`

##### [REFACTOR] [drillhole_service.py](file:///home/jmbernales/qgispluginsdev/sec_interp/core/services/drillhole_service.py)
Reducir CC en `_project_single_detached_collar` (actual CC=25) mediante extracción de lógica de transformación.

##### [FIX] Legacy Imports & Docstrings
- Eliminar imports obsoletos de QGIS detectados por el analyzer.
- Rellenar docstrings faltantes en módulos core utilizando el estándar Google.

---

### Objetivo 1: Suite de Integración 3D Completa

#### Contexto
Herencia de la v2.8.0. Es necesario validar que la exportación de trazas e intervalos proyectados mantiene la integridad topológica en entornos reales de QGIS.

#### Componentes a Implementar
- **[NEW]** [test_3d_integration_advanced.py](file:///home/jmbernales/qgispluginsdev/sec_interp/tests/integration/test_3d_integration_advanced.py): Pruebas con CRS locales y transformaciones complejas.

---

### Objetivo 2: Soporte para Secciones Poligonales (Bent Sections)

#### Contexto
Actualmente, SecInterp asume secciones rectas (un solo segmento). Los proyectos mineros requieren perfiles que sigan túneles o galerías (polilíneas).

#### Componentes a Implementar
- **[MODIFY]** [geometry_processing.py](file:///home/jmbernales/qgispluginsdev/sec_interp/core/utils/geometry/processing.py): Actualizar la lógica de proyección para soportar distancias a lo largo de polilíneas.
- **[MODIFY]** [geology_service.py](file:///home/jmbernales/qgispluginsdev/sec_interp/core/services/geology_service.py): Adaptar la extracción de afloramientos a geometrías multi-segmento.

---

## Verification Plan

### Automated Tests
- **Tests de Integración**: `FORCE_MOCKS=0 uv run python3 -m unittest tests/integration/test_3d_integration_advanced.py`
- **Docker**: `make docker-test`

---

## Estimación de Esfuerzo Total

| Objetivo | Esfuerzo | Prioridad |
|----------|----------|-----------|
| Suite 3D Advanced | 2 días | Alta |
| Bent Section Support | 5 días | Media |
