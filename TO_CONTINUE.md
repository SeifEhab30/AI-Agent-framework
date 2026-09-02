# TO CONTINUE — handoff doc

Written 2026-09-02, at the end of the original author's internship. This
file is the single entry point for whoever picks this project up next.
Read this first, then `README.md` for setup steps, then `memory.md` for
ready-to-paste prompts if you're continuing with Claude Code, Codex, or
Cursor.

Everything below reflects the actual, current state of the repo as of
this writing — not a plan, not an aspiration. Where something is
unfinished or unproven, it's labeled that way explicitly.

## 1. What this project is

A small FastAPI + SQLite todo-style app (`todoapp`) with seven domains
(todos, notes, bookmarks, widgets, reminders, labels, tags), each built
under a strictly enforced layering convention. The app itself is not the
point — it's a deliberately simple, real codebase used as the substrate
for the actual experiment: **can a set of autonomous coding agents
maintain and extend a codebase safely, under mechanical guardrails,
with minimal human intervention?**

The two halves of the repo:

- **The app** (`src/todoapp/`, `frontend/`, `tests/`) — a normal, small,
  working product. Every domain follows
  `types → config → repo → service → runtime → ui`, one direction only,
  enforced by `import-linter` (see `docs/architecture/layering.md`).
- **The agent framework** — four autonomous Claude Code Routines that
  read/write this repo via GitHub, plus the mechanical scripts
  (`scripts/check_*.py`, `scripts/doc_gardener.py`) that constrain and
  verify what they do. This is the part that's actually novel and the
  part a new maintainer is most likely here to continue.

## 2. The core approach

A few principles run through every part of this framework — understand
these before changing anything, since most design decisions trace back
to one of them:

1. **Mechanical enforcement over prompt promises.** An agent's scope
   guard is never just "the prompt says don't do X" — where a boundary
   can be checked in code (which domain was touched, which paths
   changed, whether a contract was modified), a script checks it
   (`scripts/check_builder_scope.py`, `scripts/check_dispatcher_scope.py`,
   `scripts/check_merge_gate.py`), and CI/the agent's own validation
   step run that script before anything is allowed to merge. Prompts
   state intent; scripts enforce it.
2. **Prove narrow, then widen — never trust broad on day one.** Every
   capability in this repo started maximally restricted (one diff shape,
   manual-only trigger, one domain) and was widened one step at a time,
   only after the narrower version had a real, verified success under
   its belt. See §4 for where each of the four agents currently sits on
   this ladder.
3. **A category that recurs becomes a check, not another one-off fix.**
   `docs/quality-score/findings-log.md` tags every bug an agent finds by
   category. The second time a category appears, the fixing agent is
   expected to propose a new golden rule or lint contract in the same
   PR, not just fix the instance. This is why `scripts/check_golden_rules.py`
   has grown over time instead of the same bug class recurring silently.
4. **Full-inventory traceability, not diff-only.** A PR's traceability
   table (see `builder-prompt.md`'s traceability-table paragraph in its
   Prompt section — the doc has no numbered subsections) lists every
   requirement for the
   target domain, every run — not just what changed — marked Modified or
   Not modified, each backed by a named test. This is what lets Merge
   Gate judge a PR without re-deriving the domain's entire history.
5. **Read-only where possible, no scratch state left behind.** Every
   agent reads through `gh`/`git show <ref>:<path>` against a PR's head
   commit rather than checking branches out locally. Nothing is written
   to disk that needs cleanup.

## 3. Architecture at a glance

- `src/todoapp/<domain>/` — one folder per domain, six files each
  (`types.py`, `config.py`, `repo.py`, `service.py`, `runtime.py`,
  `ui.py`). `src/todoapp/providers/` is the only place cross-cutting
  concerns (DI, auth, logging) live, and only `runtime.py` may import
  from it.
- `src/todoapp/app.py` — mounts every domain's router under one
  combined FastAPI app.
