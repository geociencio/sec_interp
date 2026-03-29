# SecInterp Internationalization (i18n) System

This directory contains the logic for managing SecInterp plugin translations across multiple languages. The system combines standard Qt tools with a "Master Data" engine to automate and normalize translations.

## Directory Structure

- `master_data/`: Contains JSON files (e.g., `es.json`, `fr.json`) that act as a master "translation memory".
- `apply_full.py`: Main script that injects translations from `master_data/` into `.ts` files.
- `clean_translations.py`: Normalizes and beautifies the XML in `.ts` files to prevent version control noise.
- `update_metadata_languages.py`: Automatically synchronizes the list of supported languages in the plugin's `metadata.txt` file.
- `auto_translate_*.py`: (Optional) Scripts for integration with machine translation services (e.g., DeepL).

## Workflow

The workflow is integrated into the project's `Makefile` for ease of execution:

1.  **String Extraction**:
    ```bash
    make transup
    ```
    This command internally executes:
    - `pylupdate5`: Scans the source code and generates/updates the `.ts` files in the `i18n/` folder.
    - `apply_full.py`: Searches for each original string in the `master_data/` JSON files and, if a translation exists, injects it into the `.ts` file, removing the "unfinished" marker.
    - `clean_translations.py`: Cleans the resulting XML.
    - `update_metadata_languages.py`: Updates the `metadata.txt` file.

2.  **Translating New Strings**:
    - If there are new strings not present in `master_data/`, they will appear as `type="unfinished"` in the `.ts` files.
    - The recommended approach is to add the translation to the corresponding JSON file in `master_data/` and run `make transup` again.

3.  **Compilation**:
    ```bash
    make transcompile
    ```
    Generate the binary `.qm` files that QGIS loads at runtime.

## Golden Rules

- **Never edit `.qm` files** directly; they are generated binaries.
- **Avoid manual edits to `.ts` files** if you can add the translation to `master_data/`. The injection system will overwrite manual changes during the next `make transup`.
- **Strings in code**: Always wrap UI text with `self.tr("Text")` for it to be detectable.
- **HTML Entities**: The `apply_full.py` script is designed to automatically handle entity conversion (like `&apos;` or `&gt;`), so you can use normal characters (`'`, `>`, `<`) in the JSON files.
