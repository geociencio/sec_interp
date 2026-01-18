# Handoff: Refactorización de Gestión de Mensajes

## Estado Actual
- **Objetivo 4 (Deuda Técnica)**: Refactor de mensajes y simplificación de botones de herramientas completado.
- **Tests**: 358 tests en verde (ejecutados vía Docker).
- **Archivos Modificados**:
    - `gui/main_dialog.py` (simplificado)
    - `gui/main_dialog_export.py` (desacoplado)
    - `gui/main_dialog_messages.py` (NUEVO)
    - `gui/main_dialog_cache_handler.py` (implementado)
    - `gui/main_dialog_settings.py` (mejorado)
    - `tests/gui/test_message_manager.py` (NUEVO)

## Pendiente
- Queda pendiente la refactorización de la lógica de validación de campos del diálogo (hacerlo más declarativo o moverlo a un gestor dedicado).

## Comando para Retomar
```bash
/inicia-sesion
```
O simplemente continuar con:
"Simplificar la lógica de validación interna de los campos del diálogo."
