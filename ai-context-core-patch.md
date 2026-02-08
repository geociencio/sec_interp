# Patch Proposal: i18n Fixes & Heuristic Refinement for `ai-context-core`

**Date**: 2026-02-07
**Target Version**: v3.0.2+
**Priority**: High (Fixes incorrect compliance scoring)

## 1. Bug Fix: Missing `translate()` aggregation

### Description
The current `ResultsAggregator` only sums calls to `tr()`, ignoring `translate()` (used by `QCoreApplication.translate`). This results in an artificially low number of "Translated strings" in the final report.

### Patch for `ai_context_core/analyzer/aggregator.py`

```diff
--- a/ai_context_core/analyzer/aggregator.py
+++ b/ai_context_core/analyzer/aggregator.py
@@ -123,8 +123,9 @@
             ),
             "i18n_stats": {
                 "total_tr": sum(
-                    m.get("qgis_compliance", {}).get("i18n_usage", {}).get("tr", 0)
-                    for m in m_data
+                    m.get("qgis_compliance", {}).get("i18n_usage", {}).get("tr", 0) +
+                    m.get("qgis_compliance", {}).get("i18n_usage", {}).get("translate", 0)
+                    for m in m_data
                 ),
                 "total_strings": sum(
                     m.get("qgis_compliance", {})
```

---

## 2. Improvement: Precision Heuristic for `total_strings`

### Description
The current heuristic for counting "potentially translatable strings" is too broad, including logs, exceptions, paths, and URLs in the denominator. This makes the i18n coverage score (percentage) useless for large projects.

### Proposed Precision Logic
1. **Context Awareness**: Ignore strings passed to loggers or technical exceptions.
2. **Structural Filtering**: Ignore strings that look like paths, URLs, or pure formatting placeholders.

### Patch for `ai_context_core/analyzer/ast_qgis.py`

```python
# Recommended Refactoring for QGISComplianceVisitor

class QGISComplianceVisitor(ast.NodeVisitor):
    def __init__(self):
        # ... existing results ...
        self._in_ignored_call = False
        self._ignored_functions = {
            "debug", "info", "warning", "error", "critical", "log", # Loggers
            "Exception", "ValueError", "TypeError", "RuntimeError"    # Exceptions
        }

    def visit_Call(self, node: ast.Call):
        # Detect if we should ignore strings inside this call
        func_name = ""
        if isinstance(node.func, ast.Name):
            func_name = node.func.id
        elif isinstance(node.func, ast.Attribute):
            func_name = node.func.attr

        old_ignored = self._in_ignored_call
        if func_name in self._ignored_functions:
            self._in_ignored_call = True

        # ... existing i18n logic (tr/translate) ...

        self.generic_visit(node)
        self._in_ignored_call = old_ignored

    def visit_Constant(self, node: ast.Constant):
        if not isinstance(node.value, str) or len(node.value.strip()) <= 1:
            return

        if self._in_ignored_call:
            return

        val = node.value.strip()

        # Filter out common technical strings
        is_path = val.startswith(("/", "./", "../")) or "\\" in val
        is_url = val.startswith(("http://", "https://", "ftp://"))
        is_placeholder = val.replace("{}", "").replace("%s", "").strip() == ""

        if not (is_path or is_url or is_placeholder):
            if " " in val or any(c in val for c in ".,!?;"):
                self.results["i18n_usage"]["total_strings"] += 1
```

## 3. Impact Assessment
Applying these patches will:
- **Increase accuracy**: Shows the real count of `tr()`/`translate()` calls.
- **Improve Score Quality**: Developers will get a realistic i18n percentage (e.g., 85% instead of 18%), making the QGIS Compliance Score a trustworthy metric.
