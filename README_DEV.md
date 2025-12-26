# Entorno de Desarrollo para el plugin SecInterp (QGIS)

## Resumen Rápido
- Este repositorio es un plugin de QGIS que depende de las librerías internas que QGIS instala (`qgis.core`, `qgis.gui`). Estas no se instalan vía `pip`.
- El entorno virtual sirve para tareas de desarrollo (linting, tests, análisis estático) y se recomienda el uso de `uv` para máxima velocidad y reproducibilidad.

## Requisitos del Sistema
- **Python**: 3.10 o superior (QGIS 3.34+ usa Python 3.12+ en algunas distros).
- **QGIS**: 3.28 LTR o superior instalado en el sistema.
- **uv**: Instalado en el sistema (`curl -LsSf https://astral.sh/uv/install.sh | sh`).

## Configuración del Entorno Virtual (Recomendado)
Para configurar el entorno de desarrollo usando `uv`:

```bash
# Crear entorno y sincronizar dependencias
uv sync

# Activar entorno
source .venv/bin/activate
```

### Framework de Calidad: Pre-commit
Hemos implementado pre-commit hooks para asegurar la calidad del código antes de cada commit.

```bash
# Instalar hooks en tu repositorio local
uv run pre-commit install
```

Los hooks ejecutarán automáticamente:
- **Ruff**: Linting y formateo ultrarrápido.
- **Trailing whitespace**: Limpieza de espacios al final de línea.
- **End of file fixer**: Asegura nueva línea al final de los archivos.
- **YAML/TOML Check**: Validación de sintaxis en archivos de configuración.

## Comandos de Desarrollo
- **Análisis de Calidad**: `uv run python analyze_project_optfixed.py`
  - Genera `PROJECT_SUMMARY.md` y actualiza el historial en `.ai-context/metrics_history.json`.
- **Linting Manual**: `uv run ruff check .`
- **Formateo Manual**: `uv run ruff format .`
- **Tests**: `uv run pytest`

## Despliegue Local (`deploy.sh`)
Usa el script de despliegue para ver los cambios en QGIS:
```bash
./scripts/deploy.sh
```
*Tip: El script detectará automáticamente tu carpeta de plugins de QGIS en Linux y creará backups automáticos.*

## Estándares de Código
1. **Conventional Commits**: Sigue el estándar definido en `docs/docsec/COMMIT_GUIDELINES.md`.
2. **Arquitectura Desacoplada**: No importes GUI en módulos de `core/`.
3. **Documentación**: Usa docstrings estilo Google (Sphinx compatible).

## Documentación de Referencia
- [ARCHITECTURE.md](ARCHITECTURE.md) - Arquitectura técnica unificada.
- [DEVELOPMENT_GUIDE.md](DEVELOPMENT_GUIDE.md) - Guía detallada para desarrolladores.
- [CHANGELOG.md](docs/docsec/CHANGELOG.md) - Historial de versiones y cambios críticos.
- [FEATURE_INTERPRETATION_25D.md](FEATURE_INTERPRETATION_25D.md) - Plan para v2.5.0.

---
**Plugin Version**: 2.4.0 | **Last Update**: 2025-12-25
