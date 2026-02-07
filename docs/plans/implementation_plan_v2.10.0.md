# Plan de Implementación - Fase v2.10.0 (Calidad y Preparación 3D)

## Objetivo General
Realizar una **reducción masiva de Complejidad Ciclomática (CC)** en los módulos core (`services`, `exporters`, `utils`) para estabilizar el sistema y preparar la arquitectura para futuras implementaciones de **renderizado y preview 3D nativo**.

---

## Estructura de Objetivos

### Objetivo 1: Reducción Masiva de Complejidad (CC >= 9)

#### Contexto
Se han identificado 8 métodos críticos con complejidad ciclomática superior a 9 que degradan la mantenibilidad.

#### Targets Específicos
- **`core/domain/dtos.py`**: `get_elevation_range` (CC=12)
- **`core/validation/validation_helpers.py`**: `validate_reasonable_ranges` (CC=11)
- **`exporters/drillhole_3d_exporter.py`**: `export` (CC=10)
- **`gui/main_dialog_export.py`**: `export_preview` (CC=10)
- **`gui/preview_renderer.py`**: `render` (CC=10)
- **`core/services/export_service.py`**: `export_data` (CC=9)
- **`core/utils/drillhole.py`**: `calculate_drillhole_trajectory` (CC=9)
- **`core/validation/layer_validator.py`**: `validate_structural_requirements` (CC=9)

#### Cambios Propuestos
- Fragmentar métodos monolíticos aplicando el principio de Responsabilidad Única (SRP).
- Extraer validaciones y transformaciones geométricas a utilerías puras.
- Implementar el patrón **Command** o **Strategy** en los exporters para simplificar la toma de decisiones.

### Objetivo 2: Preparación Arquitectónica para Preview 3D

#### Contexto
El sistema actual está optimizado para 2D. Se requiere desacoplar aún más la lógica de proyección para permitir vistas 3D reales.

#### Cambios Propuestos
- **Core Entities**: Extender `DomainGeometry` para soportar metadatos de rendering 3D.
- **Interfaces**: Definir contratos para un futuro `Preview3DEngine`.
- **Decoupling**: Asegurar que ningún servicio core dependa de widgets 2D de QGIS.

### Objetivo 3: Optimización y Documentación (Calidad > 60)

#### Contexto
Mantener la meta de elevar el Quality Score por encima de 60 (+1.5 ptos).

#### Cambios
- Implementar optimizaciones sugeridas por `ai-ctx`.
- Alcanzar el 85% de cobertura de docstrings en el paquete `core`.
- Estandarizar el uso de `pathlib` y `typing` en todo el repositorio.

---

## Verification Plan

### 1. Calidad de Código
```bash
# Verificar reducción de CC y aumento de Quality Score
uv run ai-ctx analyze --path . --complexity 10
# Meta: Quality Score > 60.0
# Meta: Métodos con CC > 10 reducidos en un 50%
```

### 2. Estabilidad
```bash
make docker-test
# Meta: 199 tests pasando (o nuevos si se agregan)
```

---

## Monitoreo y Futuro
- **Compatibilidad QGIS 4.x**: Se abordará cuando el compilador de recursos se actualice para Qt6/QGIS 4.x.

## Estimación de Esfuerzo

| Objetivo | Esfuerzo | Prioridad |
|----------|----------|-----------|
| Reducción Masiva CC | 8 horas | Alta |
| Preparación 3D | 4 horas | Media |
| Calidad y Docs | 4 horas | Media |

**Total fase**: ~2-3 días

**Total fase**: ~1-2 días
