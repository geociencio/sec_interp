# Next Steps: Deuda Técnica en UI

## Estado Actual
- **Docker**: Infraestructura estable y documentada.
- **Tests**: 100% pasando (349 tests).
- **Plan v2.7.0**: Objetivo 7 completado.

## Próxima Tarea (Objetivo 4 del Plan v2.7.0)
**Reducción de Deuda Técnica (Arquitectura)**
- **Objetivo**: Fragmentar la lógica de `gui/main_dialog.py` (Complejidad 95).
- **Pasos**:
    1.  Identificar componentes extraíbles (StatusBar, Toolbar, SignalManager).
    2.  Crear submódulos dedicados en `gui/`.
    3.  Actualizar `main_dialog.py` para delegar en estos componentes.
    4.  Verificar que no haya regresiones en el flujo de preview.

## Comando de Retorno
```bash
@/inicia-sesion
```
