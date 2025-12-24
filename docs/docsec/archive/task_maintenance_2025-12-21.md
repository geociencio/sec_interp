# Task: Project Maintenance and Synchronization

- [x] Fix false positive in `analyze_project_optfixed.py` (metadata check)
- [x] Update `metadata.txt` changelog for v2.1.1 (Native Hybrid Help)
- [x] Final project consistency check (analyzer run)
- [x] Complete commits following Conventional Commits guidelines
- [x] Port CRS fix from `refactor/optimization-core`
- [x] Cleanup merged branches (local and remote)
- [x] Refactor `exporters/profile_exporters.py` (postponed for next session)
- [x] Refactor `gui/main_dialog_validation.py`: Move heavy logic to `core/validation.py`
    - [x] Define `ValidationParams` dataclass in `core/validation.py`
    - [x] Move orchestration logic to `core/validation.py`
    - [x] Update `DialogValidator` to collect data and call core validation
