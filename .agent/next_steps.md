# Próximos Pasos - SecInterp

## 🎯 Próximo Objetivo
**Automatización de Metadatos y Versión 3.0.1 Final**

## 📋 Tareas Pendientes
- [ ] **Automatización de metadata**: Crear un script que actualice automáticamente el campo `general_description` en `metadata.txt` con la lista de idiomas disponibles.
- [ ] **Validación en Windows**: Si el usuario cambia de entorno, verificar que el parche de `sed` en `build_docs.sh` funcione o buscar alternativa cross-platform.
- [ ] **Limpieza de RAM**: Investigar si el caché de ayuda en QGIS consume recursos innecesarios tras ver múltiples manuales.

## 🛠️ Comando para Retomar
```bash
/inicia-sesion
```

## ⚠️ Notas
- El despliegue ahora requiere `make deploy` para asegurar que el flag `--no-compile` se aplique.
- No borrar la carpeta `help/html` manualmente sin ejecutar el build después, o el plugin no encontrará la ayuda.