- `frontend/` — React + Vite. **All seven domains now have frontend
  components and Vitest tests** (`frontend/src/components/<Domain>.jsx`
  + `.test.jsx`) — the earlier "frontend is v1-excluded" boundary was
  lifted and backfilled; this is done, not a pending plan.
- `docs/product-specs/<domain>.md` — the actual source of truth for what
  each domain should do, from a user's perspective. `[ready]` bullets and
  `Status:`/`Frontend:` markers on these files are what authorize Builder
  to act — see `builder-prompt.md`'s DISCOVERY section for the exact
  marker vocabulary.
- `docs/references/` — the four agent prompts, plus `conventions.md`
  and other lookup material. **This is critical-path**: Merge Gate will
  never auto-merge a change here, always human-reviewed.
- `MAP.md` — short index, not documentation. Follow its links; don't
  expand it. Now also points to this document, `memory.md`, and
  `docs/references/routine-fire-loop.drawio` (the pipeline diagram),
  since a plain index that doesn't mention its own handoff docs isn't
  much of an index.
- `docs/exec-plans/active/milestones.md` — the actual run history:
  what was tried, what broke, what was proven, in chronological order.
  This is the fullest record of *why* things are shaped the way they
  are; read it if a design decision here seems unmotivated.
- `docs/quality-score/findings-log.md` — categorized log of every bug an
  agent has found, used for the recurrence-detection rule in §2.

## 4. The four agents — current state

All four are **RemoteTrigger-based Claude Code sessions** (not code that
runs inside this repo) — their instructions live in
`docs/references/*-prompt.md` as version-controlled "source of truth,"
copied into a live trigger's config whenever the doc changes. The prompt
docs previously had this specific repo's GitHub path hardcoded; that's
now replaced with `<OWNER>/<REPO>` placeholders (see §7).

| Agent | File | Scope | Trust level right now |
|---|---|---|---|
| **Maintenance** | `routine-prompt.md` | Finds and fixes spec-vs-code drift, doc staleness. Never builds new features. | Cron-scheduled (`30 5 * * 2`), proven repeatedly, including recognizing recurring bug categories and proposing golden rules. |
| **Builder** | `builder-prompt.md` | Implements new, human-approved, ready-marked specs — new domains or `[ready]`-tagged bullets on existing ones, backend + frontend. Never touches anything outside its one target. | **Manual-only**, no cron. Proven repeatedly across several domains and behaviors (see the Status section in the doc for the exact PR list). Cadence hasn't been revisited. |
| **Dispatcher** | `dispatcher-prompt.md` | Polls whether Maintenance/Builder have real work, fires them via a GitHub Actions workflow dispatch, then checks whether any PR is Merge-Gate-eligible and fires that too. | **Manual-only**. Proven live end-to-end at least once (see milestones.md for the run where it correctly chained Builder → wait → Maintenance → wait → Merge Gate in one continuous run). |
| **Merge Gate** | `merge-gate-prompt.md` | Mechanically + semantically reviews any open PR, auto-merges what's eligible. | **Manual-only**. Proven on real, non-fabricated PRs — including catching a genuine test-coverage gap Builder itself introduced (a substring-search test that only proved a prefix match), and correctly refusing to merge until the test was tightened. Eligible diff shapes: `frontend_only`, `frontend_update`, `existing_domain`, `docs_only`. `new_domain` is deliberately never auto-mergeable (largest blast radius). |

**None of these are on a schedule except Maintenance.** Standing up
Builder/Dispatcher/Merge Gate on cron is an explicit, deliberate
not-yet-decided step — see §5.

**Critical-path gate** (in `check_merge_gate.py`, `CRITICAL_PATH_PREFIXES`):
CI/workflow config, the gate scripts themselves, agent prompts under
`docs/references/`, and dependency/build config are *never*
auto-mergeable by Merge Gate, regardless of how clean the diff looks —
always left for a human. This repo has no auth domain, so this is its
closest analog to a security carve-out.

