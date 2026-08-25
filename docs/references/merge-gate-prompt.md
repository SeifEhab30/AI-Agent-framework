# Merge Gate — standing design doc

Verified: 2026-08-25

Unlike `routine-prompt.md`/`builder-prompt.md`/`dispatcher-prompt.md`, the
merge gate is **not** a RemoteTrigger-fired Claude Code Routine session.
It's a GitHub Actions workflow (`.github/workflows/merge-gate.yml`) that
runs a small script (`scripts/check_merge_gate.py`), which in turn calls
an agent CLI for exactly one narrow judgment through a swappable adapter
(`scripts/run-agent.sh`). This file records why that's a deliberate
architectural choice, not an inconsistency with the other three.

**Why not a RemoteTrigger Routine like the others:** the other three
Routines all do multi-step, stateful, agentic work (read many files,
decide a target, write six layers, run a validation suite) — a full
session with tool access earns its keep there. The merge gate does none
of that. Everything it needs is already mechanically knowable (CI status,
diff shape, traceability row structure) except one narrow question — does
a specific test really prove a specific spec bullet — which is a single
read-in, single judgment, no follow-up action. That doesn't need an
agentic session; it needs one prompt and one answer.

**Why the boundary lives in GitHub, not in an agent's tool allowlist:** a
Claude Code-specific tool grant (no `Edit`/`Write` on a trigger) only
exists for Claude. This repo's stated goal is to work across agent
runtimes, not just Claude — so the actual enforcement point had to move
somewhere every runtime respects. GitHub Actions' job-level `permissions:`
block is that place: `merge-gate.yml`'s `review` job runs with
`contents: read` only and can never merge or write, regardless of what
`run-agent.sh` calls internally; the `merge` job has `contents: write` but
never invokes an agent at all, only acts on `review`'s own structured
output. Swapping which CLI `run-agent.sh` calls (Claude Code today, some
other agent tomorrow) never requires touching the permissions contract,
because the contract was never expressed in agent-specific terms to begin
with.

**The pieces, and what each one owns:**
- `.github/workflows/merge-gate.yml` — the permission boundary. `on:
  pull_request`, filtered in-job to `agentic-build/*` branches (no
  head-branch filter exists at the trigger level). Two jobs: `review`
  (read-only, runs the script, comments if blocked) and `merge` (write,
  gated on `review`'s `verdict` output, runs a plain `gh pr merge` --
  never an agent call).
- `scripts/check_merge_gate.py` — the mechanical checks (CI green, branch/
  mode eligibility, traceability row structure) plus orchestrating the one
  semantic call. See its own docstring for the full check list. Exit code
  is the only interface the workflow reads.
- `scripts/run-agent.sh` — the only file that names a specific agent CLI.
  Takes a prompt on stdin, returns raw text on stdout. Swapping runtimes
  is a change to this one file's case statement.
- `docs/references/merge-gate-review-prompt.md` — the literal prompt sent
  through the adapter. Single-shot, read-only, no tools, must return one
  line of JSON.

**Eligibility (v1 -- narrow on purpose):** only PRs whose diff shape is
`frontend_only` (a frontend component + test + `api.js`/`App.jsx`
registration + spec `Frontend:` marker cleared, no `src/todoapp/` files
touched) are auto-mergeable. `existing_domain`, `frontend_update`, and
`new_domain` builds are left for a human. `check_branch_and_mode()` in
`check_merge_gate.py` enforces this directly. Same "prove narrow, then
widen" discipline as every other capability this repo has added.

**Why this doesn't violate "human review and merge are mandatory, every
run, no exception"** (the standing rule in `routine-prompt.md`/
`builder-prompt.md`): that rule binds the *Builder* — it must never merge
or approve its own work. The merge gate is a separate mechanism reviewing
someone else's PR, the same relationship a human reviewer has to it today.

## Status

**Not yet run against a real PR.** Workflow, script, adapter, and prompt
all drafted 2026-08-25 as a pilot for a runtime-agnostic execution model
(workflow + prompt file + adapter, GitHub-level permission contract
instead of an agent-specific tool allowlist) — chosen deliberately as the
lowest-risk place to prove this pattern, since merge-gate has no prior
live behavior to break. If it proves out, the same shape (workflow +
adapter + permissions contract) is the intended template for eventually
moving Maintenance/Builder/Dispatcher off RemoteTrigger too — not done
yet, tracked as a separate, larger decision.

**Known gaps, not yet resolved:**
- `run-agent.sh`'s `claude -p --output-format text` invocation, reading
  the prompt from stdin, is not yet verified against a real headless
  Claude Code CLI call in CI. Needs a live dry run before this is trusted.
- `TABLE_ROW_PATTERN` in `check_merge_gate.py` is a first guess at
  `builder-prompt.md` §3a's traceability table shape, not yet proven
  against a real PR body.
- No PR has gone through this pipeline end-to-end yet. First real
  `frontend_only` Builder PR is the proof point, same "wait for a natural
  candidate" discipline used elsewhere in this repo.

## Who may edit this file

A human, always. Same rule as `routine-prompt.md`/`builder-prompt.md`/
`dispatcher-prompt.md`.
