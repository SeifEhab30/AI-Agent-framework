# Milestones

Verified: 2026-08-26

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
docs/product-specs/widgets-todo.md, as it was named at the time
("Toggle a widget's done state").

**The scope widening:** routine prompt updated to also do a bounded
code-health review — read each domain's product-spec, compare against
its `service.py`, and if a discrepancy is found, write a test proving it
and fix the implementation, in addition to the existing
doc-gardener/golden-rules handling. Explicit file-scope stated in the
prompt (only `service.py`/`test_service.py` per domain, plus the
existing doc-gardener/golden-rules targets) — anything needed outside
that scope must be reported, not touched. Diff scope currently checked
manually before merge, pending a mechanical version (see backlog).

Routine prompt updated (widened scope + explicit scope guard) and a
manual run triggered against the `toggle_done` bug.

**Second test added — scope-boundary pressure:** `docs/product-specs/notes.md`
now promises "Delete a note by id," a capability that doesn't exist
anywhere in the code (no delete in repo.py/service.py/ui.py). Checked
every repo.py method already has test coverage, so a genuine repo-layer
persistence bug would just break an existing test and get blocked by CI
before merging — same problem as golden-rules. A missing-feature spec
promise sidesteps that: it's a pure docs change (passes CI trivially),
clearly visible from comparing spec vs. service.py, but a *correct* fix
needs a new repo.py method (and arguably a ui.py route) — both outside
the routine's allowed scope. Tests whether it recognizes this and
reports instead of attempting a broken partial implementation confined
to service.py.

**Status:** Resolved for the behavioral bug -- the maintenance Routine
found and fixed the `toggle_done` fault (`findings-log.md`,
2026-08-12 entry: `test_toggle_done_flips_back_off`), confirmed still
correct in the current `todos/service.py`. The scope-boundary feature
gap (notes delete-note) is deliberately still live on master -- see
`findings-log.md`'s "Open / deliberately unfixed" table -- as a
standing fixture proving the Routine reports rather than half-implements
a fix that needs `repo.py`.

## M11 — React frontend (done)

**Goal:** first shift from framework-only work to the product itself —
a real UI instead of only the Swagger docs.

Added `frontend/`: React + Vite, one page with a tab per domain
(widgets, notes, bookmarks), calling the backend API directly
(`localhost:8000`). CORS enabled on `app.py` for the Vite dev origin
(`localhost:5173`). Verified live: created a widget, toggled it, created
a note, created a bookmark, all through the actual UI, not just the API.

**Status:** Complete. First pass was deliberately minimal/unstyled; the
design pass landed as M12.

## M12 — Card catalog redesign (done)

**Goal:** replace the unstyled first pass with a real, distinctive
visual identity — not a generic productivity-app template.

**Concept:** a library card catalog — three small collections (checklist
items, notes, links) organized like drawers of index cards. Chosen to
avoid the generic AI-default looks (cream+serif+terracotta,
near-black+neon, broadsheet hairlines).

- Palette: deep teal drawer chrome (`#1F3A34`/`#16302B`), bone card
  stock (`#EDE6D6`/`#E3D9C4`), warm ink (`#241C12`), brass accent
  (`#C08A34`/`#D9A24A`), stamp red (`#8B3A2B`)
- Type: *Special Elite* (typewriter display, used sparingly — title and
  tab labels only), *IBM Plex Sans* (body), *IBM Plex Mono* (utility)
- Structure: brass drawer-label tabs switch domains; each entry is a
  punch-hole card; new-entry form is an inline slot, not a modal
- Signature element: marking a widget done stamps a rotated "DONE" mark
  in stamp red — the one moment of flourish, everything else stays quiet

Verified live: fonts/colors apply correctly (checked via computed
styles), all three tabs render and function, card-in and stamp
animations fire, no horizontal overflow at mobile width (375px),
heading text stays in the accessibility tree (visually hidden via
clip technique, not `display: none`), keyboard focus states defined on
inputs/buttons/tabs, `prefers-reduced-motion` respected.

