---
tags:
  - secinterp
  - code-walkthrough
  - core
  - drillhole
aliases:
  - survey_processor.py
  - SurveyProcessor
cssclass: secinterp-note
---

# `core/services/drillhole/survey_processor.py`

> [!abstract] Resumen en una línea
> Determina la **profundidad final** del sondaje como `max(given, surveys, intervals)`.

**Ruta**: `core/services/drillhole/survey_processor.py` (15 líneas)
**Clase**: `SurveyProcessor`
**Capa**: Core · Drillhole
**Tags**: #secinterp #core #drillhole

---

## 🧱 `determine_final_depth()` — lógica

```python
def determine_final_depth(self, given_depth, survey_data, intervals) -> float:
    max_s_depth = max([s[0] for s in survey_data]) if survey_data else 0.0
    max_i_depth = max([i[1] for i in intervals]) if intervals else 0.0
    return max(given_depth, max_s_depth, max_i_depth)
```

---

## 🔗 Notas relacionadas

- [[trajectory_engine]] — lo llama
- [[collar_processor]] — provee `given_depth`

---

*Nota de la bóveda SecInterp Code Walkthrough — v3.8.0*
