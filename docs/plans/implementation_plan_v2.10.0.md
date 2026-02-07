# Plan de Implementación - Fase v2.10.0 (Calidad y QGIS 4.x)

## Objetivo General
Elevar el **Quality Score** del proyecto por encima de 60 (+6 ptos) y preparar la base de código para la migración a **QGIS 4.x**, resolviendo deuda técnica crítica heredada de la fase v2.9.0.

---

## User Review Required

> [!IMPORTANT]
> **Compatibilidad QGIS 4.x**
>
> Se eliminará el soporte heredado para PyQt5 directo. Todos los imports se estandarizarán a `qgis.PyQt`. Esto es un cambio interno transparente pero crítico para el futuro.

---

## Estructura de Objetivos

### Objetivo 1: Eliminación de Deuda Técnica Crítica (QGIS 4.x)

#### Contexto
La importación directa de `PyQt5` en `resources.py` bloqueará la ejecución en QGIS 4.x (que usará Qt6).

#### Cambios
##### [MODIFY] [resources.py](file:///home/jmbernales/qgispluginsdev/sec_interp/resources/resources.py)
- Reemplazar `from PyQt5 import QtCore` por `from qgis.PyQt import QtCore`.
- Actualizar script de generación de recursos si es necesario.

### Objetivo 2: Reducción de Complejidad Ciclomática (ExportService)

#### Contexto
`ExportService` contiene métodos 3D con alta complejidad ciclomática (>10) que dificultan el mantenimiento y bajan el Quality Score.

#### Cambios
##### [MODIFY] [export_service.py](file:///home/jmbernales/qgispluginsdev/sec_interp/core/services/export_service.py)
- Extraer lógica de exportación 3D a clases helper dedicadas.
- Aplicar patrón Strategy para formatos de exportación complejos.

### Objetivo 3: Optimizaciones de Rendimiento y Calidad

#### Contexto
`ai-ctx` ha identificado 24 oportunidades de optimización y el coverage de docstrings está en 75.9% (meta 85%).

#### Cambios
- Implementar las 24 optimizaciones sugeridas por `ai-ctx`.
- Completar docstrings faltantes en módulos `core`.
- Estandarizar type hints en utilerías.

---

## Verification Plan

### 1. Compatibilidad QGIS
```bash
# Verificar que no quedan imports directos de PyQt5
grep -r "from PyQt5" .
```

### 2. Calidad de Código
```bash
# Verificar aumento de Quality Score
uv run ai-ctx analyze --path .
# Baseline actual: 58.5
# Meta: > 60.0 (+1.5 ptos)
```

### 3. Estabilidad
```bash
make docker-test
# Meta: 199 tests pasando
```

---

## Estimación de Esfuerzo

| Objetivo | Esfuerzo | Prioridad |
|----------|----------|-----------|
| Deuda Técnica (PyQt5) | 2 horas | Alta |
| Complejidad (ExportService) | 4 horas | Media |
| Optimizaciones y Docs | 3 horas | Media |

**Total fase**: ~1-2 días
