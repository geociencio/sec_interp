# 🐞 QGIS Plugin Analyzer - Issues & Improvements Report

This document outlines bugs, configuration issues, and algorithmic weaknesses identified during the analysis of the `sec_interp` project. It is intended for the maintainers of `qgis-plugin-analyzer` to improve the tool's accuracy and reliability.

## 🚨 Critical Bugs

### 1. Deprecated Ruff Flag Usage
**Severity**: 🔴 Critical (Breaks functionality)
**Location**: `analyzer/engine.py:342` (Method: `run_ruff_audit`)

The analyzer uses the deprecated `--format` flag, which causes execution failures with modern `ruff` versions (v0.14.0+).

```python
# CURRENT CODE
cmd = ["ruff", "check", ..., "--format", "json"]

# REQUIRED FIX
cmd = ["ruff", "check", ..., "--output-format", "json"]
```

**Impact**: silently fails to collect linting data if `ruff` crashes, potentially returning an empty list `[]`. In this specific case, the `try-except` block caught the error and returned `[]`, leading to a false "perfect" lint score.

---

## 📉 Algorithmic Weaknesses

### 2. "Perfect Score" Anomaly (Score Masking)
**Severity**: 🟠 Major (Misleading Metrics)
**Location**: `analyzer/engine.py:760` (Method: `_get_maint_score`)

A project with **686 reported issues** (mostly "Medium" severity like missing docstrings) still received a **100.0/100 Maintainability Score**.

**Root Causes**:
1.  **Complexity Dominance**: The score is weighted `70% Complexity + 30% Linting`. Low-complexity projects (avg CC ~1.0) start with a base of 70 points.
2.  **Weak Penalty Formula**:
    ```python
    lint_penalty = ((5 * errors + others) / max(1, total_lines / 10)) * 10
    ```
    - For large projects (e.g., 28k lines), `total_lines / 10` is large (2800).
    - 686 warnings result in `(686 / 2800) * 10 = ~2.45` penalty points.
3.  **Bonus Masking**: The "Modernization Bonus" (e.g., +2.0 for docstring style) is added *after* the penalty, effectively canceling out the small penalty entirely.

**Recommendation**:
- **Separate Penalties**: Do not normalize lint penalties strictly by line count, or use a non-linear scale.
- **Cap Bonuses**: Ensure bonuses cannot restore a score to 100.0 if issues exist.
- **Increase Weights**: Increase the weight of "Medium" severity issues (currently treated as "others" with weight 1).

### 3. Missing `ruff` Configuration Fallback
**Severity**: 🟡 Minor
**Location**: `pyproject.toml` (User Project)

The analyzer relies entirely on the user's `pyproject.toml`. If the user has a permissive configuration (ignoring `D10x`, `C901`), the analyzer reports "Perfect" quality even if the code is messy.

**Recommendation**:
- The analyzer should ideally run with a **baseline strict configuration** internally for scoring purposes, or at least warn the user: *"⚠️  Permissive Lint Configuration Detected: Score may be inflated."*

---

## 🛠️ Feature Requests

1.  **Strict Mode Flag**: Add a CLI flag (e.g., `--strict`) that runs `ruff` with a preset, strict configuration to give an objective "Gold Standard" score.
2.  **Detailed JSON Output**: Include the raw `ruff` exit code and stderr in `project_context.json` to help debug when the linter fails silently.
