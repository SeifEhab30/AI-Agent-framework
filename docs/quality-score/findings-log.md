# Findings Log

Verified: 2026-08-17

Every issue the harness catches gets one row here, tagged with a category
from the controlled vocabulary below.

**Why this file exists:** a PR description records *that* something was
fixed; this file records *what kind* of thing it was, in a form that can
be counted. Without that, no one — human or agent — can notice that the
same class of defect has now appeared three times. Recurrence detection
is the input to the rule that says: the second time a category appears,
it should stop being a fix and become a check.

**How it gets used:** an agent fixing an issue looks up the category
here first. If this is the second or later occurrence, the agent proposes
a new golden rule or import-linter contract in the same PR, rather than
only the point fix. See `docs/references/routine-prompt.md`.

## Category vocabulary

Use an existing category if one fits. Only add a new one if the issue
genuinely does not belong to any of these — a vocabulary that grows
without discipline cannot be counted, which defeats the file's purpose.

| Category | Means |
|---|---|
| `behavior-spec-mismatch` | Code runs fine but does not do what the product spec describes. |
| `unimplemented-spec-promise` | Spec describes a feature that was never built at all. |
| `stale-doc-reference` | A doc points at a file, path, or symbol that no longer exists. |
| `stale-doc-prose` | Doc text describes behavior the code no longer has (links still valid). |
| `boundary-typing` | Bare `dict`/`Any` crossing a layer boundary instead of a typed model. |
| `layering-violation` | An import crosses layers in the wrong direction, or reaches `providers/` outside `runtime.py`. |
| `missing-declaration` | A domain exists without its full set of contracts / MAP.md entry. |
| `duplicate-helper` | A local helper reimplements something already in `platform/`. |
| `error-handling` | Bare `except:`, or an error swallowed so a real failure hides. |
| `observability` | `print()` in domain code instead of the providers logger. |
| `harness-tooling` | A defect in the enforcement machinery itself (a check, script, or workflow) — the tools that catch everything else. |

## Follow-up types

Every fix should leave the repo harder to break the same way twice. One
of these accompanies each entry:

- **test** — a regression test proving the bug (use for behavioral bugs)
- **rule** — a new/extended golden rule or contract (use for structural patterns)
- **doc** — a corrected spec or reference (use for spec/code mismatches)
- **none** — justified only when the fix is itself the permanent guard

## Log

Newest last. Backfilled entries below reconstruct history from
`docs/exec-plans/active/milestones.md`; entries from M14 onward are
written at the time of the fix.

| Date | Category | Where | Found by | Fix | Follow-up |
|---|---|---|---|---|---|
| 2026-08-12 | `behavior-spec-mismatch` | `todos/service.py` (then `widgets/`) | agentic Routine | `toggle_done` always set `done=True` instead of inverting | test — `test_toggle_done_flips_back_off` |
| 2026-08-12 | `stale-doc-reference` | `docs/product-specs/notes.md` | doc-gardener | link to deleted `draft_v0.py` unlinked | none — gardener's `--fix` is the standing guard |
| 2026-08-17 | `missing-declaration` | `scripts/check_golden_rules.py` | M13 review | adding a domain without contracts/MAP row passed silently | rule — golden rule 5 (domain declaration completeness) |
| 2026-08-17 | `harness-tooling` | `scripts/doc_gardener.py` | first unattended cron run | staleness used file mtime, which every fresh CI checkout resets to "now" — so all docs read as stale once their `Verified:` date fell behind the run date | rule — date sources by git commit instead, and skip the check outright on a shallow clone rather than guess |
| 2026-08-17 | `harness-tooling` | `.github/workflows/doc-gardener.yml` | first unattended cron run | gardener exited 1 on findings, failing the step before the commit/PR steps could run — the workflow could never open the PR it existed to open | rule — findings now exit 0; `--strict` opts into gating |
| 2026-08-17 | `behavior-spec-mismatch` | `bookmarks/service.py` | agentic Routine (step 2 spec review) | `create_bookmark` accepted a blank title -- `bookmarks.md` requires a non-empty URL *and* title, only URL was checked | test — `test_create_rejects_blank_title`; rule — golden rule 6 (stripped-but-unvalidated field) |

## Open / deliberately unfixed

Planted faults held live on `master` for the unattended-cron
verification window. These are test fixtures, not defects to fix.

| Category | Where | Purpose |
|---|---|---|
| `stale-doc-reference` | `docs/product-specs/notes.md` | proves doc-gardener fires and opens a PR unattended |
| `unimplemented-spec-promise` | notes delete-note, needs `repo.py` | proves the Routine respects its scope guard and reports rather than half-fixes |