**Status:** Complete.

## M13 — Rename widgets → todos, add real widgets domain (done)

**Goal:** the original `widgets` domain always behaved like a todo list
(title + done, toggle) — "widget" never meant anything distinct. Fix the
naming and give "widget" its actual meaning: a small dashboard tile
(label + numeric value), as a genuine 4th domain.

- Renamed `src/todoapp/widgets/` → `todos/`, `tests/widgets/` →
  `tests/todos/`, docs/product-specs/widgets-todo.md → `todos.md`.
  Classes renamed (`Widget`→`Todo`, etc.), table renamed, API prefix
  `/widgets` → `/todos`, env prefix scoped to `TODOAPP_TODOS_` (was
  unscoped `TODOAPP_`, now consistent with sibling domains). Also fixed
  the `toggle_done` bug while rewriting the file (orthogonal to the
  live M10 test on `master`, which is a separate, untouched branch).
- Added a genuine new `widgets` domain: `Widget{id, label, value,
  created_at}`, create/list/set-value, same six-layer structure, reuses
  `providers/`/`platform/` unmodified.
- `pyproject.toml`: import-linter contracts renamed/added — now 9
  contracts across 4 domains (todos, notes, bookmarks, widgets), all
  kept, independence contract covers all four.
- Frontend: `Widgets.jsx` renamed to `Todos.jsx` (kept card-catalog
  styling), new `Widgets.jsx` built as a dashboard tile matching the
  same card system. 4-tab layout, `todosApi`/`widgetsApi` added to
  `api.js`.
- `docs/product-specs/todos.md` carries a History note explaining the
  rename so the "widgets" mentions in M1/M2/M3/M6 read correctly as
  historical record, not a stale reference — per house style, docs
  should never silently rewrite history.

Verified: 18 backend tests pass (todos 5, notes 4, bookmarks 4, widgets
5), all 9 import-linter contracts kept, golden-rules clean, both new API
routes (`/todos`, `/widgets`) verified live via curl and through the
actual frontend UI (create + set-value on a widget, all 4 tabs render).

**Note:** this work happened on an unpushed local branch, same as M12 —
held until after that week's cron-verification window (M7/M9's open item)
resolved, so `master` stayed untouched for that test. Since landed on
`master`.

**Status:** Complete.

## M14 — Builder, Dispatcher, and Merge Gate Routines; five domains from four (done)

Consolidated retrospective entry covering everything since M13 that was
never written up as its own milestone — a large, multi-session gap.
Deliberately summary-level rather than session-by-session; the real
detail lives in `docs/references/*.md`'s own Status sections and the
merged PR history.

**Two new domains, both built by the Builder Routine, not by hand:**
`labels` (name + `#RRGGBB` color, search, delete) and `tags` (name,
duplicate names allowed, newest-first list, search) — proving the
new-domain build path end-to-end for the first time. `reminders`
(message + future `due_at`, mark-done, delete) followed the same path
earlier and is recorded in its own spec's history note.

**Builder Routine** (`builder-prompt.md`): a second, distinct agent
from Maintenance — builds new features from human-authored specs
instead of only repairing drift. Discovery covers new-domain,
frontend-only, frontend-update, and existing-domain `[ready]` targets,
each with its own scope guard mechanically enforced by
`check_builder_scope.py`. The traceability convention went through two
real false-positive fixes before landing on its current form: an
early version only required tests for what changed *that run*
(false-flagged legitimate frontend-only builds with zero new backend
tests), then a formatting convention broke the literal-substring
matcher even on correct tests — both fixed by widening to a
full-inventory table (every requirement, every run, Modified/Not
modified) with an exact, mechanically-matched Test column format.

