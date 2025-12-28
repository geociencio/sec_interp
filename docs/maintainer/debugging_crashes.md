# Guía de Debugging para Crashes de QGIS

## Introducción

Los crashes de QGIS relacionados con el plugin pueden ocurrir a dos niveles:
1. **Python**: Excepciones capturadas por nuestro logging
2. **C++/Qt**: Segfaults que requieren journalctl del sistema

Esta guía cubre ambos escenarios.

---

## 1. Logging del Plugin

### Ubicación de Logs

```bash
# Log principal del plugin
/home/jmbernales/qgispluginsdev/sec_interp/logs/sec_interp_debug.log

# Logs rotados (backups)
sec_interp_debug.log.1
sec_interp_debug.log.2
...
sec_interp_debug.log.5
```

### Ver Logs en Tiempo Real

```bash
# Seguir el log mientras usas QGIS
tail -f logs/sec_interp_debug.log

# Ver solo operaciones críticas
tail -f logs/sec_interp_debug.log | grep CRITICAL_OP
```

---

## 2. Journalctl (Logs del Sistema)

### Comandos Básicos

```bash
# Ver logs de QGIS desde el último boot
journalctl -b | grep -i qgis

# Ver logs en tiempo real
journalctl -f | grep -i qgis

# Ver logs desde hace 1 hora
journalctl --since "1 hour ago" | grep -i qgis
```

### Buscar Segfaults

```bash
# Buscar segmentation faults
journalctl -b | grep -i "segfault"

# Buscar crashes de QGIS específicamente
journalctl -b | grep -i "qgis.*segfault"
```

---

## 3. Workflow de Debugging de Crashes

### Paso 1: Preparar el Entorno

```bash
# Terminal 1: Seguir log del plugin
tail -f logs/sec_interp_debug.log

# Terminal 2: Seguir journalctl
journalctl -f | grep -i qgis
```

### Paso 2: Reproducir el Crash

1. Ejecutar QGIS desde terminal para ver stderr:
   ```bash
   qgis 2>&1 | tee qgis_stderr.log
   ```

2. Realizar la operación que causa el crash

### Paso 3: Analizar Logs

1. Ver última operación en plugin log
2. Buscar `CRITICAL_OP` antes del crash
3. Buscar segfault en journalctl

---

## 4. Patrones Comunes de Crashes

### Crash en RubberBand
**Causa**: Operación de canvas desde thread incorrecto.

### Crash en Tool Activation
**Causa**: Conflicto con otra herramienta activa o estado inconsistente del canvas.

### Crash en Canvas Refresh
**Causa**: Rubber band no removido correctamente de la escena antes de su eliminación en Python.

---

## 5. Checklist de Debugging

- [ ] Revisar `logs/sec_interp_debug.log` - última operación.
- [ ] Buscar `CRITICAL_OP` antes del crash.
- [ ] Revisar `journalctl` para segfault.
- [ ] Correlacionar timestamps entre ambos logs.
- [ ] Verificar stack trace en journalctl.
- [ ] Revisar stderr de QGIS si se ejecutó desde terminal.
