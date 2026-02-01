# Release Notes - v2.9.0

**Date**: 2026-02-01
**Stable Release**: Consolidated Architectural Modernization

## 🚀 Overview
Version 2.9.0 marks a significant milestone in the modularization and stability of SecInterp. This release consolidates the features and fixes developed during the 2.8.x and 2.9.x cycles into a single, robust, and clean architecture.

## 🏗️ Architectural Modernization
The core of this release is the transition towards a **Clean Architecture** and **Domain-Driven Design** (lite):

*   **Service Decomposition**: The monolithic `DrillholeService` has been decomposed into specialized processors (`Collar`, `Survey`, `Interval`, `ProjectionEngine`), improving maintainability and reducing complexity.
*   **Domain Layer**: Migrated from `core.types` to a semantic `core.domain` package. Entities like `GeologySegment` now reside in `entities.py`, strictly separated from async `TaskInputs`.
*   **Domain-Pure Logic**: All core services now follow a decoupled data flow, extracting data from QGIS objects in the main thread and performing calculations in background threads using pure DTOs.

## ✨ Key Improvements
*   **Core**: Centralized profile context preparation in `prepare_profile_context`.
*   **Stability**: Removed unstable `.clone()` calls in geometry processing, significantly improving reliability on various PyQt5 versions.
*   **Quality**: Achieved a clean analysis state with `ai-ctx` and standardized internal imports using the `sec_interp.` prefix.
*   **Robustness**: Improved `PYTHONPATH` handling for Dockerized testing and local environments.

## 🐛 Critical Bug Fixes
*   Fixed structural projection consistency issues.
*   Resolved `ModuleNotFoundError` during deployment by stabilizing the internal package structure.
*   Fixed coordinate reference system (CRS) transformations for memory layers.

## 🧪 Testing & Quality
*   **199 tests** passing in the official QGIS Docker environment.
*   Full compatibility with `qgis-analyzer` 3.0.x and `ai-context-core` 3.0.1.

---
*For development details, refer to the [Technical Analysis](../research/v2.9.0_technical_analysis.md).*
