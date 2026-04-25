"""Validation logic for filesystem paths and workspace settings."""

from __future__ import annotations

from pathlib import Path


def validate_safe_output_path(
    path: str,
    base_dir: Path | None = None,
    must_exist: bool = False,
    create_if_missing: bool = False,
) -> tuple[bool, str, Path | None]:
    """Validate an output path string with security and path traversal protection."""
    if not path or path.strip() == "":
        return False, "Output path is required", None

    # 1. Security check
    is_safe, msg, path_obj = _check_path_security(path)
    if not is_safe or not path_obj:
        return False, msg, None

    # 2. Base directory restriction
    if base_dir:
        is_within, msg, resolved_path = _check_base_restriction(path_obj, base_dir)
        if not is_within or not resolved_path:
            return False, msg, None
    else:
        try:
            resolved_path = path_obj.resolve(strict=False)
        except (OSError, RuntimeError) as e:
            return False, f"Cannot resolve path: {e!s}", None

    # 3. Existence and Permissions
    is_valid, msg = _validate_path_state(resolved_path, must_exist, create_if_missing)
    if not is_valid:
        return False, msg, None

    return True, "", resolved_path


def _check_path_security(path: str) -> tuple[bool, str, Path | None]:
    """Perform security checks for null bytes and traversal."""
    if "\0" in path:
        return False, "Path contains invalid null bytes", None

    try:
        path_obj = Path(path)
        if ".." in path_obj.parts:
            return False, "Path contains directory traversal sequences (..)", None
        return True, "", path_obj
    except (TypeError, ValueError) as e:
        return False, f"Invalid path: {e!s}", None


def _check_base_restriction(path_obj: Path, base_dir: Path) -> tuple[bool, str, Path | None]:
    """Ensure path is within a base directory."""
    try:
        resolved_path = path_obj.resolve(strict=False)
        base_resolved = base_dir.resolve(strict=False)
        resolved_path.relative_to(base_resolved)
        return True, "", resolved_path
    except ValueError:
        return False, f"Path escapes base directory: {base_dir}", None
    except (OSError, RuntimeError) as e:
        return False, f"Cannot validate base directory: {e!s}", None


def _validate_path_state(path: Path, must_exist: bool, create_if_missing: bool) -> tuple[bool, str]:
    """Check existence, type, and writability of a path."""
    if not path.exists():
        if must_exist:
            return False, f"Path does not exist: {path}"
        if create_if_missing:
            try:
                path.mkdir(parents=True, exist_ok=True)
            except OSError as e:
                return False, f"Cannot create directory: {e!s}"
        else:
            return True, ""

    if not path.is_dir():
        return False, f"Path is not a directory: {path}"

    # Check if writable
    try:
        test_file = path / ".write_test"
        test_file.touch()
        test_file.unlink()
        return True, ""
    except OSError:
        return False, f"Directory is not writable: {path}"


def validate_output_path(path: str) -> tuple[bool, str, Path | None]:
    """Validate that an output path is a valid directory and currently writable.

    This is a convenience wrapper around `validate_safe_output_path()`
    for general directory validation.

    Args:
        path: The path string to validate.

    Returns:
        tuple: (is_valid, error_message, resolved_path)
            - is_valid: True if the directory is valid and writable.
            - error_message: Error details if validation fails.
            - resolved_path: Absolute Path object if valid, else None.

    """
    return validate_safe_output_path(path, must_exist=True)
