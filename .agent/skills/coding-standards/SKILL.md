---
name: coding-standards
description: Project coding standards, focused on the use of pathlib, Google docstrings, and strict typing.
trigger: when writing Python code, performing refactors, or defining file paths.
---

# Coding Standards

Defines the technical rules to ensure modern, maintainable, and consistent Python code throughout the SecInterp plugin.

## When to use this skill
- When creating new Python modules or functions.
- When refactoring existing code.
- When defining file paths or manipulating the file system.

## Degree of Freedom
- **Strict**: The use of `pathlib`, Google Docstrings, and Type Hints is mandatory.

## Workflow
1. **Typing**: Add type annotations (Type Hints) to all arguments and return values.
2. **Documentation**: Write docstrings following the Google format.
3. **Paths**: Replace string manipulations or `os.path` with `pathlib.Path` objects.
4. **Modeling**: Mandatory use of Dataclasses (DTOs) for all service returns. Avoid using index-based tuples for complex data transfer.
5. **Validation**: Run `black .` and `ruff check .` to confirm compliance.
5. **Audit**: Use `qgis-analyzer analyze i18n` for new strings and `security` for sensitive code.

## Instructions and Rules

### Modern Python (Pathlib)
- NEVER use string concatenation for paths.
- Use `/` to join paths with `Path`.
- Example: `base_dir / "data" / "file.txt"`.

### Data Transfer Objects (DTOs)
- **Mandatory** use of Dataclasses (DTOs) for all service returns.
- Avoid index-based tuples for complex data transfer.

### Documentation (Google Style)
```python
"""Module-level docstring (MANDATORY per PEP 257)."""

def function(arg1: int) -> str:
    """Short summary.

    Args:
        arg1: Argument description.

    Returns:
        Return value description.
    """
```

### Code Quality
- Follow SOLID principles.
- Keep cyclomatic complexity below 15.

## Quality Checklist
- [ ] Is `pathlib` used for all paths?
- [ ] Do all functions have Type Hints?
- [ ] Do docstrings follow the Google format?
- [ ] Does the code pass `ruff` and `black` checks?
