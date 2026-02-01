# Entorno de Desarrollo para el plugin SecInterp (QGIS)

## Resumen Rápido
- Este repositorio es un plugin de QGIS que depende de las librerías internas que QGIS instala (`qgis.core`, `qgis.gui`). Estas no se instalan vía `pip`.
- El entorno virtual sirve para tareas de desarrollo (linting, tests, análisis estático) y se recomienda el uso de `uv` para máxima velocidad y reproducibilidad.

## Requisitos del Sistema
- **Python**: 3.10 o superior (QGIS 3.34+ usa Python 3.12+ en algunas distros).
- **QGIS**: 3.28 LTR o superior instalado en el sistema.
- **uv**: Instalado en el sistema (`curl -LsSf https://astral.sh/uv/install.sh | sh`).

Para configurar el entorno de desarrollo usando `uv` (recomendado):

```bash
# Sincronizar dependencias desde pyproject.toml (incluye grupo dev)
uv sync

# Activar el entorno virtual creado automáticamente
source .venv/bin/activate
```

Si prefieres usar `pip` tradicional (aunque se recomienda `uv`), puedes instalarlo con:

```bash
uv pip install -e ".[dev]"
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
- **Métricas de Calidad (Higiene)**: `uv run ai-ctx analyze .`
  - Recomendado para mantenimiento diario y control de complejidad ciclomática.
- **Auditoría de QGIS (Compliance)**: `uv run qgis-analyzer analyze .`
  - Específico para validar estándares de la comunidad QGIS (i18n, threading, metadatos).
- **Linting Manual**: `uv run ruff check .`
- **Formateo Manual**: `uv run ruff format .`
- **Tests**: `uv run pytest`

## Despliegue Local (`qgis-manage`)
Usa la nueva herramienta CLI para desplegar tus cambios en QGIS:
```bash
# Despliegue rápido con backup automático
uv run qgis-manage deploy
```
*Tip: El comando detecta automáticamente tu sistema operativo y realiza backups de seguridad.*

## Estándares de Código
1. **Conventional Commits**: Sigue el estándar definido en `docs/docsec/COMMIT_GUIDELINES.md`.
2. **Arquitectura Desacoplada**: No importes GUI en módulos de `core/`.
3. **Documentación**: Usa docstrings estilo Google (Sphinx compatible).

## Documentación de Referencia
- [ARCHITECTURE.md](ARCHITECTURE.md) - Arquitectura técnica unificada.
- [DEVELOPMENT_GUIDE.md](DEVELOPMENT_GUIDE.md) - Guía detallada para desarrolladores.
- [CHANGELOG.md](docs/docsec/CHANGELOG.md) - Historial de versiones y cambios críticos.
- [FEATURE_INTERPRETATION_25D.md](FEATURE_INTERPRETATION_25D.md) - Plan para v2.5.0.
- [UV_MODERNIZATION_GUIDE.md](docs/maintainer/uv_modernization_guide.md) - Guía de modernización de plugins con `uv`.

---
**Plugin Version**: 2.5.0 | **Last Update**: 2026-01-01
