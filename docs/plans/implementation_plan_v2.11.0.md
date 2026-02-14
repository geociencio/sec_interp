# Plan de Implementación - Fase v2.11.0 (QGIS 4.x & 3D Engine PREVIEW)

## Objetivo General
Lograr la **compatibilidad total con QGIS 4.x** (eliminación de dependencias de `PyQt5`) y establecer el **Motor de Previsualización 3D** (Preview3DEngine) diseñado en la fase anterior.

---

## Estructura de Objetivos

### Objetivo 1: Migración a QGIS 4.x / API Agnostic
#### Contexto
Preparar el plugin para el futuro QGIS 4.0 eliminando importaciones directas de `PyQt5` y usando `qgis.PyQt` shim exclusivamente.

#### Targets Específicos
- **Global**: Reemplazar `from PyQt5...` por `from qgis.PyQt...` en todo el repositorio.
- **Resources**: Actualizar `resources.py` (y el compilador de recursos) para ser compatible.
- **CI/CD**: Añadir job de verificación de imports prohibidos (usando `grep` o `pylint`).

### Objetivo 2: Preview 3D Engine (Fase 1)
#### Contexto
Implementar el motor de visualización 3D real, aprovechando la preparación de datos realizada en v2.10.0.

#### Targets Específicos
- **Engine**: Implementar `core/engines/preview_3d_engine.py` para proyectar el espacio 3D en la vista 2D.
- **UI**: Integrar widget 3D (o vista 2D con proyección) en la pestaña de preview.
- **Sync**: Sincronizar vista 2D (Perfil) y 3D (Espacio).

### Objetivo 3: Mantenimiento y Calidad
#### Contexto
Mantener el Quality Score > 60 y cobertura de tests > 80%.

---

## Verification Plan

### 1. Compatibilidad API
```bash
# Verificar que no existen imports de PyQt5 directos
grep -r "from PyQt5" . --exclude-dir=venv --exclude-dir=.git
```

### 2. Estabilidad 3D
```bash
make docker-test
# Verificar tests de integración de motores 3D
```

## Estimación de Esfuerzo
| Objetivo | Esfuerzo | Prioridad |
|----------|----------|-----------|
| Migración QGIS 4.x | 4 horas | Alta |
| Preview 3D Engine | 12 horas | Alta |
| Calidad | 2 horas | Media |

**Total fase**: ~2-3 días
