# Next Steps - SecInterp

## 1. i18n Expansion (Phase 2 - Market Gap)
- [ ] **Swedish (sv) & Danish (da)**: Follow the `/i18n-maintenance` workflow to complete the Northern European cluster.
- [ ] **User Feedback**: Monitor downloads from PL, NL, and FI to validate the impact of new translations.

## 2. Infrastructure
- [ ] **Automated CI Checks**: Integrate `i18n_diagnostic.py` into the CI pipeline to alert on untranslated strings in PRs.

## 3. Documentation
- [ ] **Help System**: Regenerate HTML help with `make docs` to include updated i18n information in the User Guide.

**Retomar sesión con**: `./scripts/update_ai_ctx.sh` (o `uv run ai-ctx analyze --path .`) para sincronizar el estado.
