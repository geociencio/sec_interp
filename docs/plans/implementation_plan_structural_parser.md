# Implementation Plan: Structural-Notation Parser Coverage

**Phase**: post-v3.10.0 backlog — prerequisite/companion of the interop **Phase A**
**Status**: 📝 PLAN — scope confirmed 2026-10-11, **deferred for future implementation** (no code written)
**Created**: 2026-10-11
**References (verified)**: `core/utils/parsing.py` (`parse_strike`, `parse_dip`,
`cardinal_to_azimuth`), `core/services/structure_service.py:148-…` (`_parse_structural_data`),
`core/utils/__init__.py` (re-exports), `tests/core/test_structural_parsing_advanced.py`,
`tests/core/test_utils.py`, real dataset
`examples/sample_data/GGL4MFT751-08_V3TABLAESTRUCTURAL.ods` (465 rows).
**Related**: `docs/plans/implementation_plan_interop_stereonet_3d.md` (Phase A exports the
attitudes this parser produces).

---

## 0. Executive summary

Structural measurements arrive in **many field notations**; the current parser covers the
common ones but has gaps (quadrants with a corrupted degree symbol yield a *silently wrong*
azimuth, and numeric `dip/dip_dir` is dropped). This plan hardens the parser to **cover all
plane notations** behind a **table-driven strategy** with an explicit, configurable
convention for the ambiguous cases — while **preserving every existing behaviour** pinned by
the current tests.

Scope: **planes only** in v1 (`strike`/`dip`/`dip_dir`). Lines (trend/plunge) and rake are
**out of scope**. Disambiguation default: `a/b` = **strike/dip (RHR)**, with
`dip/dip_dir` and `dip_dir/dip` as configurable options.

---

## 1. Verified current behaviour

Working today (evidence: executed against the real parsing module and the real dataset):

| Input | `parse_strike` / `parse_dip` |
|---|---|
| `N 15 W` / `N15W` / `N 15° W` / `N15°W` / `N 15 ø W` | `345` |
| `S 45 E` / `S45E` | `135` |
| `345`, `400` | `345` / `40` (mod 360) |
| `N30E , 45SW`, `N45E|30SE`, `045-30NE` | strike + `(dip, dip_dir)` |
| `Dip: 45 SE` → strike `None`, `(45, 135)` | ✅ |
| `Strike: N 30 E` → `30`, dip `None` | ✅ |
| `22 SW` / `22SW` / `22°SW` | `(22.0, 225)` |
| `45` (dip field) | `(45.0, None)` |

Existing tests **must keep passing** (`tests/core/test_structural_parsing_advanced.py`,
`test_utils.py`), e.g. `N 16ø W, 19ø SW → 344 / (19, 225)`, `125/45SE → 125 / (45, 135)`,
`120 SE → (120, None)` (dip is **not** clamped), `Dip: 45 SE` (strike `None`).

### Gaps (verified)

| Case | Today | Problem |
|---|---|---|
| `N 15� W` (U+FFFD from a Latin-1 file misread as UTF-8) | **`15`** | **silent wrong azimuth** (quadrant regex blocked → numeric fallback) |
| `N 15 X` (invalid cardinal) | `15` | silent; should be `None` |
| `22/225` (dip / dip-dir, numeric) | `(22, None)` | **drops 225** |
| `225/22` (dip-dir / dip) | `(225, None)` | wrong semantic |
| `SW 30` (cardinal before angle) | `None` | unsupported |
| `30/225 SW` | `(30, None)` | drops 225 |

Note: no existing test pins `N 15 → 15`, so making an incomplete quadrant return `None` is a
safe hardening (unlike the pinned behaviours above).

---

## 2. Scope

**In scope (v1 — planes)**
- A unified, table-driven **strategy list** for `parse_strike` / `parse_dip`.
- All plane notations in §3, including numeric dip/dip-dir and cardinal-before-angle.
- A **convention** parameter resolving the `a/b` ambiguity (`strike_dip` default).
- **Fail-loud**: a corrupted/incomplete quadrant returns `None` (never a bare number).
- **Normalisation**: azimuths wrapped to `[0,360)`, `dip_dir` normalised (`+360` when negative).
- Preserve the existing public API and all pinned test behaviours.

