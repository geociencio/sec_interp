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
1. **Core**: Crea un método en `PreviewService` (o un nuevo servicio) que procese los datos y devuelva un tipo definido en `core/domain/entities.py`.
2. **GUI Manager**: Actualiza `PreviewManager` para llamar al nuevo servicio y almacenar el resultado en `cached_data`. Actualiza el cálculo del hash si los datos dependen de nuevos parámetros.
3. **Renderer**: Actualiza `PreviewRenderer` y `PreviewLayerFactory` para crear la nueva capa de visualización y aplicarle simbología.

## 📈 Rendimiento y Caché
- **Caché por Hash**: Si añades parámetros al diálogo, inclúyelos en `PreviewManager._calculate_params_hash()`.
- **Simplificación**: Implementa LOD si la funcionalidad implica procesar miles de geometrías.
- **Indexación Espacial**: Usa siempre `QgsSpatialIndex` cuando necesites filtrar capas vectoriales por proximidad.

## 🔄 Flujos de Trabajo (Recomendado)

### 🧪 Ejecución de Tests
El proyecto utiliza `unittest`. Para ejecutar los tests correctamente y resolver el paquete `sec_interp`, usa el siguiente comando desde la raíz:

```bash
PYTHONPATH=.. uv run python3 -m unittest discover sec_interp/tests
```

**Nota**: No uses `pytest`. Asegúrate de incluir `PYTHONPATH=..` para que las importaciones funcionen correctamente.

### 💾 Commits Limpios
Para evitar conflictos con los hooks de pre-commit (que pueden reformatear código y fallar el commit), se recomienda seguir este orden:

1. **Formateo Previo**:
   ```bash
   uv run ruff check --fix .
   uv run ruff format .
   ```
2. **Commit**:
   ```bash
   git add .
   git commit -m "tipo: descripción"
   ```

## 🧹 Calidad de Código
- **Pre-commit**: Instala con `uv run pre-commit install`. Los checks se ejecutan en cada commit.
- **Linting**: Ejecuta `uv run ruff check .` para validar estándares.
- **Análisis de Métricas**: Ejecuta `uv run ai-ctx analyze .` habitualmente para controlar la complejidad.
- **Auditoría QGIS**: Usa `uv run qgis-analyzer analyze .` para validaciones reglamentarias de QGIS.
- Sigue las convenciones de [COMMIT_GUIDELINES.md](../standards/COMMIT_GUIDELINES.md) (Conventional Commits).
- **Importante**: Intenta corregir los errores de pre-commit en lugar de saltártelos. Usa `--no-verify` solo si es absolutamente necesario y temporal.
- Mantén una complejidad ciclomática por función inferior a 15 siempre que sea posible.

---
**Version**: 2.9.0 | **Ref**: [README_DEV.md](README_DEV.md)
