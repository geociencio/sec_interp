# Siguientes Pasos (2026-02-14)

## Estado Actual
Se ha completado la integración de `qgis-plugin-analyzer` v1.9.0 en los workflows del agente. El sistema ahora cuenta con herramientas especializadas para auditoría de i18n, seguridad y rendimiento.

## Tareas Pendientes (Prioridad Alta)
- [ ] **Infrastructure Fix (Tests)**: Refactorizar `tests/mocks/qt_mocks.py` urgentemente. La suite de tests falla por mocks incompletos (`MockQWidget`, `MockQLayout` faltan métodos como `addSpacing`, `insertWidget`, etc.).
- [ ] **Migración PyQt5**: Ejecutar reemplazo de imports en `resources/resources.py`.
- [ ] **Corrección de Signal Leaks**: Abordar las 66 fugas detectadas.
- [ ] **Cobertura de Docstrings**: Completar documentación faltante.

## Problemas Conocidos (Deuda Técnica)
- **Tests de Integración 3D**: Fallos en exportación (Geometry type mismatch, `IndexError`).
- **Smoke Tests**: Bloqueados por `AttributeError` en mocks de UI (`DemPage`, `InterpretationPage`).

## Comandos para Retomar
Para iniciar la fase de corrección:
```bash
/inicia-sesion
# Primero arreglar la infraestructura de tests
uv run pytest tests/integration/test_qgis_smoke.py
```

## Notas Técnicas
- El nuevo workflow `/audit-plugin` debe ser el punto de partida para validar cada corrección.
- La migración de `qgis.PyQt` es esencial para la compatibilidad futura con QGIS 4.
