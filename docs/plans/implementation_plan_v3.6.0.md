# Implementation Plan - Phase v3.6.0 (Global i18n & Performance)

## General Goal
Achieve 100% internationalization coverage (fixing the 587 `MISSING_I18N` issues) and optimize spatial operations in the Interpretation Manager.

---

## User Review Required

> [!IMPORTANT]
> **Critical Decisions**
> 1. **Batch Translation**: Should we use an automated LLM-based batch translation for the remaining strings or a manual curated approach?
> 2. **Spatial Index Strategy**: Optimization of `getFeatures()` might involve changing how features are tracked in memory.

---

## Proposed Changes

### Goal 1: Global i18n Resolution
#### Context
587 strings remain untranslated or missing from the catalog, affecting UX in non-English locales.

#### Components to Implement
- **[MODIFY] [i18n/](file:///home/jmbernales/qgispluginsdev/sec_interp/i18n)**: Expansion of catalog and synchronization.
- **[MODIFY] [scripts/apply_full.py](file:///home/jmbernales/qgispluginsdev/sec_interp/scripts/apply_full.py)**: Enhancements for batch processing.

### Goal 2: Spatial Performance Optimization
#### Context
`gui/dialog_interpretation_manager.py:123` triggers a warning due to non-indexed feature iteration.

#### Components to Implement
- **[MODIFY] [gui/dialog_interpretation_manager.py](file:///home/jmbernales/qgispluginsdev/sec_interp/gui/dialog_interpretation_manager.py)**: Implement `QgsSpatialIndex` for feature lookups.

---

## Verification Plan

### 1. i18n Audit
`uv run qgis-plugin-analyzer translate audit .`
Success: 0 `MISSING_I18N` issues.

### 2. Performance Benchmark
`uv run pytest tests/benchmarks/test_spatial_ops.py`
Success: Iteration time reduced by >50% for 1000+ features.

---

## Total Effort Estimation

| Goal | Effort | Priority |
|------|--------|----------|
| Global i18n | 5 days | High |
| Spatial Optimization | 2 days | Medium |