## 5. Open items / where a new maintainer should look first

- **Universal PR review.** Merge Gate currently reviews any open PR (not
  just Builder's own), but the trigger surface is still Dispatcher
  polling on a schedule/manual fire — not a real `pull_request`-event
  webhook reacting in real time. A human-authored PR that doesn't follow
  the traceability-table convention will mechanically read as "not
  eligible," not literally "rejected for being human-authored," but
  practically similar until a lighter-weight eligibility path exists for
  freeform PRs.
- **Scheduling decision for Builder/Dispatcher/Merge Gate.** All three
  are still manual-only by deliberate choice ("prove by hand first," per
  §2). Whether/when to put any of them on a cron, and at what cadence,
  is an open decision for whoever continues this — not something that
  broke, just something that was never revisited.
- **`docs_only` Merge Gate shape is new and only tested once.** It was
  added and proven against exactly one real PR. Watch for edge cases
  (e.g. a docs-only PR that also needs human judgment for content
  reasons, not just mechanical checks) before trusting it broadly.
- **A known rough edge:** Merge Gate cannot update a PR's branch itself
  (only a human or another mechanism can) — if a PR's branch falls
  behind `master` after other PRs land, Merge Gate will correctly refuse
  to merge (GitHub rejects the call) but won't self-heal by rebasing.
  This happened live once and was fixed by hand
  (`gh api -X PUT repos/<owner>/<repo>/pulls/<n>/update-branch`).
- **Frontend backfill was completed**, not deferred — don't re-plan it;
  all seven domains have working frontend + Vitest tests now.
- **`docs/exec-plans/active/milestones.md` is stale in ways that
  actively contradict this document** — read it for the general shape
  of the project's history, but don't trust specific claims in it
  without cross-checking, especially in the M10 write-up and the
  Backlog section at the bottom. Concretely, as of this handoff: M10's
  status still says the notes-domain delete-note gap is "deliberately
  still live on master" — it isn't, it was implemented (`notes/repo.py`,
  `notes/service.py` both have `delete`), and M14 already records this
  correctly elsewhere in the same file, so the two entries disagree with
  each other. The Backlog section still lists frontend backfill for
  reminders/labels/tags as deferred (done — see §3 above) and claims
  Merge Gate's semantic check "has never been exercised against a
  genuinely wrong test in a live run" (it has — see §4's table and
  `merge-gate-prompt.md`'s own Status section, both accurate as of this
  handoff). This document was deliberately not used to patch
  `milestones.md` itself during this handoff (an explicit choice, not an
  oversight) — treat reconciling it as a real, worthwhile first task,
  not busywork.
- Prompt doc "Status" sections were audited and corrected as part of
  this handoff (`merge-gate-prompt.md`'s in particular was significantly
  out of date — it said "not yet run against a real PR," which had long
  stopped being true). Trust a "Status" section over this document if
  they ever disagree *and* the Status section is more recently dated —
  but see the `milestones.md` caveat above, since that file is the one
  proven exception where "more detail" didn't mean "more accurate."

## 6. Approaches tried and abandoned — and why

Worth reading before re-proposing any of these; each was a real attempt,
not a hypothetical rejected on paper.

- **GitHub Actions as the sole capability boundary for Merge Gate**
  (`.github/workflows/merge-gate.yml`, still present, paused as
  advisory-only — it runs the mechanical checks and comments the result,
  but no longer merges anything). The idea: keep the capability boundary
  in GitHub's own job-level `permissions:` block instead of a
  Claude-specific tool allowlist, for portability across agent runtimes.
  It failed for a mundane reason, not a design flaw: the one piece
  needing an actual model call (does a named test really prove its spec
  bullet) needed a real LLM behind `scripts/run-agent.sh`, and the free
  option (GitHub Models, authenticated via the workflow's own
  `GITHUB_TOKEN`, no separate billing) turned out to be mid-retirement on
  a live test. The paid alternative needed a separate `ANTHROPIC_API_KEY`
  — a real Console account with its own billing, unrelated to a Claude
  Code subscription, which the other three agents don't pay. **Pivoted
  to a RemoteTrigger Claude Code session instead**, where the session
  itself is the model call, sidestepping the second-credential problem
  entirely — at the real cost of going back to a Claude-Code-specific
  capability boundary instead of a runtime-agnostic one. If a
  no-separate-billing model API ever becomes available, the GitHub
  Actions path is still there to revisit, not deleted.

