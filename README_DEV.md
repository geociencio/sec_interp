```markdown
# Entorno de desarrollo para el plugin SecInterp (QGIS)

Resumen rápido
- Este repositorio es un plugin de QGIS que depende de las librerías internas que QGIS instala (qgis.core, qgis.gui). Esas no se instalan por pip.
- El entorno virtual aquí descrito sirve para tareas de desarrollo y pruebas que no requieren las bindings de QGIS (linting, tests unitarios que no importen qgis, etc.).

Requisitos del sistema
- Tener instalada una versión de Python 3 (recomendado 3.10 o 3.11). Esto depende de tu distribución y de la versión de QGIS en tu máquina — QGIS 3.x usa Python 3.x (PyQt5).
- Para probar el plugin dentro de QGIS debes ejecutar QGIS (que incluye su propio intérprete con los bindings).

Crear y activar entorno virtual (Linux / zsh)
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

Licencia
-------
El proyecto está licenciado bajo GNU GPL v2 o GPL v3 (a elección del usuario). Los textos de licencia completos se incluyen como `LICENSE-GPL-2.0.txt` y `LICENSE-GPL-3.0.txt` y el archivo `LICENSE` contiene la nota de doble-licencia.

Notas sobre QGIS
- No intentes instalar el paquete `qgis` por pip — las bindings QGIS provienen del instalador de QGIS o del paquete del sistema.
- Para ejecutar y depurar el plugin, carga el plugin desde la carpeta del proyecto en QGIS o instala el plugin en el entorno QGIS apropiado.

Comandos útiles
- Activar: `source .venv/bin/activate`
- Linting (Black + isort + flake8): `black . && isort . && flake8` (instalar deps dev)
- Tests: `pytest` (puede requerir adaptación si los tests dependen de QGIS)

```
# Entorno de desarrollo para el plugin SecInterp (QGIS)

Resumen rápido
- Este repositorio es un plugin de QGIS que depende de las librerías internas que QGIS instala (qgis.core, qgis.gui). Esas no se instalan por pip.
- El entorno virtual aquí descrito sirve para tareas de desarrollo y pruebas que no requieren las bindings de QGIS (linting, tests unitarios que no importen qgis, etc.).

Requisitos del sistema
- Tener instalada una versión de Python 3 (recomendado 3.10 o 3.11). Esto depende de tu distribución y de la versión de QGIS en tu máquina — QGIS 3.x usa Python 3.x (PyQt5).
- Para probar el plugin dentro de QGIS debes ejecutar QGIS (que incluye su propio intérprete con los bindings).

Crear y activar entorno virtual (Linux / zsh)
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

Notas sobre QGIS
- No intentes instalar el paquete `qgis` por pip — las bindings QGIS provienen del instalador de QGIS o del paquete del sistema.
- Para ejecutar y depurar el plugin, carga el plugin desde la carpeta del proyecto en QGIS o instala el plugin en el entorno QGIS apropiado.

Comandos útiles
- Activar: `source .venv/bin/activate`
- Linting (Black + isort + flake8): `black . && isort . && flake8` (instalar deps dev)
- Tests: `pytest` (puede requerir adaptación si los tests dependen de QGIS)
