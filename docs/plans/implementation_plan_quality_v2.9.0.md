# Implementation Plan - Quality Improvement v2.9.0

## Goal Description
Address critical technical debt and quality issues identified by the analyzer (Score: 38.8). The main focus is reducing cyclomatic complexity in core services and the GUI preview manager to ensure long-term maintainability before the release.

## User Review Required
> [!NOTE]
> This is a refactoring sprint. No functional changes are expected, but extensive testing is required to ensure no regressions.

## Proposed Changes

### Metadata
- [x] #### [MODIFY] [metadata.txt](file:///home/jmbernales/qgispluginsdev/sec_interp/metadata.txt)
  - Remove duplicate `[general]` section to fix parsing error.

### Core Services
- [x] #### [MODIFY] [drillhole_service.py](file:///home/jmbernales/qgispluginsdev/sec_interp/core/services/drillhole_service.py)
  - Extract parameter validation to private methods.
  - Delegate z-fetching logic.
- [x] #### [MODIFY] [geology_service.py](file:///home/jmbernales/qgispluginsdev/sec_interp/core/services/geology_service.py)
  - Unified elevation sampling and attribute detachment.
- [x] #### [MODIFY] [controller.py](file:///home/jmbernales/qgispluginsdev/sec_interp/core/controller.py)
  - Break down orchestration logic.

### 2.9.0 Phase 3: Redundancy Consolidation
- [x] **Consolidate Utility Functions**: Centralized `prepare_profile_context`, `extract_feature_attributes`, etc.
- [x] **Unify Service Logic**: Applied detached data flow to all core services.
- [x] **Resolve regressions**: Standardized imports and fixed geometry compatibility.

## Verification Plan

### Automated Tests
- [x] `make docker-test` (206 tests passing - 100% Success)

### Quality Check
- [x] `ai-ctx analyze --path .` (Score stabilized, redundancy significantly reduced)
