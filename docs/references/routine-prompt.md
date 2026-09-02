# Agentic Routine — standing prompt

Verified: 2026-08-26

This file is the **source of truth** for the scheduled maintenance
Routine's instructions. The Routine itself is configured outside this
repo (claude.ai Routines, trigger `trig_011DbA7ZQiMSGW64Md3Yjaur` for
the original repo — replace with your own trigger's ID on a new fork).
For the current cron schedule, see the "Cron retimed" note in the
Status section below — this header intentionally doesn't repeat that
value a second time, since a schedule stated in two places is a
schedule that can (and did) drift out of sync between them. Edit here
first, then copy the block below into the trigger config so the two
stay in sync.

**Why the prompt lives in the repo:** every other rule the harness
enforces is version-controlled and reviewed in a diff. The agent's own
operating instructions were the one exception — changing them left no
history and no review. They constrain what gets written to this repo as
much as any lint rule does, so they belong under the same bar.

## Status

**APPLIED.** Written 2026-08-17 while the unattended-cron verification
window was still open, held until that window closed, then synced to the
live trigger the same day after tier 2 was confirmed (both the GitHub
Actions cron and this Routine fired unattended, and the Routine correctly
fixed the planted bug and correctly declined the out-of-scope one — see
`docs/exec-plans/active/milestones.md` M10).

This version was then exercised for real by the tier-3 proof run
(`docs/quality-score/findings-log.md`'s second `behavior-spec-mismatch`
entry, PR #25): it correctly found the planted defect, wrote a failing
test, fixed it, recognized the recurrence via the findings log, and
proposed golden rule 6 in the same PR — the full loop the decision rule
and recurrence check exist for. One inefficiency surfaced in that run:
it spent several turns rediscovering that no venv/deps existed (`which
python`, `find -iname venv`, then building one from scratch). The prompt
below now states the venv bootstrap up front instead of leaving the
agent to rediscover it. Otherwise this trim only tightens wording —
every decision rule, file boundary, and limit is unchanged from the
version PR #25 ran against.

**Cron retimed** (2026-08-24): schedule moved to `30 5 * * 2` (Tuesdays
05:30 UTC). Also fired ad hoc, between scheduled runs, by the Dispatcher
Routine whenever it finds doc/golden-rule staleness or drift between
`src/todoapp/` and `docs/product-specs/` (see `dispatcher-prompt.md`
candidate check 2).

**Fixed branch, reused across runs** (2026-08-18): replaces the old
`agentic-maintenance/<timestamp>` fresh-branch-per-run naming with a
single standing branch, `agentic-maintenance/standing`. A merged prior
PR means that branch's work already landed -- the next run recreates it
fresh from `origin/master`. A still-open prior PR means the next run
merges `origin/master` into the branch first, keeping this run's own
edits on any conflict, then adds its own commits to that same PR --
multiple runs' fixes can accumulate in one PR until a human merges it.

Changes from the pre-M13 version (already exercised, see above):

1. **Domain list corrected** — old prompt said "currently widgets,
   notes, bookmarks", predating M13's rename. Four domains now.
2. **Follow-up decision rule** — every fix needs a test, rule, or doc
   correction, chosen by where the defect lived, stated in the PR.
3. **Recurrence check** — consult the findings log; a category's second
   occurrence should produce a proposed check, not just a point fix.
4. **Bounded doc sync** — a spec/code mismatch may now be fixed on the
   doc side, within tight limits.

Items 2–4 widen what the agent may touch. The scope guard is the
mechanism that made the M10 test pass, so the widenings are enumerated
explicitly rather than granted as general latitude.

**Readiness-marker skip added** (2026-08-19): this prompt had no concept
of the Builder Routine's `[ready]`/`Status: Ready for implementation`
convention, so step 2 could -- and once did for real (bookmarks search,
PR #37, before the Builder ever got to it) -- accidentally build a
Builder-territory feature that happened to fit the service.py+
test_service.py boundary. Step 2 now explicitly skips any bullet/spec
carrying either marker, full stop, regardless of scope fit.

**Shallow-clone unshallow step added** (2026-08-24): a live run
(`cse_013dkU4KRVPDRLCGwgxRaDPZ`, fired by the Dispatcher Routine) printed
`doc_gardener: shallow clone or no git history -- skipping
Verified:-date staleness checks` and then reported "no staleness
found" -- a skipped check silently indistinguishable from a clean one.
Added an explicit unshallow step up front so `doc_gardener.py`'s
`Verified:`-date checks reliably actually run instead of silently
no-opping on whatever clone depth the sandbox happens to provide.

**Step 2 scoped to changed domains only** (2026-08-26): previously
compared every one of the seven domains' spec against its service.py,
every run, regardless of whether anything had changed since the last
run -- the single biggest time cost in a live run (the 2026-08-26 test,
PR #98, took ~7.7 minutes from fire to PR, almost all of it this step).
Now diffs against its own last merged PR first (same lookup
`dispatcher-prompt.md` candidate check 2a already does) and only reviews
domains that diff actually touches -- a spec-only or code-only edit
still shows up, a domain nothing touched is skipped, since it was
already reviewed clean as of the last run. This is the "targeted
hand-off" idea from `dispatcher-prompt.md`'s deferred list, but done
inside Maintenance's own prompt (it computes its own scope) rather than
passed in from the Dispatcher, which would have needed `routine-fire.yml`
to carry a custom message payload -- a bigger change than this one. Not
yet proven live with the new scoping active.

**Full-sweep fallback + fail-loud lookup added** (2026-08-26, same day,
after external review): the scoping above has a real trade-off the old
design structurally couldn't have -- it trusts every past review was
correct forever, so one incorrect "clean" judgment on a domain now
persists silently until something else touches that domain again. Fixed
with a weekly full-sweep fallback (7+ calendar days since the last full
sweep -> review all seven domains regardless of diff, ignoring the
scoped path entirely that run) rather than new per-domain tracked state,
which would itself need to stay trustworthy -- the same failure class
this guards against. The fallback needs no new state of its own: it
reuses the last-merged-PR's date already fetched for the scoped-diff
lookup. Also: the merge-commit lookup or diff command failing outright
must now be reported, never silently treated as "zero domains touched"
-- same failure shape as the shallow-clone bug above, now guarded
against here too. Neither proven live yet.

---

## Prompt

You're maintaining `<OWNER>/<REPO>` (replace with this repo's actual GitHub owner/name before use), an agent-workflow scaffold: enforced layered architecture (Types→Config→Repo→Service→Runtime→UI), a Providers cross-cutting layer, doc-gardening, golden-rule lints.

Environment has no pre-installed venv. Once, up front: `python3 -m venv .venv && .venv/bin/pip install -q -r requirements.txt -e . ruff import-linter`. Use `.venv/bin/python`/`.venv/bin/ruff`/etc. for every command below -- don't rediscover this by trial and error.

Also up front, before step 1: run `git rev-parse --is-shallow-repository`. If it prints `true`, run `git fetch --unshallow`. `doc_gardener.py`'s `Verified:`-date staleness check silently skips on a shallow clone -- no error, just fewer findings than a real check, indistinguishable in the output from an honest "nothing stale." A skipped check must never be reported as a clean one.

Read MAP.md, docs/references/conventions.md (house rules: narrow scope, typed boundaries, reuse platform/, no bare except:, no print() in domain code), and docs/quality-score/findings-log.md (category vocabulary + history, needed in step 3).

Do ALL of the following:

1. Run `doc_gardener.py` and `check_golden_rules.py`. Fix each finding, strictly scoped to the exact file(s) it flagged.

2. Code-health review, scoped to what changed since your last run -- with a periodic full-sweep fallback so a domain that was ever incorrectly judged clean doesn't stay unreviewed forever (both added 2026-08-26). The old design reviewed all seven domains from scratch every run, so a wrong judgment couldn't compound; the scoped version trusts every past review was correct, which means a mistaken "clean" verdict now persists silently unless something else touches that domain again. The fix is a periodic full sweep, not new tracking state -- it reuses the merge date you're already fetching for the lookup below, rather than adding a new piece of state that would itself need to stay trustworthy, which is exactly the failure class this guards against.
   - Find the merge commit of your own last successful PR (most recent merged PR whose branch was `agentic-maintenance/standing` -- same lookup `dispatcher-prompt.md` candidate check 2a already does) AND its merge date. No prior merged PR exists yet -> full sweep is due (nothing to compare against).
   - If the merge-commit lookup or the `git diff --stat` command itself fails or errors -- not "ran clean and found nothing," but the command didn't complete -- stop and report this in the run output rather than treating it as zero domains touched. A failed lookup silently resolving to "nothing to review" is the same failure shape as the shallow-clone bug already hit once (a skipped check indistinguishable from a clean one) -- never let that happen again.
   - That merge date is 7 or more calendar days before today -> full sweep is due: review all seven domains regardless of diff, same as the pre-2026-08-26 behavior, and skip the scoped diff below entirely this run.
   - Neither condition -> proceed with the scoped diff: `git diff --stat <that commit> origin/master -- src/todoapp/ docs/product-specs/` -- the domains this touches (by directory name under `src/todoapp/`, or by product-spec filename) are the only ones step 2 reviews this run. This mirrors the Dispatcher's own check 2a exactly, so it's safe: a spec-only edit still shows up (scoped path includes `docs/product-specs/`), a code-only edit still shows up, and a domain nothing touched genuinely has nothing new for this step to find -- it was already reviewed clean as of your last run, and nothing changed since.
   - Diff touches zero domains (scoped mode only) -> step 2 has nothing to do this run (expected when you were fired purely for a step-1 finding, e.g. `doc_gardener.py` staleness with no code/spec drift) -- skip straight to step 3.
   - For each domain in scope this run (all seven on a full sweep, or just the diff-touched ones on a scoped run), compare docs/product-specs/<domain>.md against src/todoapp/<domain>/service.py. On a real discrepancy, decide which side is wrong:
   - **Bullet tagged `[ready]`, or spec carries `Status: Ready for implementation`?** That's the Builder Routine's territory, not yours -- skip it entirely, even if the gap would otherwise fit your service.py+test_service.py scope. Don't report it either; it's not a maintenance finding, it's a Builder discovery target.
   - **Spec right, code wrong:** if fixable entirely within that domain's service.py + test_service.py (see SCOPE GUARD), write a failing test in tests/<domain>/test_service.py, then fix service.py so it passes. If it needs any other file, touch neither -- describe the discrepancy and the files it would require in the PR instead.
   - **Code right, spec stale:** correct the prose in that domain's product-spec doc and bump its `Verified:` date. One file, one domain. Not confident which side is wrong? Touch neither -- describe it and let a human decide.

3. Recurrence check: for each issue fixed in 1–2, append one row to findings-log.md's Log table (append only) with its category. If that category already has a prior entry, a point fix isn't enough -- add ONE new check function to check_golden_rules.py (never modify/weaken an existing one), called from main(). It must pass clean on the current repo AND you must verify it actually fails on the defect it targets -- state both in the PR. If the right guard is an import-linter contract instead, describe it in the PR and leave pyproject.toml alone. Can't make it clean and targeted? Don't add it -- describe why and stop; a noisy check is worse than none.

SCOPE GUARD -- hard boundary. The only files you may modify:
   - step 1: exactly what doc_gardener.py/check_golden_rules.py flagged
   - step 2: service.py + test_service.py in one domain (never types.py/config.py/repo.py/runtime.py/ui.py/providers/platform/); or that domain's product-spec.md if the spec is stale
   - step 3: findings-log.md (append only); check_golden_rules.py (one additive function, per the limits in step 3)

Nothing else, ever -- anything outside this list goes in the PR description, never the diff.

Every fix needs exactly one follow-up: a **test** (behavioral bug), a **rule** (structural pattern now recurring), or a **doc** correction (spec was wrong) -- state which and why, or justify explicitly if none applies.

Nothing to fix anywhere? Stop -- no branch, no PR.

Otherwise, run the full suite and confirm all pass: `ruff check .`, `ruff format --check .`, `lint-imports`, `pytest -q`, `check_golden_rules.py`, `doc_gardener.py`.

BRANCH -- fixed name `agentic-maintenance/standing`, reused every run, never a fresh timestamped name.
1. `git fetch origin`.
2. If `origin/agentic-maintenance/standing` exists AND its most recent PR is already merged: that branch's work already landed in master, it's stale -- recreate it fresh from `origin/master` (`git checkout -B agentic-maintenance/standing origin/master`), discarding the old tip.
3. Else (branch doesn't exist yet, or its PR is still open/unmerged): check it out and merge `origin/master` into it to catch up with anything landed since. If that merge conflicts, this run's new work wins every conflicted file -- keep/redo this run's own edits, discard whatever `origin/master`'s incoming side changed in that same spot. Never let an incoming master change silently overwrite what this run is actively building.
4. Commit this run's fix(es) on top, push (force-push only when the branch's history was rewritten by steps 2 or 3 -- a plain fast-forward push otherwise).
5. If the branch's PR is still open from a prior run, your new commits land in that same PR (multiple runs' fixes accumulate in one PR until a human merges it) -- update the PR description to cover everything in it, not just this run's addition. If there's no open PR (fresh branch from step 2, or first-ever run), open a new one.

Never push to master directly (branch-protected). Never merge your own PR -- a human always reviews, and a PR adding a golden rule always needs a human to agree to the new constraint before merging. In the PR: files changed and why, category + follow-up per issue, and anything noticed but left untouched (out of scope, or not confident it's a bug) -- for an updated PR, this covers every run folded into it, not just the latest.
