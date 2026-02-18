---
description: Estándares y mejores prácticas para la internacionalización (i18n) en SecInterp
---

# Skill: i18n Standards

Esta skill define el flujo de trabajo estándar para mantener, actualizar y validar las traducciones en el proyecto SecInterp.

## 1. Principios Fundamentales

1.  **Código Fuente (Inglés)**: Todo el código fuente, logs y comentarios deben estar en inglés.
2.  **Marcación Explícita**: Todas las cadenas visibles para el usuario deben estar envueltas en `self.tr("...")` (dentro de clases QObject) o `QCoreApplication.translate("Context", "...")`.
3.  **No Concatenación**: Usar formateo de cadenas (`%s`, `.format()`) en lugar de concatenación para permitir el reordenamiento de palabras según la gramática del idioma destino.
    *   ✅ `self.tr("File %s not found") % filename`
    *   ❌ `self.tr("File ") + filename + self.tr(" not found")`

## 2. Flujo de Trabajo (Workflow)

### 2.1. El Motor de "Master Data" (Recomendado para Escalado)
Para añadir múltiples idiomas o actualizar masivamente:
1. **Archivo JSON**: Crear/Actualizar el archivo en `scripts/i18n/master_data/<lang>.json`. Contiene el mapa `Fuente: Traducción`.
2. **Inyección**:
   ```bash
   # Genera/Sincroniza el .ts con el código fuente
   ./scripts/update-strings.sh "<lang>"

   # Inyecta las traducciones del JSON al .ts
   python3 scripts/i18n/apply_full.py <lang> scripts/i18n/master_data/<lang>.json
   ```
3. **Compilación**:
   ```bash
   lrelease i18n/SecInterp_<lang>.ts
   ```

### 2.2. Flujo Tradicional (Qt Linguist)
Para correcciones puntuales o revisión de contexto:
Usar **Qt Linguist** sobre los archivos `.ts` en `i18n/`.

*   **Contexto**: Asegurarse de entender dónde aparece la cadena.
*   **Variables**: Mantener `%1`, `%s`, etc. intactos.

### 2.3. Compilación (.qm)
Para probar en QGIS:

```bash
# Compila .ts a binarios .qm
make trans-compile
```
Los archivos `.qm` se generan junto a los `.ts` y son cargados por `SecInterp.initGui()`.

## 3. Configuración Crítica (Gotchas)

### 3.1. Archivo de Proyecto (.pro)
El archivo `i18n/sec_interp.pro` controla qué archivos se escanean.
*   **Excluir**: Tests, scripts de dev, y `venv`.
*   **Incluir**: `core/`, `gui/`, `sec_interp_plugin.py`.

### 3.2. Release & Empaquetado
*   **INCLUIR**: Archivos `.qm` (binarios).
*   **EXCLUIR**: Archivos `.ts` (fuente) para reducir tamaño del ZIP.
*   **Metadata**: Al actualizar `changelog` en `metadata.txt`, escapar el signo de porcentaje (`%`) como `%%` si se usa (ej: "Completed 100%%").

### 3.3. Validación QGIS Analyzer
El plugin `qgis-plugin-ci` puede reportar falsos positivos de "Partial Translation" si detecta docstrings como cadenas traducibles.
*   **Regla**: Si la cobertura real es 100% en la UI, se puede ignorar la advertencia sobre docstrings/clases internas no traducidas.

## 4. Estructura de Directorios

```
sec_interp/
├── i18n/
│   ├── sec_interp.pro       # Configuración de lupdate
│   ├── SecInterp_es.ts      # Fuente Español
│   ├── SecInterp_es.qm      # Binario Español (Generado)
│   └── ... (otros idiomas)
├── resources.qrc            # Debe incluir los .qm si se usan como recursos (opcional en QGIS)
└── Makefile                 # Comandos make trans-*
```

## 5. Snippets Comunes

### Cargar Traductor (en `__init__.py` o `plugin.py`)
```python
locale = QSettings().value('locale/userLocale')[0:2]
locale_path = os.path.join(self.plugin_dir, 'i18n', 'SecInterp_{}.qm'.format(locale))

if os.path.exists(locale_path):
    self.translator = QTranslator()
    self.translator.load(locale_path)
    QCoreApplication.installTranslator(self.translator)
```
