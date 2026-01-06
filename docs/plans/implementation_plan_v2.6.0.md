# Plan de Implementación - Fase v2.6.0 (Zero-External-Deps)

## Objetivo General

Mejorar la calidad y robustez del proyecto SecInterp abordando la deuda técnica crítica, manteniendo la política de **mínimas dependencias externas**. Utilizaremos el framework `unittest` estándar de Python para todas las verificaciones.

---

## User Review Required

> [!IMPORTANT]
> **Política de Dependencias**
>
> Se ha descartado el uso de `pytest-qgis` y `pytest-benchmark`. Toda la lógica de testing de integración y medición de performance se implementará nativamente sobre `unittest` y librerías estándar (`timeit`).

---

## Proposed Changes

### Objetivo 1: Tests de Integración en QGIS Real (Nativo)

#### Contexto
Validar workflows completos de usuario en un entorno QGIS real utilizando `unittest`.

---

#### [NEW] [`tests/integration/BaseIntegrationTest`](file:///home/jmbernales/qgispluginsdev/sec_interp/tests/integration/base_integration.py)

Proveerá una clase base que inicialice `QgsApplication` correctamente para permitir la ejecución de tests que dependan de la API de QGIS sin un entorno gráfico completo (headless).

---

### Objetivo 2: Reducción de Complejidad en Exportadores

#### [MODIFY] [`exporters/interpretation_3d_exporter.py`](file:///home/jmbernales/qgispluginsdev/sec_interp/exporters/interpretation_3d_exporter.py)

Refactorización para aplicar el patrón Strategy, reduciendo la complejidad ciclomática del método `export()`.

---

### Objetivo 3: Benchmarks de Performance Manuales

#### [NEW] [`tests/benchmarks/benchmark_utils.py`](file:///home/jmbernales/qgispluginsdev/sec_interp/tests/benchmarks/benchmark_utils.py)

Implementaremos utilidades simples para medir tiempos de ejecución:
- Decorador `@benchmark` para registrar tiempos.
- Verificación de SLAs directamente en los asserts de los tests.

---

### Objetivo 4: Consolidación de Infraestructura Docker y CI/CD

#### Contexto
Iniciado en la v2.5.0, el entorno Docker debe consolidarse para ser el estandarte de ejecución de los nuevos tests de integración.

#### [MODIFY] [`Dockerfile`](file:///home/jmbernales/qgispluginsdev/sec_interp/Dockerfile) / [`.devcontainer/devcontainer.json`](file:///home/jmbernales/qgispluginsdev/sec_interp/.devcontainer/devcontainer.json)

- Optimizar la imagen para ejecución headless de QGIS.
- Asegurar que todas las dependencias necesarias para `unittest` en entorno QGIS estén presentes.

#### [NEW] [`.github/workflows/main.yml`](file:///home/jmbernales/qgispluginsdev/sec_interp/.github/workflows/main.yml)

- Automatizar la ejecución de la suite completa (`unittest`) dentro del contenedor en cada push/PR.
- Reportar resultados de benchmarks en los logs de la acción.

---

## Verification Plan

### Automated Tests

#### 1. Verificación Total
```bash
PYTHONPATH=. uv run python -m unittest discover tests
```

#### 2. Tests de Integración
```bash
PYTHONPATH=. uv run python -m unittest discover tests/integration
```

#### 3. Benchmarks
```bash
PYTHONPATH=. uv run python -m unittest discover tests/benchmarks
```

---

## Estimación de Esfuerzo

| Objetivo | Esfuerzo | Prioridad |
|----------|----------|-----------|
| Tests de Integración (unittest) | 3 días | Alta |
| Refactorización Exportadores | 1-2 días | Alta |
| Benchmarks Manuales | 2 días | Alta |
| Consolidación Docker/CI | 2 días | Alta |
| **TOTAL** | **8-9 días** | |

---

**Fecha:** 2026-01-05
**Autor:** Juan M. Bernales
**Estado:** Actualizado según política de dependencias.
