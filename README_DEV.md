# Entorno de desarrollo para el plugin SecInterp (QGIS)

## Resumen rápido
- Este repositorio es un plugin de QGIS que depende de las librerías internas que QGIS instala (qgis.core, qgis.gui). Esas no se instalan por pip.
- El entorno virtual aquí descrito sirve para tareas de desarrollo y pruebas que no requieren las bindings de QGIS (linting, tests unitarios que no importen qgis, etc.).

## Requisitos del sistema
- Tener instalada una versión de Python 3 (recomendado 3.10 o 3.11). Esto depende de tu distribución y de la versión de QGIS en tu máquina — QGIS 3.x usa Python 3.x (PyQt5).
- Para probar el plugin dentro de QGIS debes ejecutar QGIS (que incluye su propio intérprete con los bindings).

## Crear y activar entorno virtual (Linux / zsh)
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

## Licencia
El proyecto está licenciado bajo GNU GPL v2 o GPL v3 (a elección del usuario). Los textos de licencia completos se incluyen como `LICENSE-GPL-2.0.txt` y `LICENSE-GPL-3.0.txt` y el archivo `LICENSE` contiene la nota de doble-licencia.

## Notas sobre QGIS
- No intentes instalar el paquete `qgis` por pip — las bindings QGIS provienen del instalador de QGIS o del paquete del sistema.
- Para ejecutar y depurar el plugin, carga el plugin desde la carpeta del proyecto en QGIS o instala el plugin en el entorno QGIS apropiado.

## Comandos útiles
- Activar: `source .venv/bin/activate`
- Linting (Ruff): `uv run ruff check .`
- Formateo (Black): `uv run black .`
- Tests: `pytest` (puede requerir adaptación si los tests dependen de QGIS)
- Análisis de calidad: `python analyze_project_optfixed.py`

## Despliegue / `deploy.sh`
El script `deploy.sh` ahora soporta variables de entorno para mayor flexibilidad y seguridad:

- Puedes sobreescribir el destino con `QGIS_PLUGINS_DIR` antes de ejecutar el script, por ejemplo:
  ```bash
  QGIS_PLUGINS_DIR=/ruta/mi/qgis/plugins ./deploy.sh
  ```
- `deploy.sh` crea un backup timestamped del directorio destino si detecta contenido previo (ej.: `/home/usuario/.../sec_interp.bak.20251127123000`).

El script fallará de forma segura si faltan comandos requeridos o si ocurre un error durante la copia.

## Documentación para desarrolladores
Para información detallada sobre arquitectura y guías de desarrollo, consulta:
- [ARCHITECTURE.md](ARCHITECTURE.md) - Arquitectura técnica del plugin
- [DEVELOPMENT_GUIDE.md](DEVELOPMENT_GUIDE.md) - Guía de desarrollo y estándares
- [docs/docsec/CHANGELOG.md](docs/docsec/CHANGELOG.md) - Historial de cambios detallado
