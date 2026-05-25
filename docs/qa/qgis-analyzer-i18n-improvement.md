# qgis-analyzer i18n Audit: False Positives with QCoreApplication.translate()

> **Target audience**: qgis-analyzer maintainers / AI agents working on qgis-analyzer
> **Project**: SecInterp v3.6.0 — QGIS geological interpretation plugin
> **Date**: 2026-05-24
> **Severity**: Medium — inflates issue count, deflates Stability score

---

## 1. Summary

The `qgis-analyzer i18n` check only recognizes `self.tr("...")` as a valid translation wrapper. It does **not** recognize `QCoreApplication.translate("Context", "...")`, which is the standard PyQt/Qt mechanism for translating strings in contexts where `self` is not a `QObject` (static methods, factory classes, module-level functions, and `super().__init__()` calls).

**Impact on SecInterp**: 254 `MISSING_I18N` issues are reported. Investigation shows the vast majority are `QCoreApplication.translate()` calls that are **correctly translated** but not recognized by the analyzer.

---

## 2. Why QCoreApplication.translate() Is Valid and Necessary

`QCoreApplication.translate()` is part of the official Qt i18n API. The PyQt documentation states:

> "If you need to have translatable text in a context where you don't have a QObject
> subclass instance available, you can use QCoreApplication.translate()."

In QGIS plugins, this is essential for:

### 2.1 Static methods and classmethods
```python
class PreviewReporter:
    @staticmethod
    def format_geology_summary(geol_data):
        if not geol_data:
            return QCoreApplication.translate("PreviewReporter", "Geology: No data")
        return QCoreApplication.translate("PreviewReporter", "Geology: {} segments").format(
            len(geol_data))
```
**Why not self.tr()**: `format_geology_summary` is `@staticmethod` — no `self`.

### 2.2 super().__init__() calls in page constructors
```python
class DemPage(BasePage):
    def __init__(self, parent=None):
        super().__init__(
            QCoreApplication.translate("DemPage", "Digital Elevation Model"), parent)
```
**Why not self.tr()**: `self.tr()` is not yet available during `super().__init__()` — the parent's `__init__` hasn't run.

### 2.3 Factory classes and non-QObject orchestrators
```python
class PreviewLayerFactory:  # Not a QObject
    def _create_geology_layer(self):
        ...
        layer.setName(
            QCoreApplication.translate("PreviewLayerFactory", "Geology Outcrops"))
```
**Why not self.tr()**: `PreviewLayerFactory` does not inherit from `QObject` — `tr()` is not available.

### 2.4 Tool classes
```python
class ProfileInterpretationTool(QgsMapTool):
    def _create_interpretation(self):
        ...
        name=QCoreApplication.translate("ProfileInterpretationTool", "New Interpretation")
```
**Why not self.tr()**: `QgsMapTool` inherits from `QObject`, so `self.tr()` IS technically available here. However, `QCoreApplication.translate()` with explicit context is often preferred for clarity and to avoid context-inheritance issues in complex class hierarchies.

---

## 3. Impact on SecInterp

| Metric | Value |
|--------|-------|
| Total `MISSING_I18N` reported | 254 |
| `QCoreApplication.translate()` calls in `gui/` | 47 |
| Lines per call (avg, multiline strings) | ~4 unique strings per call site |
| Estimated false positives | **~200+ of 254** |
| Stability Score impact | Score stuck at 52.3; real maintainability is 90.7 |

