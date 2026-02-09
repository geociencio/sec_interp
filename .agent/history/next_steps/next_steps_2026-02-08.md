# Proximos Pasos - SecInterp

## 🎯 Objetivo Inmediato
Consolidar la calidad del código tras la habilitación de reglas estrictas de Ruff y corregir los 686 problemas pendientes (docstrings, magic values, complejidad).

## 🛠️ Acciones Pendientes
1. **Corrección Masiva de Docstrings**:
   - Priorizar módulos de `gui/ui/pages/` que carecen totalmente de documentación.
   - Usar el estándar Google Docstrings.
2. **Refactorización de Valores Mágicos (`PLR2004`)**:
   - Extraer constantes en `gui/preview_layer_factory.py` y `gui/tools/interpretation_tool.py`.
3. **Optimización de Firmas de Funciones (`PLR0913`)**:
   - Evaluar el uso de dataclasses para agrupaer parámetros en métodos con más de 5 argumentos.

## 🐛 Bugs del Analizador
- Se debe asegurar que el parche aplicado localmente a `.venv/lib/python3.14/site-packages/analyzer/engine.py` (cambiando `--format` por `--output-format`) se reporte o se mantenga si se reinstala el entorno.
- Revisar `docs/dev/qgis_analyzer_issues.md` para detalles técnicos.

## 🚀 Comando para retomar
```bash
/inicia-sesion
```
