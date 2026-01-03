# Guía de Optimización de Interacciones con IA

Esta guía proporciona estrategias prácticas para maximizar la eficiencia en el uso de tokens y obtener el máximo valor de las interacciones con asistentes de IA, especialmente en tiers gratuitos.

## 📊 Contexto: Consumo de Tokens

### Situación Actual (Esta Conversación)
- **Tokens usados**: ~112,000 / 200,000 (56%)
- **Tokens restantes**: ~88,000 (44%)
- **Eficiencia**: Alta (múltiples tareas completadas)

### ¿Qué Consume Más Tokens?

1. **🔴 Alto Consumo** (Evitar cuando sea posible):
   - Ver archivos grandes completos (`view_file` sin límites)
   - Conversaciones largas con mucho contexto
   - Regeneración de código completo
   - Búsquedas amplias sin filtros

2. **🟡 Consumo Medio** (Usar estratégicamente):
   - Ver secciones específicas de archivos
   - Ediciones de código con `replace_file_content`
   - Búsquedas con `grep_search` bien filtradas

3. **🟢 Bajo Consumo** (Usar libremente):
   - Comandos simples (`run_command`)
   - Preguntas directas y específicas
   - Listar directorios (`list_dir`)
   - Crear archivos nuevos pequeños

---

## 🎯 Estrategias de Optimización

### 1. **Preparación Previa (Antes de Iniciar Chat)**

#### ✅ Haz Esto Primero:
```bash
# 1. Organiza tu trabajo en issues/tareas pequeñas
# 2. Ten claro QUÉ quieres lograr (no cómo)
# 3. Identifica archivos relevantes de antemano
# 4. Haz commits frecuentes (puntos de control)
```

#### 📝 Ejemplo de Preparación:
**❌ Mal** (vago, consumirá muchos tokens explorando):
> "Ayúdame a mejorar el código"

**✅ Bien** (específico, directo al grano):
> "Refactoriza `preview_layer_factory.py` líneas 100-150: extrae la lógica de estilos a métodos privados"

---

### 2. **Comunicación Eficiente**

#### Regla de Oro: **Sé Específico y Conciso**

**❌ Evita**:
- Preguntas abiertas sin contexto
- "Explícame todo sobre X"
- Pedir que revise todo el proyecto
- Conversaciones divagantes

**✅ Prefiere**:
- Preguntas específicas con contexto
- "¿Cómo implemento X en el archivo Y?"
- Pedir revisión de archivos específicos
- Ir al grano

#### Ejemplos Prácticos:

**Escenario 1: Debugging**
```
❌ "El código no funciona, ayúdame"
   → Consumo: Alto (tengo que explorar todo)

✅ "Error en línea 45 de geology_service.py:
   AttributeError: 'NoneType' object has no attribute 'asPolyline'"
   → Consumo: Bajo (voy directo al problema)
```

**Escenario 2: Refactoring**
```
❌ "Mejora la calidad del código"
   → Consumo: Muy alto (análisis completo)

✅ "Extrae el método _calculate_elevation de
   geology_service.py (líneas 120-150)"
   → Consumo: Bajo (tarea específica)
```

**Escenario 3: Documentación**
```
❌ "Documenta el proyecto"
   → Consumo: Muy alto

✅ "Crea docstring para GeologyService.generate_geological_profile"
   → Consumo: Bajo
```

---

### 3. **Uso Estratégico de Herramientas**

#### 🔍 Búsqueda de Código

**❌ Ineficiente**:
```python
# Ver archivo completo de 500 líneas
view_file("large_file.py")
```

**✅ Eficiente**:
```python
# Buscar función específica
grep_search("def calculate_elevation", "core/services/")

# Ver solo la función
view_code_item("GeologyService.calculate_elevation")

# Ver rango específico
view_file("geology_service.py", start_line=120, end_line=150)
```

#### 📝 Edición de Código

**❌ Ineficiente**:
```
"Reescribe todo el archivo con estos cambios..."
→ Regenera 500 líneas, alto consumo
```

**✅ Eficiente**:
```
"Reemplaza líneas 45-60 de X con Y"
→ Solo modifica lo necesario, bajo consumo
```

