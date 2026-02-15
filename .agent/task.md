# Tareas - Fase v3.0.1 (Limpieza de Linting)

## 🛠️ Corrección de Issues de Linting (v3.0.1) <!-- id: 1 -->
**Contexto**: QGIS Security Scan reportó 85 issues de linting. Se ha alcanzado el 100% de cumplimiento en Docstrings y Constantes.

- [x] Corregir imports faltantes (F821 - 65 issues) <!-- id: 40 -->
- [x] Ajustar line breaks antes de operadores binarios (W503 - 15 issues) <!-- id: 41 -->
- [x] Reorganizar imports de módulos (E402 - 3 issues) <!-- id: 42 -->
- [x] Eliminar variables no usadas (F841 - 2 issues) <!-- id: 43 -->
- [x] Cobertura del 100% de Docstrings y eliminación de números mágicos (PLR2004) <!-- id: 44 -->
- [ ] Migrar imports de `PyQt5` a `qgis.PyQt` (4 ocurrencias) <!-- id: 50 -->
- [ ] Corregir fugas de señales en `core/controller.py` (66 ocurrencias) <!-- id: 51 -->
- [ ] Completar docstrings faltantes en `resources/` y `tests/` (406 issues) <!-- id: 52 -->
- [ ] Integrar `qgis-analyzer` v1.9.0 en sistema agéntico (Skills/Workflows) <!-- id: 53 -->

> [!NOTE]
> Tests passed successfully in Docker environment (Green State). Starting session with clean baseline.

## 🚀 Migración a QGIS 4.x / API Agnostic <!-- id: 2 -->
- [ ] Reemplazar `from PyQt5...` por `from qgis.PyQt...` (Global) <!-- id: 3 -->
- [ ] Actualizar `resources.py` y compilador de recursos <!-- id: 4 -->
- [ ] Añadir job de CI/CD para verificar imports prohibidos <!-- id: 5 -->

## 🔮 Preview 3D Engine (Fase 1) <!-- id: 6 -->
- [ ] Implementar `core/engines/preview_3d_engine.py` <!-- id: 7 -->
- [ ] Integrar widget 3D en la pestaña de preview <!-- id: 8 -->
- [ ] Sincronizar vista 2D (Perfil) y 3D (Espacio) <!-- id: 9 -->
