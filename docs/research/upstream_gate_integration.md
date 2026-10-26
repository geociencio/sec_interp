# Upstream Gate Integration — qgis-manage & qgis-analyzer

> **Date**: 2026-10-25
> **Status**: implemented in `qgis-manage 0.14.0` and `qgis-plugin-analyzer 1.17.0`
> (2026-10-25); SecInterp now consumes the upstream gates.
> **Scope**: move SecInterp's portal gates into the two reusable tools, without
> duplicating responsibilities.
> **Baseline**: `qgis-manage 0.14.0`, `qgis-plugin-analyzer 1.17.0`.

## 0. Implementation status

- **qgis-manage 0.14.0**: `validate --zip` and artifact checks are implemented
  (`ARTIFACT_ROOT/METADATA/LICENSE/SIZE/BINARY/DEV_FILE/PERMISSIONS/ICON/README/QGIS4/CONFIG`),
  `package --repo-check` audits the built ZIP and normalizes modes to 0644/0755, and
  `docs_entry` is configurable.
- **qgis-analyzer 1.17.0**: `--flake8` / `--linters`, `security --tools
  native,bandit,detect-secrets,flake8`, `security --json` and `--fail-on` are
  implemented; the package-size rule is 25 MB and informational.
- **Still project-specific**: `make flake8` stays scoped to the packaged plugin
  because the analyzer's Flake8 adapter scans the whole repository; `make
  security-scan` stays as the portal-tool gate because `qgis-manage security` does not
  expose a `--portal` mode yet.
- **Removed from SecInterp**: `scripts/check_portal_package.py` and its 9 tests;
  `make portal-check` now calls `qgis-manage validate --zip`.

---

## 1. Ownership model

| Layer | Owner | Examples |
| :--- | :--- | :--- |
| Source code and project quality | **qgis-analyzer** | CC, docstrings, i18n, architecture, module size, Ruff/Flake8, AST security rules |
| Lifecycle, metadata and artifact | **qgis-manage** | `metadata.txt`, structure, LICENSE, build, ZIP, permissions, size, icon, repository compliance |
| Composition and project policy | **plugin repository** | `make pre-release`, exclusions, thresholds, upload |

Rule: **qgis-analyzer never inspects a ZIP; qgis-manage never implements AST
analysis.** Shared behavior is exposed through stable CLI/JSON contracts, not Python
imports between the two repositories.

---

## 2. Current baseline and gaps

### qgis-manage 0.12.0

Already covers:

- `validate --strict --repo`: required metadata, structure (`metadata.txt`,
  `__init__.py`, `LICENSE`), folder name, binaries, `about`/`repository`, URLs.
- `package --repo-check`: runs the same checks **before** building the ZIP.
- `security`: wraps `qgis-analyzer security --deep` (native rules), not Bandit or
  detect-secrets.
- `--json` envelope: `{schema, command, success, errors, warnings, data}`.

Gaps relevant to the portal:

1. The produced ZIP is never opened: no root-layout, size (25 MB), permissions,
   icon, README or embedded-metadata validation.
2. No Flake8 command; no Bandit/detect-secrets parity.
3. `package` inherits source modes (0600/0640 in SecInterp), producing portal
   warnings.
4. `--require-docs` hardcodes `help/html/index.html`.
5. `validate` does not require `repository` unless `--repo`; no QGIS 4 metadata
   advisory.

### qgis-plugin-analyzer 1.16.0

Already covers:

- `analyze . --max-cc N --json`: CC, docstrings, i18n, architecture, module size,
  Ruff audit (`ruff_audit.py`), native security rules, metadata/QGIS checks.
- `security --deep`: native secret/entropy and Bandit-like rules.
- Rule catalog (51 rules) and JSON findings with `file`, `line`, `type`, `severity`,
  `message`, `code`.

Gaps relevant to the portal:

1. No Flake8 adapter. `ruff_audit.py` is a good template.
2. `security` uses native reimplementations, not the portal's actual Bandit and
   detect-secrets; no `--json` on `security`.
3. `repository_compliance` enforces **20 MB over the project directory** (e.g.
   SecInterp reports 65.9 MB because `docs/` and `tests/` are counted). The portal
   limit is **25 MB over the ZIP**. This produces a false failure and belongs to
   qgis-manage's artifact layer.
4. No `portal` profile that enables the exact portal tool set.
5. No QGIS 4 metadata advisory (`qgisMaximumVersion < 4`, deprecated `supportsQt6`).

### SecInterp today

- `scripts/check_portal_package.py` → replace with `qgis-manage validate --zip`.
- `scripts/security_scan.py` → replace with analyzer `security --tools` or
  `qgis-manage security --portal`.
- `make flake8` → replace with analyzer `--flake8` (or keep a thin alias).

---

## 3. qgis-manage design

### 3.1 Artifact validation

New module: `qgis_manager/validation/artifact.py`.

```python
@dataclass
class ArtifactCheck:
    id: str                 # ARTIFACT_*
    status: str             # "error" | "warning" | "ok"
    message: str
    blocking: bool