#### 🔄 Iteración

**❌ Ineficiente**:
- Hacer muchos cambios pequeños en conversaciones separadas
- Pedir "muéstrame el resultado" después de cada cambio

**✅ Eficiente**:
- Agrupar cambios relacionados en una sola petición
- Confiar en los tests para verificar
- Usar `git diff` tú mismo para ver cambios

---

### 4. **Gestión de Contexto**

#### Aprovecha la Memoria del Proyecto

La IA tiene acceso a:
- ✅ Workflows en `.agent/workflows/`
- ✅ Documentación en `docs/`
- ✅ Estructura del proyecto

**Usa referencias en lugar de explicar**:
```
❌ "Quiero hacer tests como hicimos antes,
   con unittest y PYTHONPATH=.."

✅ "Sigue el workflow /run-tests"
```

#### Divide Sesiones Largas

**Estrategia de Checkpoints**:
1. Trabaja en una tarea específica
2. Haz commit cuando funcione
3. Cierra la conversación
4. Nueva conversación para siguiente tarea

**Ventaja**: Cada sesión empieza "fresca" sin arrastrar contexto innecesario.

---

### 5. **Workflows Predefinidos**

#### Crea Workflows para Tareas Repetitivas

Ya tienes:
- `/run-tests` - Ejecutar tests
- `/commit-changes` - Hacer commits limpios
- `/run-tests-in-qgis` - Tests en QGIS

**Crea más según necesites**:
```markdown
# .agent/workflows/add-feature.md
1. Crear servicio en core/services/
2. Crear tests en tests/core/
3. Actualizar main_dialog.py
4. Ejecutar /run-tests
5. Ejecutar /commit-changes
```

**Uso**:
```
"Sigue /add-feature para crear servicio de exportación CSV"
→ Bajo consumo, proceso estandarizado
```

---

### 6. **Priorización de Tareas**

#### Matriz de Valor vs Consumo

| Tarea | Valor | Consumo | Prioridad |
|-------|-------|---------|-----------|
| Fix bug crítico | Alto | Bajo | 🟢 Alta |
| Refactoring específico | Alto | Bajo | 🟢 Alta |
| Crear tests unitarios | Alto | Medio | 🟡 Media |
| Documentar API | Medio | Bajo | 🟡 Media |
| Análisis completo código | Bajo | Alto | 🔴 Baja |
| Exploración sin objetivo | Bajo | Alto | 🔴 Evitar |

**Estrategia**: Maximiza tareas 🟢, minimiza 🔴.

---

### 7. **Técnicas Avanzadas**

#### A. Usa Artifacts Inteligentemente

**Los artifacts NO consumen tokens en lecturas posteriores**:
```
1. Crea implementation_plan.md
2. Yo lo leo (sin consumir tokens extra)
3. Ejecuto el plan
4. Actualizo walkthrough.md
```

**Ventaja**: Documentación persistente sin re-explicar.

#### B. Aprovecha el Historial de Git

```bash
# En lugar de pedir "¿qué cambió?"
git log --oneline -10
git diff HEAD~1

# Luego pregunta específicamente
"¿Por qué cambiaste X en el commit abc123?"
```

#### C. Usa Comandos Directos

```bash
# En lugar de pedirme que ejecute comandos simples
ruff check .
pytest tests/

# Solo pídeme ayuda si hay errores
"ruff reporta error X en línea Y, ¿cómo lo arreglo?"
```

---

## 🎓 Ejemplos de Sesiones Optimizadas

### Sesión Eficiente (Bajo Consumo)

```
Usuario: "Refactoriza preview_layer_factory.py:
         extrae estilos a métodos _style_*"

IA: [Analiza archivo específico]
    [Crea métodos]
    [Ejecuta tests]
    [Commit]

Tokens: ~5,000
Resultado: ✅ Tarea completada
```

### Sesión Ineficiente (Alto Consumo)

```
Usuario: "Ayúdame con el código"

IA: "¿Qué necesitas?"

Usuario: "No sé, revisa el proyecto"

IA: [Explora todo el proyecto]
    [Analiza múltiples archivos]
    [Hace preguntas de clarificación]

Usuario: "Ah, quería refactorizar preview_layer_factory.py"

Tokens: ~30,000
Resultado: ⚠️ Misma tarea, 6x más tokens
```

