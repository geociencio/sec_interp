# Próximos Pasos - Post v2.9.0

**Fecha de Creación:** 2026-02-01
**Última Fase Completada:** v2.9.0 - Consolidación Arquitectónica

---

## 🔴 Deuda Técnica Crítica (Prioridad 1)

### 1. Eliminar Importación Legacy de PyQt5
- **Archivo**: `resources/resources.py`
- **Problema**: `from PyQt5 import QtCore` (debe ser `from qgis.PyQt import QtCore`)
- **Impacto**: Bloqueará migración a QGIS 4.x
- **Estimación**: 1-2 horas

### 2. Preparación para QGIS 4.x
- **Objetivo**: Auditar APIs deprecadas y crear plan de migración
- **Estimación**: 1 sprint

---

## 🟡 Mejoras de Calidad (Prioridad 2)

### 3. Reducir Complejidad en export_service.py
- **Objetivo**: CC < 10 en todos los métodos 3D
- **Estimación**: 4-6 horas

### 4. Mejorar Cobertura de Documentación
- **Estado Actual**: 75.9% docstrings
- **Objetivo**: 85%
- **Estimación**: 3-4 horas

### 5. Implementar Optimizaciones (24 identificadas)
- **Fuente**: `ai-ctx analyze`
- **Estimación**: 1 sprint

---

## 🟢 Mantenibilidad (Prioridad 3)

### 6. Migrar MD5 a SHA256 para Cache Keys
- **Estimación**: 1 hora

### 7. Completar Traducciones (49 strings)
- **Estimación**: 2-3 horas

### 8. Ampliar Suite de Tests
- **Estimación**: 1 sprint

---

## 📊 Métricas de Referencia (v2.9.0)

```
Quality Score:        54.3/100 (+9 pts)
Total Lines:          8,975
Tests Passing:        199/199 (100%)
Docstring Coverage:   75.9%
```

---

## 🚀 Comando para Retomar

```bash
/inicia-sesion
```

**Referencia Completa**: Ver [Phase Closure Document](../docs/maintenance/phase_closure_v2.9.0.md)
