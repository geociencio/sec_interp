# User Guide Conventions

> Authoring and image conventions for the SecInterp **User Guide**.
> See also [DOCS_STYLE_GUIDE.md](DOCS_STYLE_GUIDE.md) and [DOCS_INDEX.md](DOCS_INDEX.md).

## 1. Where things live

| Item | Location |
|------|----------|
| Source document | [`docs/source/USER_GUIDE.md`](source/USER_GUIDE.md) |
| Images | `docs/source/images/` |
| Reference in markdown | `images/<file>.png` (relative to `docs/source/`) |
| Translations | `docs/locales/<lang>/LC_MESSAGES/USER_GUIDE.po` |

Do **not** edit `help/html/` or `docs/code_walkthrough*/` (generated). Edit the source and rebuild.

## 2. Image naming

Use a `prefix_` + descriptive, lowercase, underscore-separated name:

| Prefix | Use for | Example |
|--------|---------|---------|
| `workflow_NN_` | Sequential tutorial steps (zero-padded) | `workflow_03_select_section_line.png` |
| `ui_` | General interface screenshots | `ui_main_dialog.png` |
| `guide_` | Section/feature setup screenshots | `guide_dem_setup.png`, `guide_drillhole_collars.png` |
| `guide_<tool>_N` | Sequential steps of a tool | `guide_interpretation_tool_1.png` |
| `<area>_section_preview` | Rendered section preview | `geology_section_preview.png` |
| `feature_` | Highlighted single feature | `feature_3d_export.png` |

- Sequential images **must** be zero-padded and consecutive (`_01`, `_02`, …) so they sort correctly.
- Use `.png`. Prefer a width of ~1200–1600 px (retina-friendly) and keep file size < ~500 KB.
- Reuse existing screenshots when possible; delete superseded files (`git rm`) to avoid dead assets.

## 3. Markdown insertion pattern

```markdown
![Short alt text](images/guide_dem_setup.png)
*Figure caption (Step 1).*
```

- The **alt text** and the **caption** are user-facing and therefore translatable.
- Put the image on its own line, the caption on the next line in italics.
- Keep captions short and numbered when part of a sequence.

### Placement by section

| USER_GUIDE section | Typical images |
|--------------------|----------------|
| 2. The Main Window | `ui_main_dialog*.png` |
| 3. Step 1 DEM | `guide_dem_setup.png`, `dem_section_preview.png` |
| 3. Step 2 Section Line | `guide_section_setup.png` |
| 3. Step 3 Geology | `guide_geology_setup.png`, `geology_section_preview.png` |
| 3. Step 4 Structure | `guide_structure_setup.png`, `structure_section_preview.png` |
| 3. Step 5 Drillhole | `guide_drillhole_{collars,survey,intervals}.png` |
| 3. Step 6 Preview | `preview_all.png`, `preview_panels_collapsed.png` |
| 4.1 Interpretation | `guide_interpretation_tool_{1,2,3}.png` |
| 4.4 Settings | `guide_settings_{default,advanced,info}.png` |
| 5.4 Tools | `guide_measure_tool.png` |

## 4. After adding/updating images

```bash
make docs-i18n-update   # add new msgids to the .po catalogs (prunes obsolete)
make docs-check         # links, refs, mirror drift
make docs               # build + publish (or a local en/es build to preview)
```

- Translate the **new caption/alt entries** in `docs/locales/es/LC_MESSAGES/USER_GUIDE.po`
  to keep `es` at the ≥80% publish threshold (`make docs-i18n`).
- Verify rendering with a quick local build:
  ```bash
  uv run sphinx-build -b html docs/source /tmp/ug -D language=en
  uv run sphinx-build -b html docs/source /tmp/ug_es -D language=es
  ```

## 5. Checklist

- [ ] Image saved in `docs/source/images/` with a convention-compliant name.
- [ ] Referenced as `images/<file>.png` in `docs/source/USER_GUIDE.md`.
- [ ] Alt text + caption present (translatable).
- [ ] Sequential images zero-padded and consecutive.
- [ ] Superseded images removed.
- [ ] `make docs-i18n-update` run; new entries translated (at least `es`).
- [ ] `make docs-check` passes.
