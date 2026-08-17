# Agentic Routine — standing prompt

Verified: 2026-08-17

This file is the **source of truth** for the scheduled maintenance
Routine's instructions. The Routine itself is configured outside this
repo (claude.ai Routines, trigger `trig_011DbA7ZQiMSGW64Md3Yjaur`,
cron `0 10 * * 1`). Edit here first, then copy the block below into the
trigger config so the two stay in sync.

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
version PR #25 ran against. Next scheduled fire: 2026-08-24 (Tuesday
05:00 UTC).

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

---

## Prompt

You're maintaining https://github.com/SeifEhab30/AI-Agent-framework, an agent-workflow scaffold: enforced layered architecture (Types→Config→Repo→Service→Runtime→UI), a Providers cross-cutting layer, doc-gardening, golden-rule lints.

Environment has no pre-installed venv. Once, up front: `python3 -m venv .venv && .venv/bin/pip install -q -r requirements.txt -e . ruff import-linter`. Use `.venv/bin/python`/`.venv/bin/ruff`/etc. for every command below -- don't rediscover this by trial and error.

Read MAP.md, docs/references/conventions.md (house rules: narrow scope, typed boundaries, reuse platform/, no bare except:, no print() in domain code), and docs/quality-score/findings-log.md (category vocabulary + history, needed in step 3).

Do ALL of the following:

1. Run `doc_gardener.py` and `check_golden_rules.py`. Fix each finding, strictly scoped to the exact file(s) it flagged.

2. Code-health review: for each domain under src/todoapp/ (currently todos, notes, bookmarks, widgets), compare docs/product-specs/<domain>.md against src/todoapp/<domain>/service.py. On a real discrepancy, decide which side is wrong:
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

Otherwise, run the full suite and confirm all pass: `ruff check .`, `ruff format --check .`, `lint-imports`, `pytest -q`, `check_golden_rules.py`, `doc_gardener.py`. Commit to a new branch `agentic-maintenance/<YYYY-MM-DD>-<HHMMSS UTC>` (always fresh -- never reuse a prior run's name, even same-day), push, open a PR against master. In the PR: files changed and why, category + follow-up per issue, and anything noticed but left untouched (out of scope, or not confident it's a bug). Never push to master directly (branch-protected). Never merge your own PR -- a human always reviews, and a PR adding a golden rule always needs a human to agree to the new constraint before merging.
