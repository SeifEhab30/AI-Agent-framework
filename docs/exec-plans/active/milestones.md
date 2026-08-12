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

## M7 — Doc-gardener automation (done, cron timing unverified)

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

Merged and live-tested (manual trigger): added a deliberately broken doc
link on `master`, confirmed the manual `workflow_dispatch` run found it
and created a `doc-gardener/report-*` branch with the fix, opened a real
PR (after discovering and fixing a repo setting gap — "Allow GitHub
Actions to create and approve pull requests" was off by default).

Attempted to also verify the *schedule* (cron) trigger itself fires
on its own within a tight window (first daily at 12:00 UTC, then moved to
11:05 UTC to expedite) — it did not fire within ~15 minutes of either
target time. GitHub does not guarantee scheduled workflow punctuality
(documented best-effort behavior, can silently skip a run during high
load), and there's no way to force or debug this from outside GitHub's
own infrastructure. Cron reverted to weekly: `0 9 * * 1` (Monday 09:00
UTC = Monday 12:00 GMT+3).

The bookmarks.md broken link mentioned above was already caught and
fixed by M9's agentic-loop run before the Monday cron got a chance to. A
fresh deliberately broken link is now left in
`docs/product-specs/notes.md` instead, so both the Monday 09:00 UTC
doc-gardener cron and the Monday 10:00 UTC agentic-loop cron have
something real to catch on their first unattended (non-manually-
triggered) runs.

**Status:** Core automation (detect → auto-fix → branch → PR) confirmed
working end-to-end via manual trigger — this is the part that matters.
The cron *schedule* trigger itself remains unverified as firing
correctly on its own for either workflow; next real signal is whether
next Monday's runs happen unattended and both produce PRs fixing the
notes.md link.

## M8 — More golden rules (done)

**Goal:** an outside assessment (ChatGPT, given a full framework rundown)
flagged that golden-rule coverage was thin — two rules demonstrate the
mechanism but aren't yet a real "taste layer." Cheapest gap to close.

Added two rules to `scripts/check_golden_rules.py`:
- No bare `except:` in domain code — swallows everything including
  `KeyboardInterrupt`/`SystemExit`, hides real bugs.
- No `print()` in domain code — should go through the `providers` logger
  instead, reinforcing the reuse-before-hand-rolling principle.

Verified: baseline clean run, then deliberately introduced both
violations in `widgets/service.py` in one function, confirmed both
detected with correct file/line, then reverted.

**Status:** Complete.

## M9 — Agentic maintenance loop (done)

**Goal:** close the biggest gap flagged by an external assessment: the
harness could only flag issues, not act on them. Build a scheduled agent
that reads doc-gardener/golden-rules findings, investigates, makes a
targeted fix, validates, and opens a PR — an actual self-correcting loop,
not just more static tooling.

Built as a Claude Code cloud routine (`RemoteTrigger`/`schedule`), weekly
Monday 10:00 UTC (13:00 GMT+3, ~1hr after the doc-gardener GitHub Actions
cron), model claude-sonnet-5, scoped to Bash/Read/Write/Edit/Glob/Grep
against the repo. Prompt instructs it to: read `MAP.md` and
`docs/references/conventions.md` for house rules, run
`doc_gardener.py`/`check_golden_rules.py`, fix only what those two flag
(noting anything else it notices without touching it), run the full
validation suite, then commit/push/PR — never merge itself, never push
directly to `master`.

Setup required making the repo public — Code routines' repository picker
only lists repos the routine's GitHub integration can see, and that did
not include this private repo despite GitHub being generally connected;
no working per-repo write-access grant was found for private repos after
checking connectors, installed GitHub Apps, and authorized GitHub Apps.

First manual run got through investigation, fix, and full validation
correctly, but both `git push` and the routine's GitHub MCP tool returned
`403 Resource not accessible by integration` — a real write-access gap
with no user-fixable setting found. The agent handled this well: it
reported the blocker honestly instead of working around it. A second
manual run shortly after succeeded end-to-end — found the same
deliberately-left broken link, fixed it, validated, pushed
`agentic-maintenance/2026-08-12`, and opened a real PR, merged by a
human. Cause of the first run's failure vs. the second run's success is
unconfirmed (possibly permission propagation delay) — worth treating as
a known reliability caveat, not a fully resolved issue.

**Status:** Complete. Full loop (investigate → fix → validate → PR)
confirmed working end-to-end via manual trigger and a real merged PR.
Weekly schedule trigger (Monday 13:00 GMT+3) itself remains unverified,
same caveat as M7's cron.

## M10 — Behavioral bug detection + scope guard (in progress)

**Goal:** M9 proved the loop can act on doc-gardener/golden-rules
findings — pattern matches, not judgment. An external assessment pointed
out this doesn't prove the agent can find a real logic bug nothing else
catches. Test that, while adding a mechanical backstop for the wider
scope this requires (per the same assessment's Gap #5: nothing currently
stops the agent from touching files outside a finding's scope except its
own instruction-following).

**The bug:** `widgets/service.py` `toggle_done` changed from
`self._repo.set_done(widget_id, not widget.done)` to
`self._repo.set_done(widget_id, True)` — always marks done, never
un-marks. Confirmed this passes ruff, pytest (existing `test_toggle_done`
only checks `False → True`, never toggles twice), and
`check_golden_rules.py` — genuinely invisible to every current automated
check, only findable by comparing behavior against
`docs/product-specs/widgets-todo.md` ("Toggle a widget's done state").

**The scope widening:** routine prompt updated to also do a bounded
code-health review — read each domain's product-spec, compare against
its `service.py`, and if a discrepancy is found, write a test proving it
and fix the implementation, in addition to the existing
doc-gardener/golden-rules handling. Explicit file-scope stated in the
prompt (only `service.py`/`test_service.py` per domain, plus the
existing doc-gardener/golden-rules targets) — anything needed outside
that scope must be reported, not touched. Diff scope currently checked
manually before merge, pending a mechanical version (see backlog).

**Status:** Bug merged to master. Routine prompt update and manual
trigger pending.

## Backlog (unscheduled, not yet milestones)

(none — all four original practices, CI/branch-protection hardening, and
the agentic maintenance loop are now built and verified)
