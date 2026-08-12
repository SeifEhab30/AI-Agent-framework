# Milestones

Verified: 2026-08-12

Tracks progress on the Codex-style workflow scaffold, one milestone at a
time. This is a single running log, not one file per milestone — update
status and add the next milestone in place as work lands.

## M1 — Scaffold + reference domain (done)

- MAP.md + docs/ structure
- Layered `widgets` domain (types/config/repo/service/runtime/ui) with
  `providers/` and `platform/`
- import-linter layering + forbidden contracts, enforced and verified
- `doc_gardener.py` and `check_golden_rules.py`, wired into pre-commit
- App manually verified end-to-end (create/list/toggle) via Swagger UI

**Status:** Complete.

## M2 — Second domain: notes (done)

**Goal:** prove the layering/providers convention actually generalizes
past one domain, not just that it worked once.

Added a `notes` domain (title + body, deliberately unrelated to widgets —
no cross-domain imports) that copies the `widgets/` folder structure
(`types.py` → `ui.py`) exactly:
- reuses `providers/` and `platform/` without modification
- has its own import-linter layers + forbidden contracts, plus a new
  `independence` contract ensuring `widgets` and `notes` never import
  each other
- has its own `docs/product-specs/notes.md`
- manually verified end-to-end (create/list/update) via its own Swagger UI

Widgets and notes run as two independent FastAPI apps on separate ports
(`todoapp.widgets.ui:app`, `todoapp.notes.ui:app`) rather than one combined
app — deliberate for now, since the focus is the framework, not the
product. Combining them into one entrypoint is deferred, not forgotten;
see backlog.

**Status:** Complete. Pattern confirmed to generalize with zero
modification to `providers/`/`platform/`.

## M3 — Third domain: bookmarks (done)

**Goal:** three domains is the real test of "generalizes" — two could
still be coincidence.

Added a `bookmarks` domain (url + title, independent of widgets and
notes), same six-layer structure:
- reuses `providers/` and `platform/` without modification
- own layers + forbidden contracts; `independence` contract extended to
  cover all three domains pairwise
- own `docs/product-specs/bookmarks.md`
- verified: ruff, import-linter (7 contracts kept), pytest (12 passed),
  golden-rules all clean

**Status:** Complete.

## Backlog (unscheduled, not yet milestones)

- CI (currently pre-commit-only; `--no-verify` can still bypass checks)
- Doc-gardener auto-fix or PR automation (currently report-only)
- Combined entrypoint mounting all domains under one app/port