**Out of scope**
- Lines (trend/plunge, `30→120`) and fault rake/pitch — a future v2.
- Changing `StructureMeasurement` / the GUI (only the parser + its callers' convention).
- Clamping dip to `[0,90]` (the project intentionally keeps `120 SE → 120`).

---

## 3. Notation catalogue (planes)

| # | Notation | Examples | v1 |
|---|---|---|---|
| 1 | Quadrant strike + dip angle | `N45W 30`, `N 45° W 30`, `N45W/30`, `N45W,30` | ✅ |
| 2 | Azimuth strike + dip | `315/30`, `315 30`, `315°, 30°` | ✅ |
| 3 | Strike/dip explicit (RHR) | `315/30` | ✅ |
| 4 | Quadrant strike + quadrant dip-dir | `N45W 30SW`, `N45W, 30SW` | ✅ |
| 5 | Dip + cardinal dip-dir | `30 SW`, `30SW`, `30°SW` | ✅ |
| 6 | Cardinal dip-dir + dip | `SW 30`, `SW30` | new |
| 7 | Dip + numeric dip-dir | `30/225`, `30 225`, `30-225` | new |
| 8 | Numeric dip-dir + dip (CLAR) | `225/30` | new (via convention) |
| 9 | Dip + numeric dip-dir + cardinal | `30/225 SW` | new |
| 10 | Prefixed field text | `Rumbo N45W, Echado 30 SW`, `Strike: N45W, Dip: 30` | ✅ |
| 11 | Special | `Echado horizontal` (dip 0), `vertical` (dip 90) | new |

Lines (trend/plunge, arrows), rake, degrees-minutes → **v2**.

---

## 4. Design

### 4.1 Strategy table (no if-chains; CC ≤ 10)
A module-level ordered list of `(name, try_parse, role)` strategies; `parse_strike` /
`parse_dip` iterate and return the first match. Priorities:
1. quadrant (`[NS]°? angle [EW]`) — most specific;
2. cardinal-before-angle / cardinal-after-angle;
3. numeric `a/b` (via convention);
4. numeric azimuth;
5. combined/free text (split on `[,/\\;|]`, scan tokens);
6. special words (`horizontal`, `vertical`).

### 4.2 Conventions (resolves `a/b`)
| Convention | `a/b` means | Notes |
|---|---|---|
| `strike_dip` (**default**) | strike / dip | RHR strike; preserves today's `125/45SE` |
| `dip_dipdir` | dip / dip-direction | e.g. `30/225` |
| `dipdir_dip` | dip-direction / dip | CLAR, e.g. `225/30` |

Threaded as an optional `convention: str = "strike_dip"` argument (backward compatible).

### 4.3 Output contract
- `parse_strike(value, convention="strike_dip") -> float | None`
- `parse_dip(value, convention="strike_dip") -> tuple[float | None, float | None]`
  (`dip`, `dip_dir` — unchanged shape).
- New internal result carries `(strike, dip, dip_dir, kind, raw)` for diagnostics; public
  functions keep their current shapes so `StructureService` is untouched.
- **`dip_dir` semantics**: `parse_dip` returns the direction **as written** (cardinal centre,
  e.g. `SW→225`). The **perpendicular** `dip_dir = strike ± 90` for export stays in Phase A of
  the interop plan (documented there), not here.

### 4.4 Robustness / hygiene
- Add `\uFFFD` to the degree-symbol strip list (fixes `N 15� W → 345`).
- If a token starts with `N`/`S` but no `E`/`W` follows (or a non-`EW` letter does), return
  `None` instead of the bare number.
- Normalise azimuths `% 360`; `dip_dir` `+360` when negative.

---

## 5. Files

- `core/utils/parsing.py` — strategy table, conventions, `\uFFFD`/fail-loud, normalisation.
- `core/utils/__init__.py` — re-export any new helper (e.g. `normalize_azimuth`).
- `core/services/structure_service.py` — thread the optional `convention` through
  `_parse_structural_data` (default unchanged) if a per-layer setting is added later.
- (Later, optional) settings UI to choose the convention per layer.

---

## 6. Tests

- **Regression (must stay green)**: `tests/core/test_structural_parsing_advanced.py`,
  `test_utils.py` unchanged.
- **New**: a **variant matrix** covering §3 rows 1–11, each asserted for both
  `parse_strike` and `parse_dip`.
- **New**: encoding/corruption cases (`N 15\uFFFD W → 345` or `None`;
  `N 15 X → None`).
- **New**: each convention (`strike_dip` / `dip_dipdir` / `dipdir_dip`) on `a/b` inputs.
- **New**: numeric `dip/dip_dir` (`30/225 → (30, 225)`), cardinal-before (`SW 30 → (30,225)`),
  normalisation (`225/30` → dip_dir in `[0,360)`).
- **Validation**: run the real 465-row `BASE DE DATOS` expected columns
  (`strike`, `dip`, `dip_dir`) as an integration check.

---

## 7. QA & gates
- Core stays QGIS-free; `tests/core` runs without QGIS.
- `ruff check`/`format` clean; `make mypy` (core) stays green; **CC ≤ 10** per function.
- `unittest discover tests` green.

---

## 8. Risks
| Risk | Mitigation |
|---|---|
| Breaking a pinned behaviour | Keep the existing test suite as the first gate; run before/after |
| Convention mis-defaulted for a dataset | Configurable; the value is echoed in diagnostics |
| Over-engineering (10+ notations) | Table-driven; each strategy is small and independently tested |
| Ambiguity that no convention resolves | Fail-loud + diagnostics rather than a guess |

---

## 9. Acceptance criteria
1. §3 rows 1–11 parse correctly (both directions of each `a/b` under its convention).
2. All existing parser tests pass unchanged.
3. Corrupted quadrants return `None` or the correct azimuth — **never** a silent wrong number.
4. The 465-row real dataset's `strike`/`dip` reconstruct exactly; `dip_dir` normalised.
5. `ruff`/`mypy`/`unittest` green; CC ≤ 10.

---

## 10. Open items (v2 candidates)
- Lines (trend/plunge, arrows) and fault rake/pitch.
- Degrees-minutes (`45°30'`).
- Per-layer convention setting in the UI.
