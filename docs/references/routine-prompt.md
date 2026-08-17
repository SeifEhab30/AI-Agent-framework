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
`docs/exec-plans/active/milestones.md` M10). Next scheduled fire:
2026-08-24.

Changes from the previous (pre-M13) version:

1. **Domain list corrected** — live prompt says "currently widgets,
   notes, bookmarks", which predates M13. `widgets` was renamed to
   `todos`, and a genuinely new `widgets` domain (dashboard tiles) was
   added. Four domains now.
2. **Follow-up decision rule** — every fix must be accompanied by a
   test, a rule, or a doc correction, chosen by where the defect lived,
   and the choice stated in the PR.
3. **Recurrence check** — consult `docs/quality-score/findings-log.md`;
   the second occurrence of a category should produce a proposed check,
   not just another point fix.
4. **Bounded doc sync** — a spec/code mismatch may now be fixed on the
   doc side as well as the code side, within tight limits.

Items 2–4 widen what the agent may touch. The scope guard is the
mechanism that made the M10 test pass, so the widenings below are
enumerated explicitly rather than granted as general latitude.

---

## Prompt

You're maintaining the repo at https://github.com/SeifEhab30/AI-Agent-framework, an agent-workflow scaffold with enforced layered architecture (Types→Config→Repo→Service→Runtime→UI), a Providers cross-cutting layer, doc-gardening, and golden-rule lints.

First read MAP.md and docs/references/conventions.md for house rules (narrow scope only, boundary validation with typed models, reuse platform/ helpers, no bare except:, no print() in domain code). Then read docs/quality-score/findings-log.md — you will need its category vocabulary and history in step 3.

Do ALL of the following checks:

1. Run `python scripts/doc_gardener.py` and `python scripts/check_golden_rules.py`. For each finding, investigate the actual file and make a minimal, targeted fix -- strictly scoped to only what these two tools flagged.

2. Code-health review: for each domain under src/todoapp/ (currently todos, notes, bookmarks, widgets), read its docs/product-specs/<domain>.md and compare the described behavior against the corresponding src/todoapp/<domain>/service.py. If you find a real discrepancy (the code does not do what the spec says), first decide which side is wrong:

   - If the **spec** is right and the code is wrong: can this be fully and correctly fixed by only touching that domain's service.py and test_service.py? If yes, write a test in tests/<domain>/test_service.py that proves the bug, then fix service.py so the test passes. If a correct fix would require touching any other file (repo.py, types.py, config.py, runtime.py, ui.py, providers/, platform/, or a new file), do NOT attempt a partial fix -- do not touch service.py or test_service.py for that issue either. Instead, describe the discrepancy and exactly which file(s) it would require changing in the PR description for a human to handle separately.
   - If the **code** is right and the spec has simply gone stale (it describes behavior that was deliberately changed), correct the prose in that domain's docs/product-specs/<domain>.md and bump its `Verified:` date. Only that one file, only that domain. If you are not confident which side is wrong, change neither -- describe it in the PR description and let a human decide.

3. Recurrence check. For every issue you fixed in steps 1 and 2, assign it a category from the vocabulary in docs/quality-score/findings-log.md, and append a row to that file's Log table (append only -- never edit or delete existing rows). Then check whether that category already appears in the log from a previous run. If it does -- meaning this is the second or later time this class of defect has occurred -- a point fix is not enough: propose a mechanical check so it cannot recur silently. You may add ONE new check function to scripts/check_golden_rules.py for this, subject to these limits:

   - You may only ADD a new check function and call it from main(). Never modify or weaken an existing check.
   - The new check must pass cleanly against the current repo (no pre-existing violations), and you must verify it actually fails on the defect it targets. State both results in the PR description.
   - If the right guard is an import-linter contract rather than a golden rule, do not edit pyproject.toml -- describe the contract you would add, in the PR description, and leave it to a human.
   - If you cannot make the check clean and targeted, do not add it. Describe what you would check and why it was hard, and stop there. A noisy check is worse than none.

SCOPE GUARD -- this is a hard boundary, not a suggestion. The complete set of files you may modify in a run is:

   - step 1: only the exact files doc_gardener.py/check_golden_rules.py flagged
   - step 2: service.py and test_service.py within a single domain's folder, and only when that's sufficient for a complete correct fix -- never types.py, config.py, repo.py, runtime.py, ui.py, providers/, platform/; OR docs/product-specs/<domain>.md for that same domain when the spec is the stale side
   - step 3: docs/quality-score/findings-log.md (append only), and scripts/check_golden_rules.py (additive only, one new function, under the limits above)

Nothing else, ever. Anything outside this list goes in the PR description for a human, never into the diff.

Every fix you make must leave the repo harder to break the same way twice. Each issue you resolve must be accompanied by exactly one of: a **test** (for a behavioral bug), a **rule** (for a structural pattern that has now recurred), or a **doc** correction (for a spec/code mismatch where the doc was wrong). State which one you chose for each issue, and why that was the right category rather than the other two. If you believe a fix genuinely needs no follow-up, say so explicitly and justify it.

If you find nothing to fix in any check, stop here and do nothing further (no branch, no PR).

Otherwise, after fixing, run the full validation suite and confirm all pass: `ruff check .`, `ruff format --check .`, `lint-imports`, `pytest -q`, `python scripts/check_golden_rules.py`, `python scripts/doc_gardener.py`.

Commit to a new branch named agentic-maintenance/<YYYY-MM-DD>-<HHMMSS UTC>, push it, and open a PR against master. Use a fresh unique branch name every run -- never reuse a branch name from a previous run, even on the same calendar day, since a prior PR for that name may already be merged or closed. In the PR description: list exactly which files you changed and why, the category and follow-up type for each issue, and separately list anything you noticed but did not touch (either because it was out of scope, or because you weren't confident it was actually a bug). Never push directly to master -- it's branch-protected. Never merge the PR yourself; a human always reviews and merges. In particular, never merge a PR that adds a golden rule: a new standing constraint on all future code always needs a human to agree to it.
