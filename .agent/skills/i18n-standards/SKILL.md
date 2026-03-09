---
name: i18n-standards
description: Standards and best practices for internationalization (i18n) in SecInterp
---

# Skill: i18n Standards

This skill defines the standard workflow for maintaining, updating, and validating translations in the SecInterp project.

## 1. Fundamental Principles

1.  **Source Code (English)**: All source code, logs, and comments must be in English.
2.  **Explicit Marking**: All strings visible to the user must be wrapped in `self.tr("...")` (inside QObject classes) or `QCoreApplication.translate("Context", "...")`.
3.  **No Concatenation**: Use string formatting (`%s`, `.format()`, f-strings with `tr`) instead of concatenation to allow for word reordering according to the target language's grammar.
    *   ✅ `self.tr("File %s not found") % filename`
    *   ❌ `self.tr("File ") + filename + self.tr(" not found")`

## 2. Workflow

### 2.1. Master Data Engine (Recommended for Scaling)
To add multiple languages or perform bulk updates:
1. **JSON File**: Create/Update the file in `scripts/i18n/master_data/<lang>.json`. It contains the `Source: Translation` map.
2. **Injection**:
   ```bash
   # Generates/Syncs the .ts with the source code
   ./scripts/update-strings.sh "<lang>"

   # Injects translations from JSON to .ts
   python3 scripts/i18n/apply_full.py <lang> scripts/i18n/master_data/<lang>.json
   ```
3. **Compilation**:
   ```bash
   lrelease i18n/SecInterp_<lang>.ts
   ```

### 2.2. Traditional Workflow (Qt Linguist)
For minor fixes or context review:
Use **Qt Linguist** on the `.ts` files in `i18n/`.

*   **Context**: Ensure you understand where the string appears.
*   **Variables**: Keep `%1`, `%s`, etc., intact.

### 2.3. Compilation (.qm)
To test in QGIS:

```bash
# Compiles .ts to .qm binary
make trans-compile
```
The `.qm` files are generated alongside the `.ts` files and are loaded by `SecInterp.initGui()`.

## 3. Critical Configuration (Gotchas)

### 3.1. Project File (.pro)
The `i18n/sec_interp.pro` file controls which files are scanned.
*   **Exclude**: Tests, dev scripts, and `venv`.
*   **Include**: `core/`, `gui/`, `sec_interp_plugin.py`.

### 3.2. Release & Packaging
*   **INCLUDE**: `.qm` files (binary).
*   **EXCLUDE**: `.ts` files (source) to reduce ZIP size.
*   **Metadata**: When updating the `changelog` in `metadata.txt`, escape the percent sign (`%`) as `%%` if used (e.g., "Completed 100%%").

### 3.3. QGIS Analyzer Validation
The `qgis-plugin-ci` tool may report false positives for "Partial Translation" if it detects docstrings as translatable strings.
*   **Rule**: If real UI coverage is 100%, warnings about untranslated docstrings or internal classes can be ignored.

## 4. Directory Structure

```
sec_interp/
├── i18n/
│   ├── sec_interp.pro       # lupdate configuration
│   ├── SecInterp_es.ts      # Spanish source
│   ├── SecInterp_es.qm      # Spanish binary (Generated)
│   └── ... (other languages)
├── resources.qrc            # Should include .qm if used as resources (optional in QGIS)
└── Makefile                 # make trans-* commands
```

## 5. Common Snippets

### Loading Translator (in `__init__.py` or `plugin.py`)
```python
locale = QSettings().value('locale/userLocale')[0:2]
locale_path = os.path.join(self.plugin_dir, 'i18n', 'SecInterp_{}.qm'.format(locale))

if os.path.exists(locale_path):
    self.translator = QTranslator()
    self.translator.load(locale_path)
    QCoreApplication.installTranslator(self.translator)
```
