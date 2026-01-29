# Implementation Plan - Quality Improvement v2.9.0

## Goal Description
Address critical technical debt and quality issues identified by the analyzer (Score: 38.8). The main focus is reducing cyclomatic complexity in core services and the GUI preview manager to ensure long-term maintainability before the release.

## User Review Required
> [!NOTE]
> This is a refactoring sprint. No functional changes are expected, but extensive testing is required to ensure no regressions.

## Proposed Changes

### Metadata
#### [MODIFY] [metadata.txt](file:///home/jmbernales/qgispluginsdev/sec_interp/metadata.txt)
- Remove duplicate `[general]` section to fix parsing error.

### Core Services
#### [MODIFY] [drillhole_service.py](file:///home/jmbernales/qgispluginsdev/sec_interp/core/services/drillhole_service.py)
- **Problem**: High complexity (Score 6), Module too large.
- **Solution**:
    - Extract parameter validation to private methods.
    - Delegate z-fetching logic to `DrillholeUtils` or specialized private methods.
    - Ensure strict separation of concerns (Prepare vs Process).

#### [MODIFY] [controller.py](file:///home/jmbernales/qgispluginsdev/sec_interp/core/controller.py)
- **Problem**: Large logic blocks in `generate_profile_data`.
- **Solution**:
    - Break down the main orchestration method into sub-steps: `_prepare_inputs`, `_execute_services`, `_aggregate_results`.

### GUI Managers
#### [MODIFY] [main_dialog_preview.py](file:///home/jmbernales/qgispluginsdev/sec_interp/gui/main_dialog_preview.py)
- **Problem**: High complexity in `update_preview`.
- **Solution**:
    - Extract signal handling and state updates into smaller, focused methods.

## Verification Plan

### Automated Tests
```bash
# Verify no regressions across the board
make docker-test
```

### Quality Check
```bash
# Verify Score Improvement
ai-ctx analyze --path .
```
