# 5. Centralized Logging

Date: 2025-12 (v2.6.0)

## Status

Accepted

## Context

Logging in QGIS plugins is challenging because:
- **UI Thread Safety**: Writing to `QgsMessageLog` from a background thread can cause Segmentation Faults.
- **Crash Persistence**: If QGIS crashes, the internal log panel content is lost.
- **Inconsistency**: Different modules might access different loggers or use `print()` statements.

## Decision

We have implemented a **Centralized Logging Wrapper** in `logger_config.py`.

### 1. Dual Channel Architecture
The logging system automatically detects the environment and routes messages appropriately:
- **Foreground (Main Thread)**: Messages are sent to `QgsMessageLog` (the QGIS "Log Messages" panel) for user visibility.
- **Background (Worker Threads)**: Messages are routed to `sys.stderr` to avoid accessing QGIS UI objects, preventing crashes.

### 2. Disk Persistence (`ImmediateFlushFileHandler`)
- A specialized `RotatingFileHandler` writes a copy of *all* logs (DEBUG level) to a disk file (`logs/sec_interp_debug.log`).
- **Immediate Flush**: It forces an `os.fsync()` after every write. This ensures that even if QGIS crashes hard (segfault), the last log message is preserved on disk for analysis.

## Consequences

### Positive
- **Stability**: Prevents the most common cause of plugin crashes (threading issues with logging).
- **Debuggability**: We have a "Black Box" flight recorder on disk associated with the plugin instance.
- **Standardization**: Developers just use `logger = get_logger(__name__)` and standard Python logging methods (`logger.info`, `logger.error`).

### Negative
- **Performance**: Forced disk sync (`os.fsync`) has a performance penalty, but it is deemed necessary for stability in this context.
- **Complexity**: The `logger_config.py` module is sophisticated and must be maintained carefully.

## Compliance
- **NEVER** use `print()` for debugging.
- **ALWAYS** use `get_logger(__name__)`.
- **NEVER** use `QgsMessageLog` directly in business logic (Core); rely on the logger wrapper.
