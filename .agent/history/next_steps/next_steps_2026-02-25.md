# Próximos Pasos - 2026-02-25

## Estado Actual
La Fase 2.1 de estabilización ha concluido con éxito. Se han resuelto todos los fallos críticos detectados tras la refactorización de optimización (inyección de dependencias, errores de índice y polimorfismo en renderizado).

## Tareas Pendientes
- [ ] Iniciar Fase 3: UX & Performance Elevado.
    - [ ] Optimizar el refresco del canvas en el preview.
    - [ ] Mejorar la feedback visual durante tareas asíncronas largas.
- [ ] Revisión de cobertura de tests para los nuevos objetos `DrillholeProjection`.

## Comandos para Retomar
```bash
/inicia-sesion
uv run pytest tests/core/services/test_drillhole_engine_crash.py
```

## Notas Técnicas
- El motor de trayectorias ahora es robusto ante sondajes fuera de sección.
- El renderizador soporta tanto el formato antiguo como el nuevo, pero se recomienda migrar todos los flujos a `DrillholeProjection`.
