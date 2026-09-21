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
- **Tests (unittest)**: `PYTHONPATH=.. uv run python3 -m unittest discover tests`
- **Tests (Docker, QGIS real)**: `make docker-test`

## Despliegue Local (`qgis-manage`)
Usa la herramienta CLI para desplegar tus cambios en QGIS (soporta QGIS 3 y 4):
```bash
# Despliegue rápido con backup automático (por defecto QGIS 3)
uv run qgis-manage deploy

# Despliegue para QGIS 4
uv run qgis-manage deploy --qgis-version 4
```
*Tip: El comando detecta automáticamente tu sistema operativo, gestiona perfiles y realiza backups de seguridad.*

## 📚 Generación de Documentación

La documentación se genera con **Sphinx** (MyST Markdown) y se publica en un **repositorio separado** (GitHub Pages). El proceso completo está en **[`docs/DOCUMENTATION_PROCESS.md`](docs/DOCUMENTATION_PROCESS.md)**.

**Requisitos**: `uv sync` (dev deps: `sphinx`, `sphinx-rtd-theme`, `sphinxcontrib-mermaid`, `myst-parser`, `sphinx-intl`) y `gettext` (`msgfmt`).

**Comando**:
```bash
make docs                       # build + export + publicar (equivale a ./scripts/build_docs.sh)
./scripts/build_docs.sh [DIR]   # DIR por defecto: ../sec_interp_docs
```

**Pipeline (`scripts/build_docs.sh`)**:
1. `sphinx-apidoc` regenera los stubs autodoc en `docs/source/` — **una página por módulo `.py`** del plugin (`core/`, `gui/`, `exporters/`, `plugin/`, `resources/` y raíz). Excluye `tests/`, `scripts/`, `docs/`, `help/` y `build/`.
2. Sincroniza versión/fecha de los headers (`scripts/sync_docs_version.py`, desde `metadata.txt`).
3. Compila los catálogos `.po` → `.mo` (`scripts/i18n/translate_docs.py compile`).
4. `sphinx-build -j auto` genera HTML para la unión de idiomas.
5. Publica solo `DOCS_LOCALES` (default **`en es`**) en `../sec_interp_docs/<lang>/`.
6. Sincroniza el manual offline `help/html/<lang>` para `DOCS_HELP_LOCALES` (todos los idiomas de la UI).
7. Si `../sec_interp_docs/.git` existe → `git commit` (`docs: auto-build from sec_interp@<hash>`) + `git push origin main`.

**Política de idiomas**: un idioma entra al sitio web solo cuando su `USER_GUIDE.po` alcanza **≥80%** (ver [`docs/DOCS_STYLE_GUIDE.md`](docs/DOCS_STYLE_GUIDE.md)). La ayuda offline mantiene todos los idiomas de la UI.

**Comandos de documentación**:

| Comando | Propósito |
|---|---|
| `make docs` | Build + export + publicar |
| `make docs-check` | Falla ante refs a módulos inexistentes, enlaces roto o espejos desincronizados |
| `make docs-version` | Sincroniza versión/fecha desde `metadata.txt` |
| `make docs-i18n` | Cobertura de traducción por idioma (`--min N` para exigir umbral) |
| `make docs-i18n-update` | Extrae `.pot` + `sphinx-intl update` (catálogos user-facing) |
| `bash scripts/sync_docs_mirrors.sh [--check]` | Espejos `docs/` ↔ `docs/source/` |
| `bash scripts/sync_vault_mirrors.sh [--check]` | Espejos de las bóvedas Obsidian |

**Repositorio de docs**:

| Elemento | Valor |
|---|---|
| Salida local | `../sec_interp_docs` → `/home/jmbernales/qgispluginsdev/sec_interp_docs/` |
| Remoto | `https://github.com/geociencio/sec_interp_docs.git` (branch `main`) |
| GitHub Pages | https://geociencio.github.io/sec_interp_docs/ |

> [!warning] Efectos secundarios
> - `make docs` regenera los stubs `.rst` **rastreados** en `docs/source/` (deja el árbol sucio; revísalos/commitéalos).
> - El paso 7 **hace `git push`** al repo externo de docs; no hay flag para omitirlo. Para construir sin publicar, ejecuta los pasos 1-6 manualmente.
> - `sphinx-apidoc --force` **no borra** stubs de módulos eliminados: si hay warnings de módulos inexistentes, elimina los `.rst` huérfanos en `docs/source/`.

> [!tip] Nota de shell (zsh)
> El bucle de idiomas del script asume `bash`. Si lo replicas por partes en **zsh**, usa un array (`LOCALES=(en es fr …)`) o `bash -c`, porque zsh no divide por espacios una variable escalar.

## Estándares de Código
1. **Conventional Commits**: Sigue el estándar definido en `docs/docsec/COMMIT_GUIDELINES.md`.
2. **Arquitectura Desacoplada**: No importes GUI en módulos de `core/`.
3. **Documentación**: Usa docstrings estilo Google (Sphinx compatible).

## Documentación de Referencia
- [docs/DOCS_INDEX.md](docs/DOCS_INDEX.md) — Índice (mapa de canónicos y tooling).
- [docs/DOCUMENTATION_PROCESS.md](docs/DOCUMENTATION_PROCESS.md) — Proceso de generación/publicación.
- [docs/DOCS_STYLE_GUIDE.md](docs/DOCS_STYLE_GUIDE.md) — Guía de estilo (MyST, enlaces, duplicados, i18n).
- [docs/USER_GUIDE_CONVENTIONS.md](docs/USER_GUIDE_CONVENTIONS.md) — Convenciones e imágenes del User Guide.
- [docs/ARCHITECTURE_EN.md](docs/ARCHITECTURE_EN.md) — Arquitectura técnica unificada.
- [docs/docsec/DEVELOPMENT_GUIDE.md](docs/docsec/DEVELOPMENT_GUIDE.md) — Guía para desarrolladores.
- [docs/CHANGELOG.md](docs/CHANGELOG.md) — Historial de versiones.
- [docs/structure/project_structure.md](docs/structure/project_structure.md) — Árbol de directorios del plugin.
- [docs/code_walkthrough/Index.md](docs/code_walkthrough/Index.md) — Bóveda de code walkthrough (ES/EN).
- [docs/maintainer/uv_modernization_guide.md](docs/maintainer/uv_modernization_guide.md) — Modernización con `uv`.
- Docs publicados: https://geociencio.github.io/sec_interp_docs/

---
**Plugin Version**: 3.8.0 | **Last Update**: 2026-09-21
