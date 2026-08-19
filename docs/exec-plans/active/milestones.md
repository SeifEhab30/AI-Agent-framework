# Milestones

Verified: 2026-08-19

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

## M10 — Behavioral bug detection + scope guard (done)

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

Routine's next run resolved both: correctly found the `toggle_done`
behavioral bug (spec said toggle, code always set `True`), wrote a
failing test, fixed it, and separately recognized the notes.md
missing-delete promise needed `repo.py`/`ui.py` changes outside its
`service.py`+`test_service.py` scope guard — reported it in the PR
instead of attempting a broken partial fix, exactly the discipline the
test was designed to check.

**Status:** Complete. Both test faults resolved correctly by the
routine: the fixable bug was fixed with a proving test, the
out-of-scope feature gap was honestly declined rather than
partially/incorrectly patched.

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

## M14 — Tier-3 recurrence proof (done)

**Goal:** M10 proved the routine can find and correctly scope a real
behavioral bug. What was never tested: the recurrence rule itself — that
a defect *category*'s second occurrence produces a proposed golden rule,
not just another point fix. A one-off fix proves detection; a proposed
rule proves the loop actually learns from repetition, not just repairs
each instance in isolation.

Planted a second occurrence of the `behavior-spec-mismatch` category (the
same category `toggle_done` in M10 belonged to) as a fresh, different
bug, and fired the routine. It correctly:
- found the planted defect via its own spec-vs-code comparison
- wrote a failing test proving the defect, then fixed the implementation
- checked `findings-log.md`, recognized this was the category's second
  logged occurrence
