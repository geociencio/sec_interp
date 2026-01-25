# Plan de Implementación - Fase v2.9.0 (Análisis Avanzado y Geometría)

## Objetivo General
Evolucionar las capacidades geométricas de SecInterp para soportar perfiles no lineales (polilíneas/túneles) y consolidar la suite de verificación 3D iniciada en la v2.8.0.

---

## Proposed Changes

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
