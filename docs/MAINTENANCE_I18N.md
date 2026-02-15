# Mantenimiento de Internacionalización (i18n)

Este documento describe cómo mantener y expandir las traducciones del plugin SecInterp utilizando los scripts automatizados.

## Ubicación de Archivos
- **Scripts**: `scripts/i18n/`
- **Fuentes (.ts)**: `i18n/`
- **Binarios (.qm)**: `i18n/`

## Flujo de Trabajo

### 1. Sincronizar nuevas cadenas del Código
Cuando añadas nuevos mensajes en el código usando `self.tr()` o `QCoreApplication.translate()`, ejecuta:

```bash
pylupdate5 sec_interp_plugin.py core/**/*.py gui/**/*.py -ts i18n/SecInterp_*.ts
```

### 2. Limpiar y Normalizar (Opcional pero Recomendado)
`pylupdate5` a veces genera XML con formato inconsistente o espacios extras que pueden confundir a los linters. Usa el script de limpieza para normalizar:

```bash
python3 scripts/i18n/clean_translations.py
```
*Este script corrige la indentación y elimina espacios inválidos en los tags (ej: `< message >` -> `<message>`).*

### 3. Aplicar Traducciones Base a Nuevos Idiomas
Si añades un nuevo idioma (ej: Italiano `it`), puedes aplicar términos comunes automáticamente:

1. Crea el archivo `.ts`: `pylupdate5 ... -ts i18n/SecInterp_it.ts`
2. Aplica el baseline:
   ```bash
   python3 scripts/i18n/apply_baseline.py i18n/SecInterp_it.ts it
   ```
   *Nota: Debes actualizar el diccionario en `scripts/i18n/apply_baseline.py` para añadir nuevos idiomas o términos.*

### 4. Cobertura Total (Avanzado)
Si necesitas actualizar masivamente todos los idiomas con traducciones de alta calidad basadas en el maestro de datos:

```bash
python3 scripts/i18n/apply_full.py <lang_code> scripts/i18n/master_data/<lang_code>.json
```
*Este método es mucho más potente que el baseline, ya que cubre ~150 strings por idioma (menús, diálogos, errores).*

### 5. Compilar Archivos Binarios
Antes de liberar el plugin, compila los archivos para que QGIS pueda leerlos:

```bash
lrelease i18n/*.ts
```

## Scripts de Utilidad

### `clean_translations.py`
Corrige errores comunes de formato XML y asegura una indentación de 4 espacios. Es fundamental si el editor de texto muestra "miles de errores" por problemas de sintaxis XML.

### `apply_baseline.py`
Mantiene un diccionario pequeño para localizar rápidamente *nuevos* idiomas desde cero.

### `apply_full.py` y `master_data/`
Motor de traducción masiva que permite alcanzar >75% de cobertura core en segundos para los 8 idiomas principales del plugin. Utiliza los archivos JSON en `master_data/` como fuente de verdad.