- **A per-domain tracked-timestamp file for doc-staleness detection.**
  Considered as the fix for Maintenance's diff-lookup failure mode
  (§2 rule 3 exists partly because of this). Rejected before being
  built: a tracked-timestamp file is a new piece of state that itself
  needs to stay trustworthy, which is exactly the failure class it was
  meant to prevent (a silently-wrong "last checked" record is just as
  dangerous as a silently-wrong "clean" verdict). Went with a periodic
  full-sweep fallback instead — self-healing by construction, no new
  state to trust.

- **A generic regex-anchor golden rule**, proposed after a real bug
  (`labels/service.py`'s `$`-anchored regex silently accepting a
  trailing newline in a hex color, `findings-log.md`'s 2026-08-18 entry).
  Rejected in that PR's own description: `$` vs `\Z`/`fullmatch`
  anchoring bugs are real, but a generic mechanical check for "did you
  mean fullmatch" is prone to false positives against legitimate
  multi-line-aware regexes, which would make the check itself
  untrustworthy — noisy checks get ignored, which defeats the point.
  Logged as a one-off fix instead, explicitly not generalized.

- **A generic falsy-guarded-repo-write check, generalized too early —
  then correctly generalized on the second real occurrence.** The
  `widgets/service.py` `set_value`-to-`0` bug (`if value:` silently
  no-opping) was initially fixed as a one-off (2nd occurrence of
  `behavior-spec-mismatch`, but judged too specific a shape to
  generalize yet). When the *identical* shape recurred in
  `notes/service.py`'s `update_body` (clearing to `""`), it became
  golden rule 7. The lesson embedded in the process itself: don't
  generalize a check after one occurrence, but don't skip generalizing
  after a confirmed second one either — recorded here since it's the
  clearest live example of the "second occurrence becomes a check" rule
  from §2 actually firing correctly.

- **Firing Merge Gate on a deliberately-planted bad-test fixture without
  re-confirming scope with the user first**, from this project's final
  working session (2026-08-26 equivalent in-session date). The user had
  set a standing "not running any more routines till I say so" hold
  earlier the same session; a later "do it then" was read as lifting
  that hold specifically for one fixture test, but that was the agent's
  interpretation, not something the user said outright. Caught
  immediately when the user pushed back ("didn't I say to not run any
  routines?"). No lasting damage (the run was allowed to finish, by the
  user's own choice, once asked) — the failure was procedural, not
  technical: an ambiguous natural-language authorization was treated as
  broader than it was. **Lesson: re-confirm explicitly before firing
  anything under a standing hold, even when a later message seems to
  imply permission — don't infer scope from tone.**

- **A real accidental-merge incident from branching off the wrong local
  branch.** While opening an unrelated PR, a new branch was cut without
  first switching back to `master` — the working tree was still on a
  scratch branch used for an earlier deliberate test fixture (a
  real-but-deliberately-weak test, built on purpose to prove Merge
  Gate's semantic check could catch it). The new branch inherited that
  entire fixture, including the weak test, and it was merged to real
  `master` before being caught. **Caught immediately** by grepping for
  the fixture's function names on `master` right after the merge,
  reverted cleanly with `git revert` on the squash commit, verified with
  the full validation suite, and the intended (unrelated, one-line) work
  was redone correctly on a fresh branch off an updated `master`.
  **Lesson, now a standing practice: always explicitly verify
  `git branch --show-current` is the expected base branch (usually
  `master`, freshly pulled) before cutting a new branch — never assume
  the working tree is where you left it.**

- **A stale live trigger silently drifting from its own source-of-truth
  doc.** Builder's live RemoteTrigger prompt was found to be missing an
  entire prior rewrite (the full-inventory traceability convention) —
  it had been running an outdated prompt for at least a full working
  session before an unrelated audit caught it. The failure mode: editing
  one agent's prompt doc and syncing only that one trigger, while the
  other three docs silently went unsynced whenever *they* changed too.
  **Lesson, now a standing practice: sync all four live triggers
  whenever any single prompt doc changes, not just the one directly
  touched** — confirmed via `RemoteTrigger action=get` after any prompt
  edit, not assumed.

- **`doc_gardener.py`'s path-reference regex silently never matching
  this repo's own established link convention.** Its `PATH_PATTERN`
  matched backtick- and `[text](href)`-style paths, but not this repo's
  actual convention of putting the referenced path in the markdown link
  *text* itself (`[docs/x/y.md](../relative/path)`). This meant
  staleness-by-dead-reference was silently never checked for any spec
  using that style — for an unknown length of time, since the check
  never errored, it just never fired. Found by deliberately investigating
  *why* a real fixture edit produced zero findings, rather than assuming
  the zero was correct. **Lesson: a check producing zero findings is not
  the same as a check that ran correctly — when a check's blind spot is
  plausible, deliberately construct a case it should catch and confirm
  it actually does, rather than trusting silence.**

## 7. How to plug this framework into a different repo or agent runtime

This framework was designed with portability in mind — the actual
enforcement lives in plain Python scripts + GitHub, not in anything
Claude-Code-specific, with one exception noted below.

**To point it at a different repo (same app, new fork):**
1. Every prompt doc under `docs/references/*-prompt.md` now uses
   `<OWNER>/<REPO>` as a placeholder where this repo's specific GitHub
   path used to be hardcoded. Replace it with your fork's actual path
   before creating any trigger.
2. `.github/workflows/routine-fire.yml`'s three `TRIGGER_ID=` lines are
   placeholders (`<MAINTENANCE_TRIGGER_ID>` etc.) — replace each with
   your own trigger's actual ID, or the workflow fails loudly (by
   design) rather than silently firing nothing. This is easy to miss:
   fixing the three GitHub Actions secrets alone is not sufficient, the
   workflow still needs editing.
3. Those same three secrets — `MAINTENANCE_FIRE_TOKEN`,
   `BUILDER_FIRE_TOKEN`, `MERGE_GATE_FIRE_TOKEN`. Each value is that
   specific RemoteTrigger's own API bearer token — shown once, in the
   claude.ai Routines UI, at the moment you create the trigger — stored
   with `gh secret set <NAME> --body "<token>"`. These are secrets *you*
   generate when you create your own triggers, not anything inherited
   from the original repo — the original repo's three fire-token
   secrets were deleted as part of this handoff (2026-09-02), since a
   live Anthropic bearer token left in a repo's Actions secrets after
   the account owner leaves is a real, live credential someone else
   could fire routines with. Until you add your own three secrets back,
   the Dispatcher's fires will fail with "No fire token configured" —
   expected, not a bug; you can still run any Routine by hand via
   `RemoteTrigger action=run` in the meantime.
4. Stand up each agent manually first (see README.md §6) — don't jump
   straight to cron.

**To adapt this to a genuinely different codebase (not this todo app):**
The pattern that generalizes is the *shape* of each agent, not its
specific checks:
- A **Maintenance**-shaped agent needs: a way to diff "what the spec
  says" against "what the code does" for your domain model, and a
  scoped, mechanically-checked boundary on what it's allowed to touch.
- A **Builder**-shaped agent needs: a human-authored, explicitly
  ready-marked backlog (this repo uses `[ready]` bullets and `Status:`/
  `Frontend:` markers in spec files — any unambiguous marker convention
  works), and a scope guard script that verifies its diff only touched
  what it claimed to.
- A **Dispatcher**-shaped agent needs: cheap, exact (not fuzzy) signals
  for "does X have real work" — this repo deliberately avoided any
  judgment-based firing heuristic, reserving that for a future agent
  whose signal genuinely isn't a clean diff/marker check.
- A **Merge Gate**-shaped agent needs: a mechanical eligibility check
  (CI green, diff shape, critical-path exclusion, traceability
  structure) that runs *before* any semantic/LLM judgment call, so the
  model is only ever asked the one question code can't answer (does
  this test really prove this claim), never asked to re-derive
  mechanical facts.

**The one Claude-Code-specific piece:** all four agents currently run as
RemoteTrigger Claude Code sessions — the session itself *is* the model
call for the one place a judgment call is needed (Merge Gate's semantic
test review), which is why no separate billed API key was ever needed.
An earlier GitHub-Actions-only version of Merge Gate
(`.github/workflows/merge-gate.yml`, still present, paused as
advisory-only) tried keeping the capability boundary in GitHub's own
`permissions:` block instead of a Claude-specific tool allowlist, for
portability across agent runtimes — abandoned only because the free
LLM option it depended on (GitHub Models) was mid-retirement, not
because the approach was wrong. If you're adapting this to a
non-Claude-Code agent runtime, that workflow file plus
`scripts/run-agent.sh` are the starting point, not the RemoteTrigger
approach.

**Concrete checklist if you're standing this up on a different agent
runtime (Codex, Cursor, a custom script, anything that isn't a Claude
Code RemoteTrigger session):**
1. You lose the "session itself is the model call" trick — your runtime
   needs its own way to make one LLM call per Merge Gate review (the
   semantic test-judgment step). Budget for that as a real, separate
   cost; it isn't optional, it's the one check nothing else in this
   framework can replace.
2. Start from `.github/workflows/merge-gate.yml` (currently paused,
   advisory-only) and `scripts/run-agent.sh` — they already show the
   mechanical-check-then-one-LLM-call shape working against a plain
   `GITHUB_TOKEN`, no RemoteTrigger involved. Re-enable the merge step
   there (it currently only comments) once you've wired a model call
   `run-agent.sh` can actually reach.
3. For Maintenance/Builder/Dispatcher — these don't strictly need an
   LLM-judgment step the way Merge Gate does (their checks are
   deterministic diffs/markers), but they do need *something* that can
   read a repo, write a branch, and open a PR under your chosen scope
   guard script (`check_builder_scope.py`, `check_dispatcher_scope.py`).
   Any agent runtime with repo write access and shell/tool access can
   fill this role — the scope guard scripts don't care what called them,
   they just check the resulting diff.
4. However you trigger these agents (cron, webhook, manual), preserve
   the "prove narrow, then widen" sequencing from §2 — this repo's own
   history (§6) is the cautionary example for skipping that.
5. Keep the mechanical scripts as the actual authority regardless of
   runtime — `scripts/check_*.py` and CI are what make a scope guard
   real instead of just a prompt's promise (§2 rule 1). Don't let a new
   runtime's own conventions become the only enforcement.

## 8. Where to actually start

1. Read `README.md`, run the setup steps, confirm the validation suite
   passes locally.
2. Read `docs/exec-plans/active/milestones.md` end to end — it's the
   real history and will answer most "why is it built this way"
   questions before you have to ask them.
3. Read the one prompt doc for whichever agent you're most interested in
   continuing — each one's own "Status" section (see caveat in §5) and
   inline comments explain its own reasoning far better than a summary
   here can.
4. If you're continuing with an AI coding assistant rather than by hand,
   see `memory.md` for a ready-to-paste briefing prompt.
