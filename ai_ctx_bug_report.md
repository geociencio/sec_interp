# Bug Report: `ai-ctx qgis` reports N/A for valid `metadata.txt`

## 🐛 Description
The command `ai-ctx qgis` correctly identifies `metadata.txt` as valid but fails to extract and display key fields (`Plugin Name`, `Version`, `QGIS Min Version`), showing them as `N/A`.

## 📉 Observed Behavior
```text
🗺️  QGIS PLUGIN VALIDATION

✅ metadata.txt is valid
Plugin Name: N/A
Version: N/A
QGIS Min Version: N/A
```

## 📈 Expected Behavior
The tool should extract and display the values present in the `metadata.txt` file:
```text
Plugin Name: Sec Interp
Version: 2.9.0
QGIS Min Version: 3.0
```

## 🕵️ Reproduction Steps
1.  Environment: Linux, `ai-context-core` v3.0.0 (installed via `uv`).
2.  File: `metadata.txt` containing a `[general]` section.
3.  Command: Run `uv run ai-ctx qgis`.

## 🛠️ Technical Details & Investigation
A local reproduction script using Python's standard `configparser` confirms the file is parsable and valid.

**File Content (`metadata.txt`):**
```ini
[general]
name=Sec Interp
qgisMinimumVersion=3.0
description=Data extraction for geological interpretation
version=2.9.0
...
```

**Reproduction Script Result:**
Using `configparser.ConfigParser(strict=False)` successfully reads the `[general]` section and retrieves the keys `name`, `version`, and `qgisMinimumVersion`.

**Hypothesis:**
The `ai-ctx` parser might be looking for keys in a global scope (without section) or using a parser configuration that strictly requires specific formatting not present in this file (though standard QGIS metadata usually allows `[general]`).

## 💻 System Information
- **OS**: Linux
- **Python**: 3.13
- **ai-context-core**: 3.0.0