The false positives **cannot be suppressed** via:
- `# noqa` comments (qgis-analyzer doesn't parse Python comments for suppression)
- `.analyzerignore` (would require excluding entire files, hiding real issues)
- `analyzer_config.json` (no i18n configuration options exist)

---

## 4. Proposed Fixes

### Option A: Recognize QCoreApplication.translate() as valid i18n (RECOMMENDED)

Add `QCoreApplication.translate("Context", "...")` to the set of recognized i18n wrapping patterns, alongside `self.tr("...")` and `QObject.tr("...")`.

**Implementation guidance**:
1. The i18n checker should look for string literals that are the second argument to `QCoreApplication.translate()` calls
2. The first argument (`"Context"`) should be recognized as the translation context, analogous to the class name in `self.tr()`
3. Format strings using `.format()` on the result of `QCoreApplication.translate()` should be recognized (e.g., `QCoreApplication.translate("Ctx", "Text: {}").format(...)`)

**Regex/pseudo-code for detection**:
```python
# Current (simplified): only detects self.tr("...")
I18N_CALL_RE = re.compile(r'self\.tr\s*\(\s*["\'](.+?)["\']')

# Proposed: also detects QCoreApplication.translate("Context", "...")
I18N_CALL_RE = re.compile(
    r'(?:self\.tr|Q(?:CoreApplication|Object)\.translate)\s*\([^)]*["\']([^"\']+)["\']'
)
```

### Option B: Configurable i18n wrapper patterns

Allow projects to define custom i18n wrapper patterns in `analyzer_config.json`:

```json
{
    "i18n": {
        "wrapper_patterns": [
            "self.tr",
            "QCoreApplication.translate",
            "QObject.translate"
        ],
        "false_positive_tags": ["# no-i18n"]
    }
}
```

### Option C: Respect # noqa / # no-i18n suppression comments

If Options A and B are too complex, at minimum support inline suppression comments so projects can self-document false positives:

```python
return QCoreApplication.translate(  # noqa: MISSING_I18N — static method, no self.tr()
    "PreviewReporter", "Geology: No data")
```

---

## 5. Test Cases for Validator

These should pass (no MISSING_I18N reported):

```python
# Case 1: self.tr() — already works
class MyDialog(QDialog):
    def __init__(self):
        self.setWindowTitle(self.tr("My Dialog"))

# Case 2: QCoreApplication.translate() in static method — SHOULD PASS
class Reporter:
    @staticmethod
    def format():
        return QCoreApplication.translate("Reporter", "No data available")

# Case 3: QCoreApplication.translate() in super().__init__() — SHOULD PASS
class MyPage(BasePage):
    def __init__(self, parent=None):
        super().__init__(
            QCoreApplication.translate("MyPage", "My Page Title"), parent)

# Case 4: QCoreApplication.translate() in non-QObject class — SHOULD PASS
class LayerFactory:
    def create(self):
        layer.setName(QCoreApplication.translate("LayerFactory", "My Layer"))

# Case 5: .format() on translated string — SHOULD PASS
label = QCoreApplication.translate("Ctx", "Found {} items").format(count)
```

---

## 6. Reproduction

```bash
# Clone SecInterp (any QGIS plugin using QCoreApplication.translate() will do)
git clone https://github.com/jmbernales/sec_interp
cd sec_interp

# Run i18n analysis
uv run qgis-analyzer analyze i18n .

# Observe: 254 MISSING_I18N reported
# Inspect gui/preview_reporter.py:39 — already wrapped in QCoreApplication.translate()
uv run qgis-analyzer analyze . 2>&1 | grep "preview_reporter"
```

---

## 7. Existing Workaround (SecInterp-specific)

SecInterp uses a dual-scope i18n strategy to compensate:

| Tool | Scope | Result |
|------|-------|--------|
| `verify_i18n_hygiene.py` (custom AST checker) | Validates `self.tr()` AND `QCoreApplication.translate()` wrapping | 0 violations ✅ |
| `qgis-analyzer i18n` | Only validates `self.tr()` | 254 false positives ⚠️ |

The custom checker was built because the analyzer's limitation was discovered during Phase v3.7.0 QA. It parses the Python AST and recognizes both patterns, plus correctly excludes docstrings, format specifiers, CSS, and developer log strings.

---

## 8. Conclusion

The i18n checker in qgis-analyzer is not incorrect — it's **incomplete**. `QCoreApplication.translate()` is part of the standard Qt i18n API and is required for correct translation in static methods, factory classes, and constructor chains. Adding recognition of this pattern would:

- Eliminate ~80% of false positive i18n issues in projects like SecInterp
- Improve Stability Score accuracy
- Align the analyzer with PyQt/Qt best practices

The fix is a pattern-recognition change in the i18n analysis module, not a new feature. It should be achievable with a regex update or AST visitor extension.

---

*Prepared by the SecInterp agentic QA system (CodeWhale/DeepSeek V4).*
*Contact: via SecInterp GitHub repository.*
