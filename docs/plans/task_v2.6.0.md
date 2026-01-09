# Planificación Fase v2.6.0 - SecInterp

## Objetivo General
Mejorar la calidad, robustez y mantenibilidad del proyecto abordando la deuda técnica crítica y moderada identificada en el cierre de fase v2.5.0.

## Tareas

### 1. Análisis y Priorización
- [x] Revisar deuda técnica del cierre de fase
- [x] Definir alcance de la fase v2.6.0
- [x] Estimar esfuerzo por tarea
- [x] Crear roadmap detallado

### 2. Tests de Integración (Crítico - 2-3 días) 🔴
- [x] **Setup Inicial**
  - [x] Implementar `BaseIntegrationTest` en `tests/integration/base_integration.py`
  - [x] Configurar inicialización de `QgsApplication` para tests
- [x] **Implementar Tests de Workflows (unittest)**
  - [x] `test_interpretation_workflow.py`
  - [x] `test_measurement_workflow.py`
  - [x] `test_export_workflow.py`
- [x] **Integración CI/CD**
  - [x] Ajustar workflow de GitHub Actions para correr `unittest` en entorno QGIS (Docker)

### 3. Reducción de Complejidad en Exportadores (Crítico - Completado) ✅
- [x] **Análisis Inicial**
  - [x] Ejecutar `ruff check --select C901`
- [x] **Diseño de Refactorización**
  - [x] Refactorizar mediante métodos privados (CC <= 5 alcanzado)
- [x] **Implementación**
  - [x] Refactorizar `interpretation_3d_exporter.export()`
- [x] **Verificación**
  - [x] Ejecutar `python -m unittest`

### 4. Benchmarks de Performance (Crítico - Completado) ✅
- [x] **Utilidades de Benchmark**
  - [x] Crear `tests/benchmarks/benchmark_utils.py` con decoradores de tiempo
- [x] **Implementar Benchmarks (unittest)**
  - [x] `test_geometry_benchmarks.py`
  - [x] `test_export_benchmarks.py`

### 5. Consolidación Docker y CI/CD (Crítico - Completado) ✅
- [x] **Optimización de Imagen**
  - [x] Refinar `Dockerfile` para ejecución headless estable
  - [x] Verificar `PYTHONPATH` definitivo en el contenedor
- [x] **Automatización CI/CD**
  - [x] Configurar GitHub Action para ejecutar `unittest discover` dentro de Docker
  - [x] Implementar captura de resultados y logs técnicos

### 5. Documentación de API (Moderado - POSPUESTO a v2.7.0) 🟡
- [ ] Configurar Sphinx
- [ ] Completar docstrings faltantes
- [ ] Generar documentación automática
- [ ] Publicar en GitHub Pages

### 6. Centralización de Logging (Moderado - POSPUESTO a v2.7.0) 🟡
- [ ] Auditar configuración actual
- [ ] Centralizar en `logger_config.py`
- [ ] Implementar niveles configurables
- [ ] Documentar uso

### 7. Validación de Schemas (Moderado - POSPUESTO a v2.7.0) 🟡
- [ ] Evaluar Pydantic vs alternativas
- [ ] Diseñar models para drillhole JSON
- [ ] Implementar validación
- [ ] Agregar tests

### 8. Limpieza de Código (Menor - POSPUESTO a v2.7.0) 🟢
- [ ] Extraer clase base `BaseExporter`
- [ ] Refactorizar nombres inconsistentes
- [ ] Limpiar imports en research/

---

## Notas de Implementación

### Prioridad de Ejecución
1. **Primero:** Tests de Integración (desbloquea validación de workflows)
2. **Segundo:** Reducción de Complejidad (mejora mantenibilidad)
3. **Tercero:** Benchmarks (establece baseline para futuro)

### Riesgos Identificados
- ⚠️ Configuración de `qgis_testrunner` puede ser compleja
- ⚠️ Refactorización puede introducir regresiones
- ⚠️ Benchmarks pueden ser inconsistentes en CI

### Criterios de Éxito
- ✅ 10+ tests de integración pasando
- ✅ Complejidad ciclomática < 10 en todos los exportadores
- ✅ Suite de benchmarks con SLAs definidos
- ✅ Todos los tests unitarios existentes siguen pasando
