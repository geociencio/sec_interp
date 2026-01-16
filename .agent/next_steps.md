# Next Steps: Documentación Técnica (Sphinx)

## Estado Actual
- **Validación**: Completada (Niveles 1, 2 y 3).
- **Tests**: 369 tests PASANDO. 100% Estable.

## Tarea Inmediata (Objetivo 1 del Plan v2.7.0)
**Infraestructura de Documentación (Sphinx)**
- **Objetivo**: Desacoplar la documentación HTML del repositorio principal y automatizar su generación.
- **Pasos**:
    1.  Configurar `conf.py` con `autodoc` y `napoleon` para docstrings estilo Google.
    2.  Crear script `build_docs.sh` para exportar a carpeta externa (`../sec_interp_docs`).
    3.  Limpiar archivos HTML rastreados en el repo actual.
    4.  Crear targets en `Makefile` (`make docs`).

## Comando de Retorno
```bash
@/inicia-sesion
```
(La IA debe leer `docs/plans/implementation_plan_v2.7.0.md` para confirmar detalles del Objetivo 1).