@dataclass
class ArtifactResult:
    path: Path
    root: str | None
    checks: list[ArtifactCheck]
    errors: list[str]
    warnings: list[str]

def validate_artifact(
    zip_path: Path,
    *,
    max_size_mb: float = 25.0,
    icon_min_px: int = 32,
    strict_permissions: bool = False,
) -> ArtifactResult: ...
```

Checks (IDs are stable contract):

| ID | Severity | Rule |
| :--- | :--- | :--- |
| `ARTIFACT_ROOT` | error | Exactly one top-level folder; ASCII letters/digits/`_`/`-`; no leading digit |
| `ARTIFACT_METADATA` | error | Required fields incl. `repository`; version `X.Y.Z`; filename matches version |
| `ARTIFACT_LICENSE` | error | `LICENSE` at plugin root, exact name, non-empty |
| `ARTIFACT_SIZE` | error | ZIP ≤ 25 MB |
| `ARTIFACT_BINARY` | error | No `.so/.dll/.exe/.dylib/.pyd/.pyc/.pyo` |
| `ARTIFACT_DEV_FILE` | error | No `tests/`, `docs/`, `scripts/`, `.git/`, caches, hidden files |
| `ARTIFACT_PERMISSIONS` | warning | Modes `0644`/`0755`; `--strict-permissions` upgrades to error |
| `ARTIFACT_ICON` | warning | `metadata.icon` exists; PNG ≥ `icon_min_px` |
| `ARTIFACT_README` | warning | `README*` present |
| `ARTIFACT_QGIS4` | warning | `qgisMaximumVersion >= 4.0`; `supportsQt6` deprecated |
| `ARTIFACT_CONFIG` | info | `.bandit`/`.secrets.baseline`/`.flake8` at ZIP root → `Validated (configured)` |

Integration points:

1. `cli/commands/package.py`: after `_build_package`, if `--repo-check`, run
   `validate_artifact`; fail the command on blocking errors. Keep the pre-build
   checks (fast fail) and add the post-build artifact audit.
2. New `validate --zip PATH`:
   ```bash
   qgis-manage validate --zip dist/sec_interp.3.12.0.zip --strict --json
   ```
   `--zip` is mutually exclusive with the positional project path.
3. `core/package.py::_write_zip`: add `normalize_permissions=True` (default when
   `--repo-check`) writing `ZipInfo.external_attr` as `0644`/`0755`, and deterministic
   timestamps (`SOURCE_DATE_EPOCH`) for reproducible artifacts.
4. Config:
   ```toml
   [tool.qgis-manager]
   max_package_size_mb = 25
   icon_min_px = 32
   normalize_permissions = true
   docs_entry = "help/html/es/index.html"   # or glob
   ```
5. JSON envelope (extends the existing `schema: 1`):
   ```json
   {
     "schema": 1,
     "command": "validate",
     "success": false,
     "errors": ["ARTIFACT_LICENSE: LICENSE is missing"],
     "warnings": ["ARTIFACT_PERMISSIONS: 27 files with mode 600"],
     "data": {
       "mode": "zip",
       "path": "dist/sec_interp.3.12.0.zip",
       "root": "sec_interp",
       "size_bytes": 2452906,
       "checks": [
         {"id": "ARTIFACT_LICENSE", "status": "error", "blocking": true,
          "message": "LICENSE is missing"}
       ]
     }
   }
   ```

Acceptance criteria:

- ZIP with missing `LICENSE`, two roots, >25 MB, a `.pyc`, or mismatched filename
  fails with the right `ARTIFACT_*` id.
- ZIP with `0600` modes passes by default with a warning; `--strict-permissions`
  fails.
- `package --repo-check` fails if the **built** ZIP is invalid even when the source
  tree was valid.
- `validate --zip` never reads the source tree.
- JSON is stable and documented; exit code `0` pass, `1` blocking findings,
  `2` invalid input/tool error.

### 3.2 Portal security command

Keep `security` backward compatible; add a portal mode that delegates to the
analyzer adapters:

```bash
qgis-manage security --portal
# -> qgis-analyzer security . --deep --tools bandit,detect-secrets,flake8 --json
```

Do **not** reimplement Bandit/detect-secrets inside qgis-manage: the analyzer owns
tool adapters, qgis-manage only orchestrates. `--json` must be passed through
unchanged.

### 3.3 Metadata and docs

- Include `repository` as required under `--repo` (already) and warn when
  `qgisMaximumVersion < 4.0` or `supportsQt6` is present.
- Make `--require-docs` accept a configured entry (`docs_entry` or a glob such as
  `help/html/*/index.html`).

---

## 4. qgis-analyzer design

### 4.1 Flake8 adapter

New module `analyzer/flake8_audit.py`, modeled on `ruff_audit.py`:

```python
def run_flake8_audit(project_path: Path, *, config: Path | None = None) -> dict:
    cmd = [sys.executable, "-m", "flake8", str(project_path),
           "--format=json", "--output-file=/dev/stdout"]
    if config:
        cmd += ["--config", str(config)]
    ...
    return {"findings": [...], "exit_code": ..., "tool_unavailable": ...}
```

Normalize each finding to the analyzer schema:

```json
{"file": "gui/x.py", "line": 10, "col": 5, "code": "F811",
 "type": "FLAKE8_F811", "severity": "info", "message": "..."}
```

Flake8's JSON formatter comes from the `flake8-json` plugin. Declare it as an optional
extra (`qgis-analyzer[flake8]`) or fall back to parsing the default
`path:row:col: CODE text` output when the plugin is absent.

CLI:

```bash
qgis-analyzer analyze . --flake8            # default .flake8 if present
qgis-analyzer analyze . --linters ruff,flake8
```

Config/profile:

```toml
[tool.qgis-analyzer.linters]
flake8 = true
flake8_config = ".flake8"
```

Acceptance criteria: Flake8 absent → `tool_unavailable=true`, never a silent zero;
JSON findings merge into `ruff_findings`-style list; `--json` remains schema 1 (add
`flake8_metadata`).

### 4.2 Bandit and detect-secrets adapters

Extend `security` without breaking native rules:

```bash
qgis-analyzer security . --deep --tools bandit,detect-secrets --json
```

- Default (`--tools native`) keeps current behavior.
- `--tools bandit,detect-secrets` runs the real tools, parses JSON, maps:
  - Bandit HIGH → `portal_severity: critical`, `blocking: true`
  - Bandit MEDIUM/LOW → `warning` / `info`
  - detect-secrets any finding → `critical`, `blocking: true`
- Merge findings with the existing schema (`file`, `line`, `type`, `severity`,
  `message`), adding `tool`, `rule_id`, `portal_severity`, `blocking`.
- Add `--json` to `security` (currently missing).
- If a tool is unavailable: `tool_unavailable=true` and exit `2`, not a silent pass.

Acceptance criteria: a `shell=True` fixture blocks; a fake AWS key blocks;
clean plugin returns 0; native mode remains unchanged.

### 4.3 Portal profile

```toml
[tool.qgis-analyzer.profiles.portal]
linters = ["ruff", "flake8"]
security_tools = ["bandit", "detect-secrets"]
metadata_rules = true
fail_on = "critical"
```

`qgis-analyzer analyze . --profile portal` runs the exact portal set in one pass.

### 4.4 Metadata / QGIS 4 rules

Add to the metadata scope (not to the artifact layer):

- `METADATA_REPOSITORY`: `repository` required.
- `METADATA_VERSION`: numeric `X.Y.Z`.
- `METADATA_QGIS4`: `qgisMaximumVersion >= 4.0`.
- `METADATA_SUPPORTS_QT6`: deprecated flag warning.
- `METADATA_CATEGORY`: one of Raster/Vector/Database/Mesh/Web.

### 4.5 Fix the package-size rule

Current `analyzer/validators.py`:

```python
_MAX_PACKAGE_SIZE_MB = 20
if total_size_mb > _MAX_PACKAGE_SIZE_MB:
    errors.append(f"Package size ({total_size_mb:.2f}MB) exceeds the 20MB limit.")
```

It measures the **project directory**, so SecInterp fails at 65.9 MB because of
`docs/` and `tests/`. The portal limit is **25 MB on the ZIP**.

Recommended:

- Remove package-size enforcement from `analyze` (source tree is not a package), or
  keep it as `info` only.
- If a size check is kept, require an explicit ZIP path (`--artifact`) and use
  25 MB.

---

## 5. Cross-repo contract

- **No Python imports** between qgis-manage and qgis-analyzer; invoke CLIs.
- `schema_version` / `schema` stay `1`; new fields are additive.
- Severity enum: `critical` (blocking), `warning`, `info`.
- Exit codes: `0` clean, `1` findings, `2` invalid input/tool unavailable.
- `tool_unavailable` must be explicit; never convert a missing tool into zero
  findings.
- JSON field names are part of the contract; add tests that snapshot the envelope.

---

## 6. Migration in SecInterp

| Phase | Change | Removes |
| :--- | :--- | :--- |
| 1 | Manager `validate --zip` + `package` artifact check | `scripts/check_portal_package.py`, `make portal-check` becomes a thin wrapper |
| 2 | Analyzer `--flake8` + `security --tools` | `make flake8` body, `scripts/security_scan.py` |
| 3 | Manager `security --portal` + docs entry config | project-specific security command |
| 4 | Analyzer `--profile portal` | duplicated per-project tool flags |

Keep `make pre-release` as the composition point; project-specific exclusions and
thresholds remain in the plugin repository.

---

## 7. Priority

| Priority | Repository | Item |
| :---: | :--- | :--- |
| P0 | qgis-manage | `validate --zip` + artifact checks in `package --repo-check` |
| P0 | qgis-analyzer | Flake8 adapter |
| P0 | qgis-analyzer | Bandit/detect-secrets adapters + `security --json` |
| P1 | qgis-manage | Permission normalization, icon/README, docs entry |
| P1 | qgis-analyzer | Portal profile + metadata/QGIS 4 rules |
| P1 | qgis-analyzer | Fix 20 MB/project-dir package-size rule |
| P2 | both | Snapshot JSON schemas, `--fail-on`, config precedence |
