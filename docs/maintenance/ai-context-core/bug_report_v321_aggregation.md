# Bug Report: ai-context-core v3.2.1 - Metrics Aggregation Mismatch

## 🚨 Summary
The `AI_CONTEXT.md` and `PROJECT_SUMMARY.md` global summaries report `0` for **Functions**, **Classes**, and **Maintenance Index**, despite individual module analyses being correct in the cache.

## 🔍 Root Cause Analysis
The issue is a **key-mismatch** between the project metrics calculator and the formatter responsible for building the final complexity aggregation dictionary.

### 1. The Producer: `analyzer/builders/calculator.py`
The function `calculate_project_metrics` (lines 79-143) calculates several values but **omits** `total_functions` and `total_classes` from the returned dictionary. Additionally, it names the maintenance index `avg_maintainability`.

```python
# calculator.py (simplified)
return {
    "quality_score": ...,
    "total_lines_code": total_loc,
    "total_physical_lines": total_physical,
    "avg_complexity": round(avg_complexity, 2),
    "max_complexity": max_complexity,
    "avg_maintainability": round(avg_mi, 2), # Named 'avg_maintainability'
    "test_files_count": test_files_count,
    "entry_points_count": len(entry_points),
    # MISSING: total_functions, total_classes
}
```

### 2. The Consumer: `analyzer/builders/formatter.py`
The function `format_complexity_agg` (lines 6-23) attempts to extract these keys using `.get(key, 0)`, resulting in the default value of `0` being used.

```python
# formatter.py (simplified)
return {
    "total_modules": len(valid_modules),
    "total_lines": project_metrics.get("total_lines_code", 0),
    "total_physical_lines": project_metrics.get("total_physical_lines", 0),
    "total_functions": project_metrics.get("total_functions", 0), # Fails (Key missing)
    "total_classes": project_metrics.get("total_classes", 0),     # Fails (Key missing)
    "average_complexity": project_metrics.get("average_complexity", 0),
    "avg_maintenance_index": project_metrics.get("average_maintenance_index", 0), # Fails (Mismatch)
    ...
}
```

### 3. The UI Layer: `analyzer/builders/context_metrics.py`
The `MetricsBuilder` then reads these zero values and renders them in the Markdown file.

## 🛠️ Proposed Resolution (Local Hotfix)

To fix this locally in `.venv/lib/python3.12/site-packages/ai_context_core/analyzer/builders/calculator.py`, the return dictionary must be updated to include the missing keys.

## 📍 Environment Details
- **Tool**: ai-context-core
- **Version**: 3.2.1 (identified via `uv run ai-ctx --version`)
- **Status**: Confirmed via cache inspection and source code audit.
