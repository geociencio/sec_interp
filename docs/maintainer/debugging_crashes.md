# Debugging Guide for QGIS Crashes

## Introduction

QGIS crashes related to the plugin can occur at two levels:
1. **Python**: Exceptions captured by our logging
2. **C++/Qt**: Segfaults requiring system journalctl

This guide covers both scenarios.

---

## 1. Plugin Logging

### Log Location

```bash
# Main plugin log
/home/jmbernales/qgispluginsdev/sec_interp/logs/sec_interp_debug.log

# Rotated logs (backups)
sec_interp_debug.log.1
sec_interp_debug.log.2
...
sec_interp_debug.log.5
```

### View Logs in Real Time

```bash
# Follow the log while using QGIS
tail -f logs/sec_interp_debug.log

# View only critical operations
tail -f logs/sec_interp_debug.log | grep CRITICAL_OP
```

---

## 2. Journalctl (System Logs)

### Basic Commands

```bash
# View QGIS logs since last boot
journalctl -b | grep -i qgis

# View logs in real time
journalctl -f | grep -i qgis

# View logs from the last hour
journalctl --since "1 hour ago" | grep -i qgis
```

### Search for Segfaults

```bash
# Search for segmentation faults
journalctl -b | grep -i "segfault"

# Search for QGIS crashes specifically
journalctl -b | grep -i "qgis.*segfault"
```

---

## 3. Crash Debugging Workflow

### Step 1: Prepare the Environment

```bash
# Terminal 1: Follow plugin log
tail -f logs/sec_interp_debug.log

# Terminal 2: Follow journalctl
journalctl -f | grep -i qgis
```

### Step 2: Reproduce the Crash

1. Run QGIS from terminal to see stderr:
   ```bash
   qgis 2>&1 | tee qgis_stderr.log
   ```

2. Perform the operation that causes the crash

### Step 3: Analyze Logs

1. Check last operation in plugin log
2. Look for `CRITICAL_OP` before the crash
3. Look for segfault in journalctl

---

## 4. Common Crash Patterns

### Crash in RubberBand
**Cause**: Canvas operation from an incorrect thread.

### Crash in Tool Activation
**Cause**: Conflict with another active tool or inconsistent canvas state.

### Crash in Canvas Refresh
**Cause**: Rubber band not properly removed from the scene before its Python-side deletion.

---

## 5. Debugging Checklist

- [ ] Check `logs/sec_interp_debug.log` — last operation.
- [ ] Look for `CRITICAL_OP` before the crash.
- [ ] Check `journalctl` for segfault.
- [ ] Correlate timestamps between both logs.
- [ ] Verify stack trace in journalctl.
- [ ] Check QGIS stderr if run from terminal.
