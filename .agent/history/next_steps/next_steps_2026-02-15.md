# Próximos Pasos - SecInterp (Fase v3.0.1)

## 🎯 Objetivo Inmediato
Continuar con la limpieza de deuda técnica y preparación para QGIS 4.0.

## 📝 Tareas Pendientes
1.  **Migración PyQt**: Reemplazar los 4 imports restantes de `PyQt5` por `from qgis.PyQt...` en el resto del proyecto (especialmente en `resources.py` y tests).
2.  **Señales**: Investigar y corregir las fugas de señales reportadas en `core/controller.py` que afectan la estabilidad a largo plazo.
3.  **Docstrings**: Seguir con la cobertura de docstrings en `resources/` y `tests/` para alcanzar el 100% global.
4.  **Preview 3D**: Iniciar el diseño/prototipo del `preview_3d_engine.py`.

## 🛠️ Comandos Útiles
Para verificar el tamaño del build tras cambios:
```bash
make zip && ls -lh dist/sec_interp.3.0.0.zip
```

Para correr la suite de tests oficial:
```bash
make docker-test
```

## ⚠️ Bloqueos
- Ninguno. El sistema está en estado **VERDE** (361 tests OK).
