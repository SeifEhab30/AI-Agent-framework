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

## M4 — CI (done)

**Goal:** close the `--no-verify` gap — pre-commit only enforces rules on
machines where hooks are installed and not bypassed; CI enforces them
regardless.

- Added `.github/workflows/ci.yml`: runs ruff, ruff format check,
  import-linter, pytest, golden-rules on every push/PR
- Added `doc_gardener.py` as a non-blocking CI step (reports only, doesn't
  fail the build — revisit once it can auto-fix instead of just flag)
- Repo pushed to `github.com/SeifEhab30/AI-Agent-framework`
- First CI run confirmed green on GitHub Actions

**Status:** Complete. CI is live and enforcing on every push.

## M5 — Branch protection (done)

**Goal:** make the CI gate binding, not just informational — without
this, CI could go red on `master` and nothing would stop it.

- Branch protection rule added on `master` in GitHub repo settings,
  requiring the `checks` CI job to pass before merging
- "Include administrators" enabled — confirmed by a rejected direct push
  (`GH006: Protected branch update failed`, no passing check for that
  commit) — the rule now blocks admins too, not just external PRs
- Going forward: direct `git push` to `master` no longer works. Changes
  need a feature branch + PR, CI runs there, merge once green.

**Status:** Complete.

## M6 — Combined entrypoint (done)

**Goal:** run the product as one service instead of three independent
demo apps, without changing any domain's internal structure.

Added `src/todoapp/app.py`: imports each domain's `build_runtime()` and
`build_router()`, mounts all three routers under one `FastAPI()` instance.
No domain code was touched — this is pure composition sitting outside the
domain folders, same as `runtime.py`/`ui.py` do within a domain.

- Verified: import-linter still shows 7/7 contracts kept (new module
  doesn't need its own contract — it's not a domain and doesn't get
  imported by one)
- Verified live: created a widget, a note, and a bookmark all through the
  same running instance (`uvicorn todoapp.app:app`), confirmed via
  `app.openapi()['paths']` that all six routes are mounted
- Each domain remains independently runnable via its own `<domain>.ui:app`

**Status:** Complete. Merged via PR, CI green, branch protection exercised
end-to-end.

## M7 — Doc-gardener automation (in progress)

**Goal:** move doc-gardener from "run it by hand and hope someone reads
the output" to actually catching drift on its own — without letting an
automated process silently rewrite doc content.

Scope, deliberately narrow:
- `doc_gardener.py --fix` auto-fixes exactly one thing: a markdown link
  `[text](path)` where `path` no longer exists gets unlinked to plain
  text. Nothing else is ever auto-edited — a stale `Verified:` date is
  still report-only, since deciding a doc is still accurate needs a human
  to read it, not a date bump.
- Always writes `docs/quality-score/report.md` with the full findings.
- New `.github/workflows/doc-gardener.yml`: runs weekly (Monday 06:00
  UTC) plus on-demand via `workflow_dispatch`. If `--fix` changed
  anything, it commits to a new branch and opens a PR using the
  Actions-provided `GITHUB_TOKEN` (no secrets needed from the user).
  Nothing merges automatically — same branch protection + CI gate as
  every other change.

Verified locally: deliberately added a broken markdown link, confirmed
it's flagged without `--fix`, confirmed `--fix` unlinks it and only it
(surrounding prose untouched), confirmed the report file updates
correctly, then removed the test link.

**Status:** Built and verified locally; pending branch + PR to merge, and
a manual `workflow_dispatch` run on GitHub to confirm the PR-opening step
actually works (the cron trigger itself can't be tested until it's due).

## Backlog (unscheduled, not yet milestones)

(none — all four original practices plus CI/branch-protection hardening
are now built)
