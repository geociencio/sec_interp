# SecInterp Internationalization (i18n) System

This directory contains the logic for managing SecInterp plugin translations across multiple languages. The system combines standard Qt tools (`pylupdate5`, `lrelease`) with a rigorous "Master Data" engine to automate, format, and normalize translations safely.

## 🏗️ Architecture & Philosophy

The i18n system strictly adheres to the **"Single Source of Truth" (SSoT)** pattern.
Instead of developers directly modifying complex and fragile Qt XML (`.ts`) files, all translations are managed via simple JSON dictionaries located in `master_data/`.

During the build process, the system natively parses the XML using `xml.etree.ElementTree`, safely injects the strings from the JSON dictionaries, formats the XML using native indentation, and updates the plugin metadata—all without fragile regex hacks.

## 📂 Directory Structure

- `master_data/`: Contains JSON files (e.g., `es.json`, `de.json`) that act as the master "translation memory" for each supported locale.
- `apply_full.py`: The core orchestrator. Parses the `.ts` files, injects translations safely via AST, and applies native XML beautification (`ET.indent`).
- `auto_translate_all_missing.py`: Bulk automation script. Uses a translation API to find missing strings (marked as `unfinished`), translates them using Google Translate in parallel, and saves them back to `master_data/` asynchronously, enforcing alphabetical order.
- `update_metadata_languages.py`: Automatically synchronizes the list of supported languages dynamically in the plugin's root `metadata.txt` file.
- `translate_docs.py` / `bulk_translate_user_guide.py`: Ad-hoc pipelines for translating markdown documentation or Qt technical guides.

*(Note: Legacy scripts like `apply_baseline.py` and `clean_translations.py` have been permanently deprecated in favor of native Python XML handlers and unified JSON registries).*

## 🔄 Daily Workflow (How to Translate)

The workflow is natively integrated into the project's root `Makefile` for zero-friction execution.

### 1. Extract, Update, and Inject Strings
When you add new `self.tr("New Text")` strings in the Python code or UI, run:
```bash
make transup
```
**Under the hood, this command will:**
1. Call `pylupdate5` to scan source code and generate/update the `.ts` files.
2. Call `apply_full.py` to search for each original string in the `master_data/` JSON files and safely inject them into the `.ts` file, stripping the "unfinished" XML tag.
3. Call `update_metadata_languages.py` to refresh `metadata.txt`.

### 2. Auto-Translating New Strings (Machine Translation)
If you introduced new strings that are not present in `master_data/`, they will appear as `type="unfinished"` inside the Qt `.ts` files.
To automatically translate them across **all 13 supported languages** without manual dictionary editing:
```bash
python scripts/i18n/auto_translate_all_missing.py
```
This script will parse the missing keys, ping Google Translate in parallel threads, and rewrite the `master_data/*.json` files enforcing `sort_keys=True` to maintain tidy Git diffs.

Once the JSON is updated, simply run `make transup` again to inject them!

### 3. Compilation for QGIS
To compile the raw XML `.ts` files into the binary `.qm` format that QGIS physically reads during runtime:
```bash
make transcompile
```

## 📜 The Golden Rules

> [!CAUTION]
> **Never edit `.qm` files directly.** They are compiled Qt binaries.

> [!WARNING]
> **Never edit `.ts` files directly.** Any manual modifications you make inside the XML files will be **wiped out** the next time `make transup` is executed. Always modify the corresponding `master_data/{lang}.json` file.

- **Strings in code**: Always wrap user-facing text with `self.tr("Text")` or `QCoreApplication.translate("Context", "Text")` so that `pylupdate5` detects them.
- **HTML Entities**: The `apply_full.py` orchestrator automatically handles entity conversion (`&apos;`, `&gt;`). Enter the strings normally in the JSON files (`'`, `>`, `<`).
- **Alphabetical Sorting**: Our JSON dictionaries are strictly sorted alphabetically to preserve Git History readability. `auto_translate_all_missing.py` handles this automatically, but ensure you format the JSON if adding entries manually.
