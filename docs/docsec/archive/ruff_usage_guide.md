# Guía de Uso de Ruff - SecInterp

**Fecha**: 2025-12-07
**Configuración**: `ruff.toml`

---

## 📋 Índice

1. [¿Qué es Ruff?](#qué-es-ruff)
2. [Instalación](#instalación)
3. [Comandos Básicos](#comandos-básicos)
4. [Integración con Editor](#integración-con-editor)
5. [Configuración Optimizada](#configuración-optimizada)
6. [Ejemplos de Uso](#ejemplos-de-uso)

---

## 1. ¿Qué es Ruff?

**Ruff** es un linter y formateador de Python extremadamente rápido, escrito en Rust.

### Ventajas

✅ **10-100x más rápido** que Flake8, Pylint, Black combinados
✅ **Todo en uno**: Reemplaza múltiples herramientas
✅ **Compatible** con Black, isort, Flake8, Pylint
✅ **Auto-fix**: Corrige automáticamente muchos problemas

### Reemplaza

- **Flake8** - Linting básico
- **Black** - Formateo de código
- **isort** - Ordenamiento de imports
- **pyupgrade** - Modernización de sintaxis
- **pydocstyle** - Validación de docstrings
- **Y más...** (>700 reglas)

---

## 2. Instalación

### Opción 1: Con uv (Recomendado)

```bash
# En el directorio del proyecto
cd /home/jmbernales/qgispluginsdev/sec_interp

# Instalar Ruff
uv pip install ruff

# Verificar instalación
.venv/bin/ruff --version
```

### Opción 2: Con pip

```bash
# Activar entorno virtual
source .venv/bin/activate

# Instalar Ruff
pip install ruff

# Verificar instalación
ruff --version
```

### Opción 3: Instalación global (opcional)

```bash
# Con pipx (recomendado para herramientas CLI)
pipx install ruff

# O con pip global
pip install --user ruff
```

---

## 3. Comandos Básicos

### 3.1 Linting (Verificar código)

```bash
# Verificar todo el proyecto
ruff check .

# Verificar archivo específico
ruff check core/algorithms.py

# Verificar con estadísticas
ruff check . --statistics

# Formato conciso
ruff check . --output-format=concise

# Formato JSON (para CI/CD)
ruff check . --output-format=json
```

### 3.2 Auto-fix (Corregir automáticamente)

```bash
# Corregir todos los problemas auto-corregibles
ruff check . --fix

# Corregir archivo específico
ruff check core/algorithms.py --fix

# Modo seguro (no hace cambios, solo muestra)
ruff check . --fix --diff
```

### 3.3 Formateo de Código

```bash
# Formatear todo el proyecto
ruff format .

# Formatear archivo específico
ruff format core/algorithms.py

# Ver cambios sin aplicar (dry-run)
ruff format . --diff

# Verificar si el código está formateado
ruff format . --check
```

### 3.4 Comandos Combinados

```bash
# Lint + Auto-fix + Format (workflow completo)
ruff check . --fix && ruff format .

# Solo verificar (sin cambios)
ruff check . && ruff format . --check
```

---

## 4. Integración con Editor

### 4.1 VS Code

**Instalar extensión**:
1. Abrir VS Code
2. Ir a Extensions (Ctrl+Shift+X)
3. Buscar "Ruff"
4. Instalar "Ruff" de Astral Software

**Configuración** (`.vscode/settings.json`):

```json
{
  // Habilitar Ruff
  "[python]": {
    "editor.defaultFormatter": "charliermarsh.ruff",
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
      "source.fixAll.ruff": "explicit",
      "source.organizeImports.ruff": "explicit"
    }
  },

  // Configuración de Ruff
  "ruff.enable": true,
  "ruff.lint.enable": true,
  "ruff.format.enable": true,
  "ruff.organizeImports": true,

  // Ruta al ejecutable (si está en .venv)
  "ruff.path": ["${workspaceFolder}/.venv/bin/ruff"],

  // Deshabilitar otras herramientas (opcional)
  "python.linting.enabled": false,
  "python.linting.pylintEnabled": false,
  "python.linting.flake8Enabled": false
}
```

### 4.2 PyCharm / IntelliJ

1. Ir a **Settings** → **Tools** → **External Tools**
2. Agregar nueva herramienta:
   - **Name**: Ruff Check
   - **Program**: `$ProjectFileDir$/.venv/bin/ruff`
   - **Arguments**: `check $FilePath$ --fix`
   - **Working directory**: `$ProjectFileDir$`

3. Agregar otra para formateo:
   - **Name**: Ruff Format
   - **Program**: `$ProjectFileDir$/.venv/bin/ruff`
   - **Arguments**: `format $FilePath$`

### 4.3 Vim/Neovim

```lua
-- Con nvim-lspconfig
require('lspconfig').ruff_lsp.setup{}

-- O con ALE
let g:ale_linters = {'python': ['ruff']}
let g:ale_fixers = {'python': ['ruff']}
```

---

## 5. Configuración Optimizada

Tu archivo `ruff.toml` ya está optimizado con:

### 5.1 Reglas Habilitadas

- **F** - Pyflakes (errores básicos)
- **E/W** - pycodestyle (estilo PEP 8)
- **I** - isort (ordenamiento de imports)
- **N** - pep8-naming (nombres)
- **D** - pydocstyle (docstrings)
- **UP** - pyupgrade (sintaxis moderna)
- **B** - flake8-bugbear (bugs comunes)
- **C4** - flake8-comprehensions
- **SIM** - flake8-simplify
- **PTH** - flake8-use-pathlib
- **PL** - Pylint
- **TRY** - tryceratops (excepciones)
- **C90** - mccabe (complejidad)

### 5.2 Reglas Ignoradas (QGIS/PyQt5)

```toml
# Compatibilidad con QGIS/PyQt5
"F821",   # undefined-name (módulos QGIS)
"N802",   # camelCase (PyQt/QGIS usa camelCase)
"N803",   # argumentos camelCase
"N806",   # constantes Qt

# Flexibilidad en docstrings
"D100", "D104",  # No todos los módulos necesitan docstrings
"D203", "D213",  # Conflictos de formato

# Pylint overrides
"PLR0913",  # too-many-arguments (común en QGIS)
"PLR2004",  # magic-values (coordenadas QGIS)
```

### 5.3 Configuraciones Especiales

```toml
[lint.isort]
known-first-party = ["sec_interp"]  # Tu paquete
known-third-party = ["qgis", "PyQt5"]

[lint.mccabe]
max-complexity = 10  # Complejidad ciclomática máxima

[format]
docstring-code-format = true  # Formatear código en docstrings
```

---

## 6. Ejemplos de Uso

### 6.1 Workflow Diario

```bash
# 1. Antes de commit
ruff check . --fix
ruff format .

# 2. Verificar que todo esté bien
ruff check .
ruff format . --check

# 3. Commit
git add .
git commit -m "feat: add new feature"
```

### 6.2 Pre-commit Hook

Crear `.git/hooks/pre-commit`:

```bash
#!/bin/bash
# Pre-commit hook para Ruff

echo "🔍 Running Ruff checks..."

# Lint
if ! .venv/bin/ruff check . --fix; then
    echo "❌ Ruff check failed. Please fix the issues."
    exit 1
fi

# Format
if ! .venv/bin/ruff format .; then
    echo "❌ Ruff format failed. Please fix the issues."
    exit 1
fi

echo "✅ Ruff checks passed!"
exit 0
```

Hacer ejecutable:
```bash
chmod +x .git/hooks/pre-commit
```

### 6.3 CI/CD (GitHub Actions)

```yaml
# .github/workflows/lint.yml
name: Lint

on: [push, pull_request]

jobs:
  ruff:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - name: Install Ruff
        run: pip install ruff

      - name: Run Ruff
        run: |
          ruff check .
          ruff format . --check
```

### 6.4 Makefile

Agregar a tu `Makefile`:

```makefile
.PHONY: lint format check

# Lint y auto-fix
lint:
	@echo "🔍 Running Ruff lint..."
	.venv/bin/ruff check . --fix

# Formatear código
format:
	@echo "✨ Formatting code..."
	.venv/bin/ruff format .

# Verificar sin cambios
check:
	@echo "🔍 Checking code..."
	.venv/bin/ruff check .
	.venv/bin/ruff format . --check

# Todo junto
qa: lint format check
	@echo "✅ Quality assurance complete!"
```

Uso:
```bash
make lint    # Lint + auto-fix
make format  # Formatear
make check   # Solo verificar
make qa      # Todo junto
```

### 6.5 Ignorar Reglas Específicas

**En línea**:
```python
# Ignorar regla específica en una línea
x = 1  # noqa: E501

# Ignorar múltiples reglas
import os  # noqa: F401, I001
```

**En archivo**:
```python
# ruff: noqa: D100
"""Módulo sin docstring de módulo."""

def foo():
    pass
```

**En bloque**:
```python
# ruff: noqa
# Todo este bloque se ignora
import sys
import os
```

---

## 7. Comandos Útiles

### 7.1 Filtrar Errores por Tipo

```bash
# Ver solo un tipo de error específico (ejemplo: D415)
.venv/bin/ruff check . --select=D415

# Ver múltiples tipos de errores
.venv/bin/ruff check . --select=D415,D417,D200

# Ver todos los errores de docstrings (categoría D)
.venv/bin/ruff check . --select=D

# Ver errores de complejidad
.venv/bin/ruff check . --select=C901,PLR0915

# Ver errores de manejo de excepciones
.venv/bin/ruff check . --select=TRY400,TRY300

# Ver líneas largas
.venv/bin/ruff check . --select=E501

# Ver imports relativos
.venv/bin/ruff check . --select=TID252
```

### 7.2 Corregir Errores Específicos

```bash
# Corregir solo un tipo de error (si es auto-fixable)
.venv/bin/ruff check . --select=D415 --fix

# Corregir con correcciones "unsafe" (más agresivo)
.venv/bin/ruff check . --select=D415 --unsafe-fixes --fix

# Ver qué cambiaría sin aplicar
.venv/bin/ruff check . --select=D415 --diff

# Ver qué cambiaría con unsafe-fixes sin aplicar
.venv/bin/ruff check . --select=D415 --unsafe-fixes --diff

# Corregir múltiples tipos específicos
.venv/bin/ruff check . --select=W293,Q000,UP006 --fix
```

### 7.3 Formatos de Salida

```bash
# Formato completo (muestra código)
.venv/bin/ruff check . --output-format=full

# Formato conciso (solo ubicaciones)
.venv/bin/ruff check . --output-format=concise

# Formato agrupado por archivo
.venv/bin/ruff check . --output-format=grouped

# Formato JSON (para procesamiento)
.venv/bin/ruff check . --output-format=json

# Estadísticas de errores
.venv/bin/ruff check . --statistics
```

### 7.4 Ver Reglas Disponibles

```bash
# Listar todas las reglas
ruff rule --all

# Buscar regla específica
ruff rule F401

# Ver reglas de una categoría
ruff rule --category pycodestyle

# Ver descripción de una regla
ruff rule D415
```

### 7.5 Generar Configuración

```bash
# Ver configuración actual
ruff check --show-settings

# Generar configuración desde pyproject.toml
ruff check --config pyproject.toml

# Especificar archivo de configuración
ruff check . --config ruff.toml
```

### 7.6 Análisis de Proyecto

```bash
# Análisis completo con estadísticas
.venv/bin/ruff check . --statistics

# Ver solo archivos con errores
.venv/bin/ruff check . --output-format=concise | grep -v "All checks passed"

# Contar total de errores
.venv/bin/ruff check . --output-format=concise | wc -l

# Ver errores por archivo
.venv/bin/ruff check . --output-format=grouped
```

---

## 8. Migración desde Otras Herramientas

### Desde Black

```bash
# Ruff format es compatible con Black
# Solo reemplaza el comando
black .  →  ruff format .
```

### Desde Flake8

```bash
# Mapeo de configuración
# .flake8 → ruff.toml

[flake8]
max-line-length = 88
ignore = E203,W503

# Equivalente en ruff.toml
line-length = 88
[lint]
ignore = ["E203", "W503"]
```

### Desde isort

```bash
# isort ya está integrado en Ruff
isort .  →  ruff check . --select I --fix
```

---

## 9. Solución de Problemas

### Ruff no encuentra el archivo de configuración

```bash
# Especificar configuración manualmente
ruff check . --config ruff.toml
```

### Conflictos con Black

```bash
# Ruff format es compatible con Black por defecto
# Si hay conflictos, verifica:
ruff format . --diff
```

### Demasiados errores

```bash
# Empezar con reglas básicas
ruff check . --select F,E

# Ir agregando gradualmente
ruff check . --select F,E,W,I
```

---

## 10. Casos de Uso Prácticos (SecInterp)

### 10.1 Análisis Inicial del Proyecto

```bash
# 1. Ejecutar análisis completo
.venv/bin/ruff check . --output-format=full

# 2. Ver estadísticas por tipo de error
.venv/bin/ruff check . --statistics

# Resultado inicial: 1,110 errores encontrados
```

### 10.2 Ajustar Configuración para QGIS

**Problema**: 114 errores de imports relativos (TID252) porque la configuración prohibía todos los imports relativos.

**Solución**: Modificar `ruff.toml` línea 179:

```toml
# Antes
ban-relative-imports = "all"

# Después
ban-relative-imports = "parents"  # Permite imports del mismo nivel
```

**Resultado**: Reducción de 114 → 34 errores de imports relativos.

### 10.3 Correcciones Automáticas Masivas

```bash
# Aplicar todas las correcciones automáticas seguras
.venv/bin/ruff check . --fix

# Resultado: 616 errores corregidos automáticamente (55%)
# - Anotaciones modernizadas (List → list, Optional[X] → X | None)
# - Comillas estandarizadas (simples → dobles)
# - Imports ordenados
# - Declaraciones UTF-8 eliminadas
# - Espacios en blanco limpiados
```

### 10.4 Correcciones Específicas por Tipo

**Ejemplo 1: Corregir docstrings sin puntuación final (D415)**

```bash
# Ver todos los errores D415
.venv/bin/ruff check . --select=D415 --output-format=concise

# Resultado: 21 errores encontrados

# Aplicar corrección con unsafe-fixes
.venv/bin/ruff check . --select=D415 --unsafe-fixes --fix

# Resultado: 21 errores corregidos
```

**Ejemplo 2: Ver líneas demasiado largas**

```bash
# Ver todas las líneas >88 caracteres
.venv/bin/ruff check . --select=E501

# Resultado: 78 líneas largas (corrección manual requerida)
```

**Ejemplo 3: Mejorar manejo de excepciones**

```bash
# Ver errores de logger.error en bloques except
.venv/bin/ruff check . --select=TRY400

# Corrección manual: cambiar logger.error() → logger.exception()
```

### 10.5 Progreso del Proyecto

| Fase | Errores | Acción |
|------|---------|--------|
| **Inicial** | 1,110 | Análisis completo |
| **Después de config** | 1,031 | Ajuste de `ban-relative-imports` |
| **Después de --fix** | 415 | Correcciones automáticas |
| **Después de D415** | 394 | Corrección de docstrings |
| **Mejora total** | **-716 (-64.5%)** | ✅ |

### 10.6 Workflow Recomendado

```bash
# 1. Análisis inicial
.venv/bin/ruff check . --statistics

# 2. Ajustar configuración si es necesario
# Editar ruff.toml según necesidades del proyecto

# 3. Correcciones automáticas seguras
.venv/bin/ruff check . --fix

# 4. Correcciones unsafe (revisar cambios después)
.venv/bin/ruff check . --unsafe-fixes --fix

# 5. Correcciones específicas por tipo
.venv/bin/ruff check . --select=D415 --unsafe-fixes --fix

# 6. Verificar progreso
.venv/bin/ruff check . --statistics

# 7. Commit de cambios
git add .
git commit -m "style: apply ruff fixes"
```

### 10.7 Integración en Makefile

Agregar estos targets al `Makefile` del proyecto:

```makefile
.PHONY: ruff-check ruff-fix ruff-stats ruff-unsafe

# Verificar código sin cambios
ruff-check:
\t@echo "🔍 Running Ruff checks..."
\t.venv/bin/ruff check .

# Aplicar correcciones automáticas seguras
ruff-fix:
\t@echo "🔧 Applying Ruff fixes..."
\t.venv/bin/ruff check . --fix
\t.venv/bin/ruff format .

# Ver estadísticas
ruff-stats:
\t@echo "📊 Ruff statistics..."
\t.venv/bin/ruff check . --statistics

# Correcciones unsafe (con precaución)
ruff-unsafe:
\t@echo "⚠️  Applying unsafe fixes..."
\t.venv/bin/ruff check . --unsafe-fixes --fix

# Análisis completo
ruff-analyze:
\t@echo "📋 Full Ruff analysis..."
\t.venv/bin/ruff check . --output-format=full > ruff_report.txt
\t@echo "Report saved to ruff_report.txt"
```

Uso:
```bash
make ruff-check    # Solo verificar
make ruff-fix      # Corregir automáticamente
make ruff-stats    # Ver estadísticas
make ruff-unsafe   # Correcciones agresivas
make ruff-analyze  # Generar reporte
```

---

## 11. Recursos

- **Documentación oficial**: https://docs.astral.sh/ruff/
- **Reglas**: https://docs.astral.sh/ruff/rules/
- **GitHub**: https://github.com/astral-sh/ruff
- **VS Code Extension**: https://marketplace.visualstudio.com/items?itemName=charliermarsh.ruff

---

**Última actualización**: 2025-12-07
