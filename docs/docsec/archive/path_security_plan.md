# Path Traversal Security Implementation Plan

## Security Issue

**Current State:** The `validate_output_path()` function in `core/validation.py` performs basic validation but lacks protection against path traversal attacks.

**Vulnerability:** Malicious users could potentially use path traversal sequences (`../`, `..\\`, symlinks) to write files outside the intended directory.

---

## Proposed Security Enhancements

### 1. Path Traversal Detection

Add validation to detect and reject common path traversal patterns:
- `../` (Unix-style parent directory)
- `..\\` (Windows-style parent directory)
- Absolute paths when relative expected
- Null bytes (`\0`) in paths
- Symlinks pointing outside allowed directories

### 2. Path Normalization

Use `Path.resolve()` to:
- Resolve symlinks
- Normalize path separators
- Convert to absolute canonical path
- Remove redundant separators and `.` components

### 3. Allowed Directory Validation

Ensure resolved path is within an allowed base directory:
- Check that resolved path starts with allowed base path
- Prevent escaping to parent directories
- Validate against whitelist of allowed directories

---

## Implementation

### New Function: `validate_safe_output_path()`

```python
def validate_safe_output_path(
    path: str,
    base_dir: Optional[Path] = None,
    must_exist: bool = False,
    create_if_missing: bool = False
) -> Tuple[bool, str, Optional[Path]]:
    """Validate output path with path traversal protection.
    
    Args:
        path: Path string to validate
        base_dir: Optional base directory to restrict paths to
        must_exist: If True, path must already exist
        create_if_missing: If True, create directory if it doesn't exist
        
    Returns:
        Tuple of (is_valid, error_message, resolved_Path_object)
        
    Security:
        - Detects path traversal patterns (../, ..\\)
        - Resolves symlinks
        - Validates against base directory
        - Rejects null bytes and suspicious characters
    """
```

### Security Checks

1. **Null Byte Check**
   ```python
   if '\0' in path:
       return False, "Path contains null bytes", None
   ```

2. **Path Traversal Pattern Check**
   ```python
   if '..' in Path(path).parts:
       return False, "Path contains directory traversal sequences", None
   ```

3. **Resolve and Normalize**
   ```python
   try:
       resolved_path = Path(path).resolve(strict=False)
   except (OSError, RuntimeError) as e:
       return False, f"Invalid path: {e}", None
   ```

4. **Base Directory Validation**
   ```python
   if base_dir:
       base_resolved = base_dir.resolve()
       try:
           resolved_path.relative_to(base_resolved)
       except ValueError:
           return False, "Path escapes base directory", None
   ```

5. **Symlink Check (Optional)**
   ```python
   if resolved_path.is_symlink():
       # Optionally reject or validate symlink target
       target = resolved_path.readlink()
       # Validate target is also within base_dir
   ```

---

## Files to Update

### 1. `core/validation.py`
- Add `validate_safe_output_path()` function
- Update `validate_output_path()` to use new function
- Add comprehensive docstrings and examples

### 2. `exporters/base_exporter.py`
- Add path validation before export
- Use `validate_safe_output_path()` in base class

### 3. `gui/main_dialog.py`
- Validate export paths before passing to exporters
- Show clear error messages for invalid paths

---

## Testing

### Unit Tests (`tests/test_validation.py`)

```python
def test_path_traversal_detection():
    """Test detection of path traversal attempts."""
    # Test cases
    assert not validate_safe_output_path("../etc/passwd")[0]
    assert not validate_safe_output_path("..\\windows\\system32")[0]
    assert not validate_safe_output_path("/tmp/../etc/passwd")[0]
    assert not validate_safe_output_path("output/../../etc")[0]

def test_null_byte_rejection():
    """Test rejection of null bytes in paths."""
    assert not validate_safe_output_path("output\0/file.txt")[0]

def test_base_directory_enforcement():
    """Test that paths are restricted to base directory."""
    base = Path("/tmp/safe_output")
    assert validate_safe_output_path("/tmp/safe_output/file.txt", base)[0]
    assert not validate_safe_output_path("/tmp/other/file.txt", base)[0]

def test_symlink_validation():
    """Test symlink handling."""
    # Create test symlink
    # Validate behavior
```

---

## Security Best Practices

### 1. Defense in Depth
- Multiple layers of validation
- Fail securely (reject on doubt)
- Clear error messages (without leaking system info)

### 2. Principle of Least Privilege
- Restrict to specific output directories
- Don't allow arbitrary filesystem access
- Validate early, validate often

### 3. Input Sanitization
- Normalize all paths
- Reject suspicious patterns
- Use allowlists over denylists

---

## Migration Plan

### Phase 1: Add New Function
1. Implement `validate_safe_output_path()`
2. Add comprehensive tests
3. Document security features

### Phase 2: Update Callers
1. Update `validate_output_path()` to use new function
2. Update exporters to use secure validation
3. Update GUI to validate before export

### Phase 3: Deprecation
1. Mark old validation as deprecated
2. Migrate all callers to new function
3. Remove old function in future version

---

## Example Usage

```python
# In exporter
def export(self, output_path: Path, data: Any) -> bool:
    # Validate path is safe
    is_valid, error, safe_path = validate_safe_output_path(
        str(output_path),
        base_dir=Path.home() / "Documents",  # Restrict to Documents
        create_if_missing=True
    )
    
    if not is_valid:
        logger.error(f"Invalid output path: {error}")
        return False
    
    # Use safe_path for export
    with open(safe_path, 'w') as f:
        # ... export logic
```

---

## Benefits

✅ **Security**: Prevents path traversal attacks  
✅ **Robustness**: Handles edge cases (symlinks, special chars)  
✅ **Clarity**: Clear error messages for users  
✅ **Compatibility**: Backward compatible with existing code  
✅ **Testability**: Comprehensive test coverage  

---

## References

- [CWE-22: Path Traversal](https://cwe.mitre.org/data/definitions/22.html)
- [OWASP Path Traversal](https://owasp.org/www-community/attacks/Path_Traversal)
- [Python pathlib security](https://docs.python.org/3/library/pathlib.html#pathlib.Path.resolve)

---

**Priority:** High (Security Issue)  
**Effort:** Medium (2-3 hours)  
**Impact:** High (Prevents security vulnerability)
