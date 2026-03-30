# Internationalization (i18n) Maintenance Guide

This document describes how to maintain, expand, and automate translations for the SecInterp QGIS plugin using the refactored **Master Data** engine.

---

## 🏗️ Philosophy: Single Source of Truth (SSoT)

The i18n system follows a strict SSoT pattern. **All translations must be managed exclusively via JSON dictionaries** located in `scripts/i18n/master_data/`.

- **Standard Flow**: `Source Code (.py)` -> `Qt Source (.ts)` -> `Execution (.qm)`.
- **Master Data Flow**: `master_data/*.json` -> `Qt Source (.ts)` (Injection) -> `Execution (.qm)`.

> [!CAUTION]
> **Never edit `.ts` files manually.** Any manual changes in the XML will be overwritten by the automated injection process. Always modify the corresponding JSON file in `master_data/`.

---

## 📂 System Architecture

The core of the system resides in `scripts/i18n/`:

| Component | Responsibility |
|-----------|----------------|
| `master_data/` | JSON files (e.g., `es.json`, `fr.json`) with `Source: Translation` pairs. |
| `apply_full.py` | The main orchestrator. Robustly parses `.ts` files using `ElementTree` and injects translations from JSON. |
| `auto_translate_all_missing.py` | AI-powered automation for bulk machine translation across all 13 supported languages. |
| `update_metadata_languages.py` | Synchronizes the supported language list in the plugin's root `metadata.txt`. |

---

## 🔄 Maintenance Workflow

The workflow is natively integrated into the project's root `Makefile`.

### 1. Synchronizing New Strings (Extraction & Injection)

When you add new `self.tr("New Text")` or `QCoreApplication.translate()` calls in the code:

```bash
# 1. Scans code, updates .ts, injects from JSON, and updates metadata
make transup
```

**What happens under the hood?**
1.  `pylupdate5` scans the code and updates the `.ts` files (marking new strings as `unfinished`).
2.  `apply_full.py` looks for matches in `master_data/*.json` and replaces the `unfinished` entries with the master translation.
3.  `update_metadata_languages.py` refreshes the `metadata.txt` file.

---

### 2. AI-Powered Parallel Translation (Automation)

If you have many new strings marked as `unfinished` and want to translate them across all 13 supported languages automatically:

```bash
# Translates missing strings using Google Translate API in parallel
python scripts/i18n/auto_translate_all_missing.py
```

**Key Features of this script:**
- **Asynchronous Execution**: Ping APIs in parallel threads for maximum speed.
- **Master Update**: Automatically rewrites `master_data/*.json` files while preserving alphabetical sorting for clean Git history.
- **Safe State**: Only translates strings explicitly marked as `unfinished`.

---

### 3. Compilation for QGIS Runtime

Before deploying or testing the plugin in QGIS, compile the XML sources into binaries:

```bash
# Compiles .ts to .qm binaries
make transcompile
```

---

## 📜 The Golden Rules

1.  **Always wrap strings**: Only strings inside `self.tr()` or `QCoreApplication.translate()` will be detected by the scanner.
2.  **No XML manual edits**: If a translation is wrong, fix it in the respective `master_data/<lang>.json`.
3.  **HTML Entities**: Enter characters normally (`'`, `>`, `<`, `&`) in the JSON files; the injection motor handles XML-safe escaping automatically.
4.  **Metadata Sync**: supported locales in `metadata.txt` must match the `.ts` files present in `i18n/`. Run `make transup` to ensure consistency.

---

## 🧪 Testing Translations

To verify a specific language locally:
1.  Run `make transcompile`.
2.  Open QGIS and change the system locale to the desired language (Settings -> Options -> General).
3.  Restart QGIS and open SecInterp.

**Last Updated**: 2026-03-30
**System Version**: 3.4.0
