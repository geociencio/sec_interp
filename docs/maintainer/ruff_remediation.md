# Ruff Error Remediation Plan

## Current State
- **Total Errors**: 287
- **Auto-fixable**: 4 (with --unsafe-fixes)

## Error Distribution
1. **E501**: Line too long
2. **E402**: Module import not at top
3. **UP035**: Deprecated import (List/Dict)
4. **PTH123**: Use pathlib instead of open()
5. **PLC0415**: Import outside top-level

## Remediation Strategy
### Phase 1: Quick Wins
- Use `ruff check --fix --unsafe-fixes`
- Fix bare excepts

### Phase 2: Imports
- Move imports to top level where possible.

### Phase 3: Code Quality
- Break long lines and simplify complex functions.

## Target
Reduce errors to <50.
