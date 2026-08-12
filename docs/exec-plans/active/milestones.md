# Milestones

Verified: 2026-08-12

Tracks progress on the Codex-style workflow scaffold, one milestone at a
time. Update status and add the next milestone as work lands. Move a
milestone to `docs/exec-plans/completed/` once it's done and no longer
needs to stay "active."

## M1 — Scaffold + reference domain (done)

- MAP.md + docs/ structure
- Layered `widgets` domain (types/config/repo/service/runtime/ui) with
  `providers/` and `platform/`
- import-linter layering + forbidden contracts, enforced and verified
- `doc_gardener.py` and `check_golden_rules.py`, wired into pre-commit
- App manually verified end-to-end (create/list/toggle) via Swagger UI

**Status:** Complete.

## M2 — Second domain (in progress)

**Goal:** prove the layering/providers convention actually generalizes
past one domain, not just that it worked once.

Add a second domain (name TBD) that copies the `widgets/` folder
structure (`types.py` → `ui.py`) exactly, and:
- reuses `providers/` and `platform/` without modification
- passes the same import-linter layers + forbidden contracts, extended to
  cover the new domain
- gets its own `docs/product-specs/` entry and a design-doc if any
  deviation from the widgets pattern is needed

If anything about `providers`/`platform` turns out to be widgets-specific,
that's the signal to fix here — before a third domain compounds the issue.

**Status:** Not started.

## Backlog (unscheduled, not yet milestones)

- CI (currently pre-commit-only; `--no-verify` can still bypass checks)
- Doc-gardener auto-fix or PR automation (currently report-only)
