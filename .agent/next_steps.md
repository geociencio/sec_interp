# Próximos Pasos (Paso de Testigo)

**Estado Actual:**
- **Suite de Tests:** 100% Estabilizada (347 OK). Infraestructura de mocks reconstruida en `tests/base_test.py`.
- **Roadmap v2.7.0:** Fase de infraestructura (Mocks, Logging, Export 3D) completada.
- **Pendiente Inmediato:** Inicio del **Objetivo 1 (Documentación Sphinx)** o **Objetivo 3 (Validación Nativa con Dataclasses)**.

**Tareas Críticas para la Próxima Sesión:**
1.  **Objetivo 1 (Sphinx):** Configurar `docs/source/conf.py` y crear `scripts/build_docs.sh` para limpiar el repo de HTMLs.
2.  **Objetivo 3 (Dataclasses):** Implementar `core/models/settings_model.py` para reemplazar la validación manual dispersa.

**Comando para Verificar Estado:**
```bash
env PYTHONPATH=.. uv run python3 -m unittest discover tests
```

**Advertencias:**
- El `ModuleProxy` en `base_test.py` es sensible. No resetear agresivamente si se añaden nuevos servicios.
- La ejecución de tests en benchmarks requiere haber importado `tests.base_test` primero (esto ya está automatizado en `tests/__init__.py`).
