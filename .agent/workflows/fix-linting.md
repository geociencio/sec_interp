---
description: Workflow para corregir automáticamente problemas de linting y formateo
agent: QA Engineer
skills: [coding-standards, qa-docker]
validation: |
  - Verificar que ruff y black pasen sin errores
  - Confirmar que imports están ordenados
---

Este workflow automatiza la corrección de problemas de estilo y calidad de código reportados por herramientas estáticas.

### 1. Diagnóstico Inicial

🤖 **Agent Action**: Ejecutar análisis para identificar problemas.

```bash
uv run ruff check .
```

🤖4. **Corrección Automática QGIS Analyze**:
   Usa el fix automático para problemas específicos de QGIS (imports, señales, logging).
   ```bash
   uv run qgis-analyzer fix . --apply --auto-approve
   ```

5. **Verificación Final**:
   Ejecuta nuevamente los linters para asegurar que no quedaron errores residuales.
   ```bash
   uv run ruff check .
   ```

### 2. Corrección Automática (Auto-Fix)

🤖 **Agent Action**: Aplicar correcciones automáticas seguras.

```bash
# 1. Ordenar imports
uv run ruff check --select I --fix .

# 2. Formatear código (Black style via Ruff)
uv run ruff format .

# 3. Aplicar fixes generales (F401, E711, etc.)
uv run ruff check --fix .
```

### 3. Verificación Manual Asistida

Para los errores que NO se pueden corregir automáticamente (ej: `F821 Undefined name`), el agente debe:
1.  Identificar el archivo y línea.
2.  Aplicar un parche específico usando `sed` o edición manual.
3.  Verificar que la corrección no rompa la lógica.

### 4. Validación Final

```bash
uv run ruff check . && uv run black --check .
```

### 5. Commit de Limpieza

```bash
git add .
git commit -m "style: apply automated linting fixes"
```
