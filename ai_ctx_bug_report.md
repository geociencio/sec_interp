# Bug Report: Critical Incompatibility with Python 3.14 in `ai-context-core`

**Date**: 2026-02-07
**Severity**: High
**Component**: `ai_context_core.analyzer.ast_metrics`

## Description

The `ai-context-core` package fails to analyze Python files containing docstrings or string constants when running on Python 3.14. This causes the analyzer to silently discard these files during the scanning process, resulting in incorrect metrics, particularly 0% i18n coverage, despite valid `tr()` calls being present in the codebase.

## Root Cause

The issue is caused by the removal of `ast.Str` in Python 3.14. The `ai_context_core` codebase explicitly references `ast.Str` in `ast_metrics.py`, which raises an `AttributeError` when the code attempts to access it.

**File**: `.venv/lib/python3.14/site-packages/ai_context_core/analyzer/ast_metrics.py`
**Line**: ~240 (inside `calculate_sloc`)

```python
# Failing code in ast_metrics.py
and isinstance(body[0].value, (ast.Constant, ast.Str))
```

## Traceback

When running `ai-ctx inspect sec_interp_plugin.py` (or any file with docstrings), the following error occurs:

```
❌ Syntax Error: module 'ast' has no attribute 'Str'
```

This error is caught by the broad `except Exception` block in `engine.py`, causing the file to be treated as having a syntax error or simply ignored, leading to zero counts for all metrics derived from that file (including i18n strings).

## Suggested Fix

Replace the direct reference to `ast.Str` with a safe fallback that works across Python versions (since `ast.Str` was deprecated in 3.8 and removed in 3.14).

**Recommended Change**:

```python
# In ai_context_core/analyzer/ast_metrics.py

# CHANGE THIS:
# and isinstance(body[0].value, (ast.Constant, ast.Str))

# TO THIS:
and isinstance(body[0].value, (ast.Constant, getattr(ast, "Str", ast.Constant)))
```

This change ensures that on Python 3.14+, `ast.Str` is effectively ignored (replaced by `ast.Constant`, which is already in the tuple), preventing the `AttributeError` while maintaining backward compatibility for older Python versions if necessary.

## Impact on i18n

Because the main plugin files (like `sec_interp_plugin.py` and `gui/main_dialog.py`) contain docstrings, they trigger this crash. Consequently, the QGIS Compliance Checker logic (which runs on the same AST) never gets to execute the `visit_Call` method to count `tr()` calls, resulting in a reported 0% translation coverage.
