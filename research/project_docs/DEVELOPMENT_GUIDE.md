# Guía de Desarrollo de SecInterp

Este documento proporciona directrices para extender y mantener el plugin SecInterp siguiendo la nueva arquitectura desacoplada.

## 🛠️ Entorno de Desarrollo
- **Python**: 3.9+
- **QGIS**: 3.28 LTR o superior.
- **Gestor de Paquetes**: se prefiere el uso de `uv` para la gestión de dependencias y scripts de análisis.

## 📐 Principios de Diseño
1. **Separación Core/GUI**: Nunca importes `PyQt5`, `PyQt6` o `qgis.gui` dentro de `core/`. Si necesitas tipos de datos específicos de QGIS, usa `qgis.core`.
2. **Servicios Especializados**: Toda lógica de negocio pesada debe residir en un servicio dentro de `core/services/`.
3. **Managers de UI**: El `MainDialog` debe delegar responsabilidades a clases Manager (ej. `PreviewManager`, `DialogToolManager`).
4. **Puras Geometrías**: Utiliza `core/utils/geometry.py` (y sus subgrupos) para operaciones espaciales comunes.

## 🧪 Añadiendo una Nueva Funcionalidad
Si deseas añadir un nuevo tipo de previsualización:
1. **Core**: Crea un método en `PreviewService` (o un nuevo servicio) que procese los datos y devuelva un tipo definido en `core/types.py`.
2. **GUI Manager**: Actualiza `PreviewManager` para llamar al nuevo servicio y almacenar el resultado en `cached_data`. Actualiza el cálculo del hash si los datos dependen de nuevos parámetros.
3. **Renderer**: Actualiza `PreviewRenderer` y `PreviewLayerFactory` para crear la nueva capa de visualización y aplicarle simbología.

## 📈 Rendimiento y Caché
- **Caché por Hash**: Si añades parámetros al diálogo, inclúyelos en `PreviewManager._calculate_params_hash()`.
- **Simplificación**: Implementa LOD si la funcionalidad implica procesar miles de geometrías.
- **Indexación Espacial**: Usa siempre `QgsSpatialIndex` cuando necesites filtrar capas vectoriales por proximidad.

## 🧹 Calidad de Código
- **Pre-commit**: Instala con `uv run pre-commit install`. Los checks se ejecutan en cada commit.
- **Linting**: Ejecuta `uv run ruff check .` para validar estándares.
- **Análisis**: Usa `uv run qgis-analyzer analyze .` para obtener un informe de calidad y evolucion de métricas.
- Sigue las convenciones de [COMMIT_GUIDELINES.md](../standards/COMMIT_GUIDELINES.md) (Conventional Commits).
- **Importante**: Realizar siempre los commits con el flag `--no-verify` para evitar errores de configuración en los pre-commit hooks locales.
- Mantén una complejidad ciclomática por función inferior a 15 siempre que sea posible.

---
**Version**: 2.5.0 | **Ref**: [README_DEV.md](README_DEV.md)