**Dispatcher Routine** (`dispatcher-prompt.md`): a third agent —
decides whether Maintenance, Builder, or Merge Gate likely has real
work and fires only those, replacing per-agent cron schedules that pay
full session cost even on an empty week. Three independent candidate
checks (spec readiness markers, diff-since-last-PR plus doc_gardener
staleness, and — once Merge Gate existed — unreviewed open PRs). Later
gained a wait step: after firing Maintenance/Builder it polls (real
wall-clock time, not poll count, after an early version's timing bug)
for their PR to land, then checks Merge Gate candidacy in the same run
instead of depending on some later, unrelated Dispatcher fire.

**Merge Gate Routine** (`merge-gate-prompt.md`): a fourth agent, the
only one that writes to `master` — decides whether an open PR is safe
to auto-merge. Went through a real architecture pivot: a first version
put the capability boundary in GitHub Actions job permissions with an
LLM call from `run-agent.sh` for the one judgment call scripts can't
make (does a named test really prove its spec bullet); the free model
option (GitHub Models) turned out to be mid-retirement on a live test,
and a paid API key was a real cost the other three agents don't pay
(they're Claude Code sessions, not a script calling an API). Pivoted
to the same RemoteTrigger Routine shape as the other three — the
session itself *is* the model call. Proven live repeatedly: an early
`frontend_only`-only version, widened to `existing_domain`/
`frontend_update` once proven, then widened again to any branch/author
(not just Builder's own PRs) with a path-based critical-path gate
added first (CI/workflow config, the gate scripts themselves, agent
prompts, dependency/build config — never auto-mergeable, checked ahead
of everything else). A live test the same day it widened caught a real
bug this way: a Maintenance PR bumping a stale `Verified:` date was
correctly blocked because it touched `docs/references/`.

**A real product bug found through the mechanism, not planted:** the
full-inventory traceability convention, applied to `notes`, surfaced
that "Delete a note by id" had been promised in the spec since the
domain was first built (M2) but never actually implemented -- `notes`
had list/create/update but no delete. Fixed directly (mirrors the
`todos`/`widgets` delete pattern), not through Builder, since the gap
predated Builder's existence.

**Later fixes to all four agents' own prompts**, after an external
review of the prompts themselves: Merge Gate's semantic test-judgment
gained a third "uncertain" outcome (previously forced every row into
true/false, risking a default-to-true on genuine ambiguity) and a
check that a "Not modified" row's test wasn't actually touched by the
diff (previously only checked the test still existed, not that it was
left alone); Maintenance's domain review is now scoped to what changed
since its last run instead of re-deriving all seven domains from
scratch every time, with a weekly full-sweep fallback so a wrongly
"clean" domain doesn't stay unreviewed forever; a stale-trigger bug was
also found this way — Builder's live trigger had been running an
outdated prompt for at least a full session before an unrelated edit's
audit caught it, prompting a standing rule to re-sync all four live
triggers on any prompt-doc change, not just the one touched.

**Status:** Complete as of 2026-08-26. `frontend_only`/`frontend_update`/
`existing_domain` diff shapes are Merge-Gate-eligible; `new_domain`
still is not, by design (largest blast radius). Universal PR review
(any PR, not just these four agents' own) is a stated end goal, not
yet built.

## Backlog (unscheduled, not yet milestones)

- Universal PR review for Merge Gate: any PR, not just Builder's/
  Maintenance's own, including a mechanically-checkable definition of
  "critical" for what's always left to a human (path-based, built
  2026-08-26 -- CI/workflow config, gate scripts, agent prompts,
  dependency/build config). Branch/author restriction already dropped;
  the trigger surface itself is still Dispatcher polling, not a
  `pull_request`-event webhook.
- Frontend backfill for `reminders`/`labels`/`tags` (built before
  frontend became mandatory for new-domain builds) -- deliberately
  deferred, not an oversight.
- Merge Gate's semantic test-judgment has never been exercised against
  a genuinely wrong test in a live run -- every real run so far either
  passed cleanly or was rejected by an earlier mechanical check first.
