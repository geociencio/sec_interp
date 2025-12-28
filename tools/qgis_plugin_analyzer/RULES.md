# Rules Catalog: QGIS Plugin Analyzer 📜

This document details the automatic audit rules implemented in the analyzer to ensure that plugins follow official QGIS community standards and development best practices.

## 1. Internationalization (i18n)

| Rule ID | Severity | Description | Recommendation |
| :--- | :--- | :--- | :--- |
| `MISSING_I18N` | 🔴 High | Detects UI strings (setText, setToolTip, etc.) not wrapped in translation functions. | Wrap strings in `self.tr("Text")` or `QCoreApplication.translate()`. |

## 2. Obsolete API and Precision

| Rule ID | Severity | Description | Recommendation |
| :--- | :--- | :--- | :--- |
| `OBSOLETE_API` | 🔴 High | Use of legacy methods like `writeAsVectorFormat()`. | Use the modern V3 version: `QgsVectorFileWriter.writeAsVectorFormatV3()`. |
| `OBSOLETE_VARIANT` | 🟡 Medium | Use of obsolete `QVariant` type constants (e.g., `QVariant.String`). | Use `QMetaType.Type.QString` or native types depending on QGIS version. |
| `UNPRECISE_LAYER` | 🟡 Medium | Use of `mapLayersByName()`. | Use `mapLayers()` or unique layer IDs to avoid ambiguity with duplicate names. |

## 3. Threading Safety

| Rule ID | Severity | Description | Recommendation |
| :--- | :--- | :--- | :--- |
| `UNSAFE_THREADING` | 🔴 High | Use of standard Python `threading.Thread`. | Use `QgsTask` or `QThread` to interact safely with the QGIS main thread. |

## 4. Resource Management

| Rule ID | Severity | Description | Recommendation |
| :--- | :--- | :--- | :--- |
| `MANUAL_RESOURCE_PATH` | 🟡 Medium | Manual paths for icons or UI files (e.g., `icons/ico.png`). | Use the Qt Resource System with the `:/plugins/...` prefix. |

## 5. Performance

| Rule ID | Severity | Description | Recommendation |
| :--- | :--- | :--- | :--- |
| `SPATIAL_INDEX` | 🔴 High | Iterating over features without using a spatial index on heavy layers. | Use `QgsSpatialIndex` to optimize spatial queries. |

## 6. Architecture

| Rule ID | Severity | Description | Recommendation |
| :--- | :--- | :--- | :--- |
| `HEAVY_LOGIC_UI` | 🟡 Medium | Complex logic or heavy dependencies detected inside Graphical User Interface (GUI) files. | Move business logic to `core/services/` or `core/logic/`. |