---

## 📋 Checklist Pre-Interacción

Antes de iniciar una conversación, pregúntate:

- [ ] ¿Tengo claro QUÉ quiero lograr?
- [ ] ¿Puedo especificar archivos/líneas exactas?
- [ ] ¿He intentado resolver esto yo mismo primero?
- [ ] ¿Existe un workflow para esto?
- [ ] ¿Es una tarea atómica o debo dividirla?
- [ ] ¿Tengo el contexto necesario (errores, logs)?

**Si respondiste NO a varias**: Prepárate mejor antes de iniciar.

---

## 🚀 Plan de Acción Inmediato

### Para Este Proyecto (sec_interp)

1. **Crea Workflows Adicionales**:
   ```bash
   .agent/workflows/
   ├── run-tests.md ✅
   ├── commit-changes.md ✅
   ├── run-tests-in-qgis.md ✅
   ├── add-feature.md (crear)
   ├── fix-bug.md (crear)
   └── release.md (ya existe)
   ```

2. **Documenta Patrones Comunes**:
   - Cómo añadir un nuevo servicio
   - Cómo añadir una nueva página en el diálogo
   - Cómo exportar a un nuevo formato

3. **Usa Issues/Tasks**:
   - Crea issues en GitHub (o archivo local)
   - Una tarea = una conversación
   - Cierra issue al completar

### Ejemplo de Issue Bien Definido:
```markdown
## Tarea: Añadir exportación a GeoJSON

**Archivos afectados**:
- exporters/geojson_exporter.py (crear)
- tests/exporters/test_geojson_exporter.py (crear)
- gui/main_dialog_export.py (modificar línea 45)

**Criterios de éxito**:
- [ ] Clase GeoJSONExporter hereda de BaseExporter
- [ ] Tests pasan
- [ ] Integrado en diálogo de exportación

**Estimación tokens**: ~8,000
```

---

## 💡 Tips Finales

### 1. **Sesiones Cortas y Frecuentes > Sesiones Largas**
- ✅ 5 sesiones de 10k tokens = 50k tokens, 5 tareas completadas
- ❌ 1 sesión de 50k tokens = 50k tokens, 2-3 tareas completadas

### 2. **Confía en las Herramientas**
- Tests automáticos > Pedir verificación manual
- Git diff > Pedir "muéstrame los cambios"
- Linters > Pedir revisión de estilo

### 3. **Aprende los Workflows**
- Primera vez: Pide ayuda (alto consumo)
- Segunda vez: Sigue el workflow (bajo consumo)
- Tercera vez: Hazlo tú mismo (0 consumo)

### 4. **Documenta Decisiones**
- Usa artifacts para decisiones importantes
- Evita re-explicar el mismo contexto
- Referencia documentos existentes

---

## 📊 Métricas de Éxito

### Sesión Eficiente:
- ✅ <10k tokens por tarea completada
- ✅ Objetivo claro desde el inicio
- ✅ Mínimo "ida y vuelta"
- ✅ Resultado tangible (commit, tests pasando)

### Sesión Ineficiente:
- ❌ >20k tokens por tarea
- ❌ Múltiples clarificaciones
- ❌ Exploración sin rumbo
- ❌ Sin resultado concreto

---

## 🎯 Resumen Ejecutivo

**Regla 80/20**: El 80% de tu valor viene del 20% de las interacciones.

**Maximiza ese 20%**:
1. **Preparación**: Sé específico
2. **Ejecución**: Usa workflows
3. **Verificación**: Confía en tests
4. **Documentación**: Usa artifacts

**Minimiza el 80% restante**:
- Evita exploraciones abiertas
- No pidas que revise todo
- Usa herramientas locales primero
- Divide tareas grandes

---

**Recuerda**: Una pregunta bien formulada vale más que 10 conversaciones vagas.

---

**Próximos Pasos Sugeridos**:
1. Crea workflows para tus tareas más comunes
2. Define templates de issues
3. Practica la "preparación de 5 minutos" antes de cada sesión
4. Revisa esta guía antes de iniciar conversaciones importantes