- proposed golden rule 6 in the same PR, verified it passes clean on the
  fixed repo and actually fails when the defect is reintroduced (stated
  both in the PR, same discipline required by the routine's own prompt)

PR #25 — proposed rule reviewed and merged by a human.

**Status:** Complete. Full loop (detect → fix → recognize recurrence →
propose a new mechanical check → prove it catches the target defect)
confirmed working end-to-end, not just designed.

## M15 — Builder Routine (feature development, not maintenance) (done)

**Goal:** every milestone so far proved the maintenance Routine can
*preserve* what exists — find drift, fix it, decline what's out of
scope. Nothing yet proved an agent could *build* something new. Close
that gap with a second, fully separate agent, deliberately not a mode
switch on the proven maintenance Routine, so a bug in the far
less-proven builder can never contaminate maintenance's earned trust.

**Design, reviewed against three external assessments before building:**
- `docs/references/builder-prompt.md` — mirrors `routine-prompt.md`'s
  structure (Verified date, Status section, versioned Prompt body).
  Phase 1 only: the human always writes the spec first
  (`docs/product-specs/<domain>.md`, `Status: Ready for implementation`
  for a new domain, `[ready]`-tagged bullet for an existing one); the
  Builder never authors a spec itself in v1.
- **Discovery**: new-domain candidates preferred over existing-domain;
  exactly one target built per run; multiple candidates named as "also
  found, not built" in the PR; nothing ready-marked or spec genuinely
  ambiguous → stop, no branch, no PR.
- **Scope**: full six-layer authority (types→config→repo→service→
  runtime→ui) for its one target only — a materially larger grant than
  maintenance's `service.py`-only boundary, which is exactly why it's a
  separate agent and separate trust model.
- **Traceability**: every spec requirement needs a named, passing test;
  PR description includes a requirement→test table.
- **`scripts/check_builder_scope.py`** — the scope guard isn't just a
  prompt promise. Structural checks (via `tomllib`, same technique
  `check_golden_rules.py` already used) that `pyproject.toml` contracts
  are only ever appended/superset-extended, never edited; a set-based
  domain-touch count (more than one domain directory per run fails);
  forbidden-path list covering maintenance's own territory and the
  script's own file. Wired into CI on any `agentic-build/*` branch, not
  just self-reported by the Builder.
- New `RemoteTrigger` (`trig_01H6QZXRUi4S2zdY2X9R2ZPy`), manual
  `action=run` only, no cron — same "prove it by hand before trusting a
  schedule" bar M9 cleared before its own cron was trusted.

**First real run (2026-08-17):** target spec `docs/product-specs/reminders.md`
(message + future-dated `due_at`, list, mark-done, delete) — a genuinely
new domain, human-written, not scripted for the Builder. Discovery
correctly found it as the sole ready-marked target. Built all six
layers, 8 tests covering all 4 spec behaviors, zero scope violations
(`check_builder_scope.py` clean), honest PR (frontend explicitly named
as out of scope, not silently missing). Merged as PR #31.

**Real gap found in human review, not by any mechanical gate:** a
naive-vs-aware `datetime` comparison — a `due_at` submitted without a
UTC offset would crash with `TypeError` instead of the intended
`ValidationError`. No golden rule or scope check could have caught
this; it required an actual human reading the logic. Fixed in a
follow-up commit on the same PR, validating the plan's own stated
residual-gap philosophy: mechanical gates catch structural violations,
not every logic bug.

**Negative-capability checklist** (per the plan's own bar, mirroring
M10's out-of-scope-decline test): confirmed via the actual PR #31 diff,
not just trusted — no existing domain's business logic touched,
`routine-prompt.md`/`findings-log.md`/`check_golden_rules.py`/
`doc_gardener.py` untouched, `frontend/` untouched, no import-linter
contract modified (only appended), target spec's *requirements*
unchanged (only `Verified:` bumped), not self-merged/self-approved,
every spec bullet had a named covering test.

Both prompts (`routine-prompt.md`, `builder-prompt.md`) later
token-trimmed (~22-28%) with word-for-word instruction/permission
equivalence verified before syncing to the live triggers (PR #32).

**Status:** Complete. Full arc (design → mechanical scope guard → first
real build on an unscripted human spec → real bug found and fixed in
review → negative-capability verified against the actual diff) proven,
not just planned.

## M16 — Standing branches, marker-clearing, visible ambiguity flagging (done)

**Goal:** both routines previously created a fresh, uniquely-timestamped
branch every single run (`agentic-maintenance/<timestamp>`,
`agentic-build/<timestamp>-<domain>`) and re-evaluated every spec/marker
from scratch each time. Three real, user-identified gaps this produced:
manual PR-by-PR review overhead scaling with every run; already-built
Builder targets (and already-resolved ambiguous specs) getting
silently rediscovered every run with no memory of prior evaluation; and
an ambiguous/contradictory spec's stop condition leaving zero trace
outside the run transcript, discoverable only by reading a log a human
had to think to go check.

**Standing branches:** replaced per-run branch names with one fixed
branch per routine (`agentic-maintenance/standing`,
`agentic-build/standing`). A run whose branch's prior PR is already
merged recreates it fresh from `origin/master`; a run whose branch still
has an open PR merges `origin/master` in first (**this run's own new
work wins any conflict** — corrected mid-session after an initial draft
had the direction backwards) and adds its commits to that same PR,
rewriting the PR description to cover every run folded into it, rather
than opening a new PR each time.

**Builder marker-clearing:** after a successful build, the Builder now
deletes `Status: Ready for implementation` (new domain) or strips
`[ready]` from the one bullet it built (existing domain) as part of its
own PR. Required a companion fix in `check_builder_scope.py`
(`check_target_authorized`/`check_traceability` now read the target
spec from `base`/origin-master via a new `read_spec_at()` helper, not
the working tree) — otherwise the Builder clearing its own marker would
fail its own scope check on its own PR.

**Visible ambiguity flagging:** an ambiguous/contradictory spec now
gets marked `Status: Blocked -- ambiguous` plus a `## Needs resolution`
section quoting the exact conflict — a real, reviewable diff instead of
a buried transcript line. Deduped: an already-`Blocked` spec is skipped
silently on later runs; if the run built something else, the flag rides
along as a one-line PR-description reminder rather than its own PR; a
dedicated flag-only PR only fires when there's nothing else to build.

**Real gap found live, fixed same-day:** after `tags.md`'s direct-negation
uniqueness contradiction was resolved by a human, the remaining
list-order contradiction ("alphabetical" vs. "creation order,
recent-first" — two bullets about the *same* operation, not literal
opposites) wasn't caught by the original ambiguity rule. The Builder
built both as separate methods and silently guessed "recent-first"
meant descending order (PR #41) instead of flagging the conflict.
Discovery rule 5 tightened to explicitly cover same-operation conflicts,
not just direct negations, and to explicitly forbid resolving ambiguity
by building every reading as a separate method or guessing an unclear
phrase's meaning. `tags.md` itself fixed for real afterward (PR #44):
creation-order listing only, alphabetical removed from both code and
spec.

**Proven live, not just designed** — each routine fired twice in
sequence against real, deliberately staged fixtures:
- Builder run 1: correctly built the sole valid target (widgets
  delete-by-id, tagged `[ready]` for the test) on a freshly created
  `agentic-build/standing`, PR #49.
- Builder run 2 (before #49 was merged): correctly found nothing new to
  build — every other candidate was either stale-but-already-built or
  the genuinely ambiguous `tags.md` — made zero commits, stayed silent,
  left PR #49 untouched. Confirms the "quiet when nothing found" path
  and a no-op branch merge.
- Maintenance run 1: found and fixed a planted falsy-guard bug in
  `notes/service.py` (`update_body` no-opped on an empty-string body,
  same shape as an earlier widgets bug) on a freshly created
  `agentic-maintenance/standing`; recognized the recurrence and proposed
  golden rule 7 (`check_falsy_guarded_repo_write`), verified it catches
  both the notes and widgets defect shapes. PR #50.
- Maintenance run 2 (before #50 was merged): found genuinely new,
  unplanted work (`doc_gardener.py` staleness on `milestones.md`/
  `conventions.md`, this time run with full git history) — added a
  second commit to the same branch, fast-forward pushed, and rewrote PR
  #50's description to summarize both runs together. This is the proof
  that was missing before this milestone: accumulation onto an
  already-open PR confirmed actually working, not just designed.

**Also fixed:** a real bug introduced mid-session — an earlier edit had
accidentally deleted the `## Prompt` section header from
`builder-prompt.md`; caught before syncing to the live trigger (PR #47).
Both triggers re-synced to the final, merged prompt content afterward.

Separately verified the repo's non-agentic `doc_gardener.yml` GitHub
Actions cron (distinct from both Routines — no agent involved, just
`python scripts/doc_gardener.py --fix` on a schedule): planted a dead
markdown link, confirmed the scheduled run (which itself fired ~30
minutes after its exact cron time, a live demonstration of GitHub's
documented best-effort scheduling) correctly auto-fixed it.

**Status:** Complete. Both routines' redesigned branch/marker/ambiguity
mechanics confirmed working end-to-end via real, repeated fires against
real fixtures — not just code review of the new prompt/script logic.

## Known, real, unaddressed gaps (not yet a scheduled milestone)

- **Maintenance has no concept of the `[ready]`/`Status:` readiness-marker
  convention at all** (that's Builder-only) — it can and has accidentally
  built small Builder-territory features that happen to fit its narrow
  `service.py`+`test_service.py` boundary (observed for real: it built
  bookmarks search before the Builder ever got to it, PR #37). Not
  designed or fixed.
- **`notes.md` promises "Delete a note by id."**, genuinely unimplemented
  anywhere. Maintenance can detect this (spec-vs-code review covers every
  domain) but can't fix it (needs `repo.py`, out of its scope, so it'd
  only report it). The Builder can't even see it, since discovery only
  considers `[ready]`-tagged bullets and this one isn't tagged.
  Deliberately left untagged — hold until one of the routines is
  naturally capable of resolving it, don't manually unlock it.
- **Deprecation/dead-code detection** — sketched only, in
  `builder-prompt.md`'s "Future extension" section. Not designed or
  built.
- **Prompt generalization beyond this one repo** — both prompts are
  tightly coupled to this repo's exact paths, package name, and tooling.
  Deferred until a second real project actually adopts the framework.

## Backlog (unscheduled, not yet milestones)

(none — all four original practices, CI/branch-protection hardening, the
agentic maintenance loop, and the Builder Routine are now built and
verified; see the gaps list above for what's genuinely still open)
