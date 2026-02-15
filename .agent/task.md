# Tareas - Fase v3.0.1 (Limpieza de Linting)

## 🛠️ Corrección de Issues de Linting (v3.0.1) <!-- id: 1 -->
**Contexto**: QGIS Security Scan reportó 85 issues de linting que no afectan funcionalidad pero deben corregirse para mantener calidad del código.

- [ ] Corregir imports faltantes (F821 - 65 issues) <!-- id: 40 -->
  - `core/interfaces/drillhole_interface.py`: Añadir `from typing import Any`
  - `core/interfaces/structure_interface.py`: Añadir `from qgis.core import QgsGeometry`
  - `core/services/drillhole/*.py`: Añadir `from qgis.core import QgsFeature`
- [ ] Ajustar line breaks antes de operadores binarios (W503 - 15 issues) <!-- id: 41 -->
  - `core/domain/dtos.py`: Reformatear expresiones multi-línea
- [ ] Reorganizar imports de módulos (E402 - 3 issues) <!-- id: 42 -->
  - `core/performance_metrics.py`: Mover imports al inicio del archivo
- [ ] Eliminar variables no usadas (F841 - 2 issues) <!-- id: 43 -->
  - `core/performance_metrics.py`: Remover variable `_current`

## 🚀 Migración a QGIS 4.x / API Agnostic <!-- id: 2 -->
- [ ] Reemplazar `from PyQt5...` por `from qgis.PyQt...` (Global) <!-- id: 3 -->
- [ ] Actualizar `resources.py` y compilador de recursos <!-- id: 4 -->
- [ ] Añadir job de CI/CD para verificar imports prohibidos <!-- id: 5 -->

## 🔮 Preview 3D Engine (Fase 1) <!-- id: 6 -->
- [ ] Implementar `core/engines/preview_3d_engine.py` <!-- id: 7 -->
- [ ] Integrar widget 3D en la pestaña de preview <!-- id: 8 -->
- [ ] Sincronizar vista 2D (Perfil) y 3D (Espacio) <!-- id: 9 -->
