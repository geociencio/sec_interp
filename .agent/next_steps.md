# Next Steps - 2026-03-01

## Contexto Actual
Se ha completado la Fase 3.2.0 (Expansión de Tests) y la Fase 3.2.1 (Automatización de Documentación). El proyecto cuenta ahora con **450 tests unitarios e integración** que pasan exitosamente en Docker. Se corrigió una regresión en el motor de trayectorias.

## Tareas Pendientes Inmediatas
- [ ] **Migración a QGIS 4.x**: Iniciar la auditoría de compatibilidad de la API (Skill `qgis-migration-4x`).
- [ ] **Refactorización de UI**: Reducir la complejidad en los gestores de diálogo que aún superan los umbrales de Ruff.
- [ ] **Cobertura de 3D**: Expandir tests de integración para casos de bordes en proyecciones cartesianas complejas.

## Comando para retomar
```bash
/inicia-sesion
```

## Pendientes de Calidad
- [ ] Corregir 4 tests "skipped" en la suite actual (verificar por qué se omiten en Docker).
- [ ] Eliminar advertencias de `DEPRECATED` en el Docker build (cambiar a BuildKit si es posible en el entorno).
