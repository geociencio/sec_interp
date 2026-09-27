# Exploración: MCP de QA para QGIS 4 (adaptado a SecInterp)

**Estado**: 📝 EXPLORACIÓN / propuesta (no implementado)
**Creado**: 2026-09-23
**Rama**: `feature/dem-section-v3.9.0`
**Motivación**: disponer de un *driver* programático para el **smoke test manual en QGIS 4**
que hoy hacemos a mano (deploy + abrir diálogo + preview), y para futuras validaciones
automatizadas de integración real (complemento de los tests Mock-first, que no cubren
diferencias de API con el QGIS real — ver lección `setDisabled`).

---

## 1. Contexto: `deepseek_qgis_mcp`

Investigado `github.com/kicker315/deepseek_qgis_mcp`: fork efímero (creado y último push el
2025-03-25; 9 commits; 7★; sin licencia ni descripción) del upstream
`jjsantos01/qgis_mcp` (1.105★, activo hasta 2025-10).

- **Arquitectura**: plugin QGIS que abre un **socket TCP `localhost:9876`** (atendido por
  `QTimer` cada 100 ms) + servidor MCP con `FastMCP` (`mcp[cli]`). Protocolo JSON crudo, sin
  framing robusto ni auth.
- **Tools**: `ping`, `get_qgis_info`, `load/create_project`, `get_project_info`,
  `add_vector/raster_layer`, `get_layers`, `remove_layer`, `zoom_to_layer`,
  `get_layer_features`, `execute_processing`, `save_project`, `render_map`, `execute_code`.
- **Añadido DeepSeek**: `ollama_client.py` (modelo `deepseek-r1:14b` en
  `http://localhost:11434`) + tools `process_with_ollama`/`execute_with_ai`.
- **Riesgos**: `execute_code` ejecuta Python arbitrario en QGIS (`exec`) = **RCE**; socket sin
  token; sin límite de tamaño de mensaje.
- **QGIS 4**: **no compatible** (enums planos `QgsMapLayer.VectorLayer`, `Qgis.Critical`);
  probado solo en 3.22.
- **Calidad**: `from qgis.core import *`, doble `main()`, `main.py` de ejemplo, metadata con
  placeholders (`author=TuNombre`), sin tests ni licencia.

**Conclusión**: sirve como referencia de arquitectura, pero no como base a adoptar tal cual.

---

## 2. Opciones

| Opción | Descripción | Pros | Contras |
|---|---|---|---|
| **A. Adoptar upstream + portar a QGIS 4** | Fork de `jjsantos01/qgis_mcp`, migrar enums, añadir token | Base con comunidad | Trae `execute_code` (RCE) y una superficie enorme; mantenimiento ajeno |
| **B. MCP propio acotado a SecInterp** | Plugin/servidor mínimo con tools específicas de QA (sin `exec` libre) | Seguro, pequeño, QGIS 4 desde el inicio, alineado con SecInterp | Trabajo inicial; hay que mantenerlo |
| **C. No hacer nada** | Seguir con smoke manual | Cero coste | No automatiza la brecha mock↔QGIS real |

**Recomendación: Opción B.** Un **MCP de QA propio**, acotado, QGIS 4 desde el inicio y sin
ejecución arbitraria de código.

---

## 3. Diseño propuesto (Opción B)

### 3.1 Arquitectura
- **Plugin QGIS** `sec_interp_qa_mcp` (fuera del ZIP del plugin de producción): socket TCP en
  `127.0.0.1` con **token de sesión** efímero; framing con longitud prefijada (no `json.loads`
  a ciegas); límite de tamaño de mensaje.
- **Servidor MCP** (`src/`, `FastMCP`): traduce tools MCP a comandos del socket.
- Reutiliza `qgis-manage deploy` para desplegar SecInterp antes de las pruebas.

### 3.2 Tools acotadas (sin `execute_code`)
- `ping`, `get_qgis_info`
- `load_project(path)` / `load_sample_data()` (carga `examples/sample_data`)
- `list_layers()`, `layer_info(id)`
- `set_layer(layer_id, target="dem|section|geology|structure|collar|survey|interval")`
- `open_sec_interp()` (abre el diálogo del plugin)
- `run_preview()` (pulsa Preview y espera)
- `assert_preview_ready()` (S2: botones activos)
- `read_results_text()` / `snapshot_canvas(path)`
- `export_preview(path)` (Export)
- `get_qgis_log(level)` (lee `QgsMessageLog` de SecInterp para detectar excepciones)

> `execute_code` **no** se expone. Cualquier acción nueva se añade como tool explícita y
> revisable.

### 3.3 Seguridad
- Bind estricto `127.0.0.1`; **token** obligatorio por comando; token generado al arrancar y
  mostrado en el dock del plugin.
- Límite de longitud de mensaje; timeouts; cierre de conexión inactiva.
- Sin acceso a red saliente.

### 3.4 Compatibilidad QGIS 4
- Enums **scoped** desde el inicio (`Qgis.LayerType`, `Qgis.MessageLevel`, `Qt.ItemFlag.*`).
- Imports vía `qgis.PyQt`; nada de `from qgis.core import *`.
- Probar en QGIS 4 (objetivo) y mantener 3.28 (mínimo del plugin).

---

## 4. Fases de implementación

1. **F0 — Esqueleto**: plugin con socket + token + framing robusto; servidor `FastMCP`;
   tools `ping`/`get_qgis_info`/`load_project`/`list_layers`. Smoke: ping↔pong.
2. **F1 — Carga de datos**: `load_sample_data`, `set_layer`, `layer_info`. Smoke: cargar
   `examples/sample_data` y mapear capas a los slots de SecInterp.
3. **F2 — Control del plugin**: `open_sec_interp`, `run_preview`, `assert_preview_ready`,
   `read_results_text`, `snapshot_canvas`, `export_preview`, `get_qgis_log`.
4. **F3 — Integración con `.agent/`**: documentar en `.agent/` cómo un agente usa el MCP para
   el smoke de cada fase; considerar un workflow `/smoke-qgis4`.
5. **F4 — Opcional IA**: cliente local (Ollama/DeepSeek/OpenAI-compatible) que sugiera
   pasos, **manteniendo** el principio de tools explícitas (sin `exec`).

**Estimación**: F0-F2 ~1-2 sesiones; F3 incremental; F4 opcional.

---

## 5. Riesgos y fuera de alcance

- **Riesgos**: mantener el plugin QA fuera del ZIP de producción (`.qgisignore`); el token no
  debe registrarse; el plugin QA podría interferir con perfiles reales → usar un perfil QGIS
  dedicado.
- **Fuera de alcance**: sustituir los tests unitarios (Mock-first sigue siendo la base);
  `execute_code` libre; publicación del plugin QA en el repositorio QGIS.

## 6. Referencias

- `kicker315/deepseek_qgis_mcp` (fork de referencia) · `jjsantos01/qgis_mcp` (upstream)
- Lección `AGENT_LESSONS.md` (2026-09-23, mock fiel a la API real)
- `docs/plans/implementation_plan_dem_section_v3.9.0.md` (smoke manual QGIS 4)
