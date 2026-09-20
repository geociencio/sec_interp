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

> [!abstract] One-line summary
> Determines the **final depth** as `max(given, surveys, intervals)`.

**Path**: `core/services/drillhole/survey_processor.py` (15 lines)
**Class**: `SurveyProcessor`
**Layer**: Core · Drillhole
**Tags**: #secinterp #core #drillhole

---

## 🧱 `determine_final_depth()` — logic

```python
def determine_final_depth(self, given_depth, survey_data, intervals) -> float:
    max_s_depth = max([s[0] for s in survey_data]) if survey_data else 0.0
    max_i_depth = max([i[1] for i in intervals]) if intervals else 0.0
    return max(given_depth, max_s_depth, max_i_depth)
```

---

## 🔗 Related notes

- [[trajectory_engine]] — calls it
- [[collar_processor]] — provides `given_depth`

---

*Note of the SecInterp Code Walkthrough vault — v3.8.0*
