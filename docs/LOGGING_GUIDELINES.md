# Guía de Registro de Desarrollo (DEVELOPMENT_LOG.md)

Para mantener la legibilidad y coherencia del registro de desarrollo, todas las IAs y colaboradores deben seguir estas reglas:

## 1. Orden Cronológico Inverso
Las entradas **NUEVAS** deben insertarse siempre en la **PARTE SUPERIOR** del archivo, justo debajo del encabezado principal y el separador.
*   Lo más reciente arriba.
*   Lo más antiguo abajo.

## 2. Formato del Encabezado
Cada sesión debe comenzar con un encabezado de nivel 2 con la fecha y un título descriptivo:
`## [AAAA-MM-DD] - Título de la Sesión (HH:MM)`

## 3. Secciones Estándar
Se recomienda usar las siguientes secciones para facilitar el escaneo rápido:
*   `### Resumen`: Breve párrafo sobre el objetivo de la sesión.
*   `### Logros` o `### Actividades`: Lista de tareas completadas.
*   `### Resultados`: Métricas, estado de tests o impacto del cambio.
*   `### Documentación`: Enlaces a planes de implementación, walkthroughs o informes de cierre.

## 4. Separadores
Utilizar tres guiones `---` entre sesiones para una separación visual clara.

## Ejemplo
```markdown
## [2026-01-12] - Corrección de Errores de Preview (20:30)

### Resumen
Sesión para corregir el error de desempaquetado en sondajes.

### Logros
- Corregido `ValueError` en `core/types.py`.
- Actualizado test de regresión.

---
```
