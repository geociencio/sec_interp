from typing import Tuple, Optional, Union
from pathlib import Path

def validate_safe_output_path(
    path: str,
    base_dir: Optional[Path] = None,
    must_exist: bool = False,
    create_if_missing: bool = False,
) -> Tuple[bool, str, Optional[Path]]:
    r"""Validate an output path string with security and path traversal protection.

    Args:
        path: Original path string to validate.
        base_dir: Optional base directory to restrict the path to (security sandbox).
        must_exist: If True, validation fails if the path is not currently found on disk.
        create_if_missing: If True, attempts to create the directory if it does not exist.

    Returns:
        tuple: (is_valid, error_message, resolved_path)
            - is_valid (bool): True if the path is safe and meets requirements.
            - error_message (str): Reason for validation failure.
            - resolved_path (Path | None): Cleaned, absolute Path object if valid.
    """
    if not path or path.strip() == "":
        return False, "Output path is required", None

    # Security: Check for null bytes (common attack vector)
    if "\0" in path:
        return False, "Path contains invalid null bytes", None

    try:
        path_obj = Path(path)
    except (TypeError, ValueError) as e:
        return False, f"Invalid path: {e!s}", None

    # Security: Check for path traversal patterns in components
    if ".." in path_obj.parts:
        return False, "Path contains directory traversal sequences (..)", None

    # Security: Resolve to canonical absolute path (follows symlinks)
    try:
        # strict=False allows non-existent paths to be resolved
        resolved_path = path_obj.resolve(strict=False)
    except (OSError, RuntimeError) as e:
        return False, f"Cannot resolve path: {e!s}", None

    # Security: If base_dir provided, ensure path is within it
    if base_dir:
        try:
            base_resolved = base_dir.resolve(strict=False)
            # This will raise ValueError if resolved_path is not relative to base
            resolved_path.relative_to(base_resolved)
        except ValueError:
            return False, f"Path escapes base directory: {base_dir}", None
        except (OSError, RuntimeError) as e:
            return False, f"Cannot validate base directory: {e!s}", None

    # Check existence requirements
    if must_exist and not resolved_path.exists():
        return False, f"Path does not exist: {path}", None

    # Create directory if requested
    if create_if_missing and not resolved_path.exists():
        try:
            resolved_path.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            return False, f"Cannot create directory: {e!s}", None

    # If path exists, validate it's a directory
    if resolved_path.exists():
        if not resolved_path.is_dir():
            return False, f"Path is not a directory: {path}", None

        # Check if writable (try to create a temporary file)
        try:
            test_file = resolved_path / ".write_test"
            test_file.touch()
            test_file.unlink()
        except OSError:
            return False, f"Directory is not writable: {path}", None

    return True, "", resolved_path


def validate_output_path(path: str) -> Tuple[bool, str, Optional[Path]]:
    """Validate that an output path is a valid directory and currently writable.

    This is a convenience wrapper around `validate_safe_output_path()`
    for general directory validation.

    Args:
        path: The path string to validate.

    Returns:
        tuple: (is_valid, error_message, resolved_path)
            - is_valid (bool): True if the directory is valid and writable.
            - error_message (str): Error details if validation fails.
            - resolved_path (Path | None): Absolute Path object if valid.
    """
    return validate_safe_output_path(path, must_exist=True)
