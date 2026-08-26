# Dispatcher Routine — standing prompt

Verified: 2026-08-26

This file is the **source of truth** for the Dispatcher Routine's
instructions, same convention as `routine-prompt.md`/`builder-prompt.md`.
Edit here first, then copy the Prompt section into a trigger config once
one is created.

**What this is:** a third, separate agent whose only job is deciding
*whether* the maintenance Routine, the Builder Routine, or the Merge Gate
Routine likely has real work to do, and firing the one(s) that do —
replacing separate crons per agent (each of which pays full
session-provisioning cost even on a completely empty week) with one
cheap, frequent check that only spends real agent tokens on the heavier
Routines when there's an actual candidate.

**Why a separate agent, not logic added to maintenance or the Builder:**
considered and rejected a "train" design where each agent, on finishing,
decides whether to trigger the next one. Rejected because it spreads
cross-agent trigger authority across every agent instead of keeping it
in one narrow, auditable place, forces every agent's prompt to also
carry orchestration logic unrelated to its actual job (mixing "do the
work" with "decide who works next"), and still doesn't solve "what
starts the chain" — something still needs a schedule. Concentrating
trigger-invocation authority in one dispatcher, and nothing else, is
easier to reason about and matches how maintenance and the Builder were
kept apart from each other for the same reason: a bug in a
higher-authority action shouldn't be able to hide inside an agent doing
unrelated work.

## Status

**Live trigger exists** (`trig_019dVGjHNLr49gn1e1JFzPZk`, manual-only,
no cron yet -- same prove-by-hand-first discipline the other two
Routines earned before either got a schedule). Firing mechanism now
built and verified live (see below) -- this is the coarse version only,
deliberately scoped down from a fuller design (see "Deferred to a later
version" below).

**Design decisions locked in during drafting (2026-08-19):**
- Checks must be **exact where the convention allows it**, not a fuzzy
  heuristic — the Builder's readiness-marker convention and
  maintenance's pure spec-vs-code-diff nature both admit a deterministic
  gate. No naivety needed for either of today's two agents.
- Where a check is exact, don't try to additionally judge whether a
  matched change "looks meaningful" — any change to a relevant path is a
  candidate, full stop. Filtering by perceived relevance is exactly
  where a real bug could hide; the cost savings already come from most
  weeks having zero relevant changes at all, not from being clever about
  which changes matter.
- The generous/naive-toward-firing bias is reserved for a **future**
  agent whose candidate signal isn't a clean marker or diff (e.g. a
  hypothetical deprecation agent judging "is this domain actually
  unused" — a real judgment call, not a grep). Not needed for the
  current two.
- This version does **not** hand off targeted findings (e.g. "these
  specific domains changed") to the fired agent — each fired agent still
  runs its own full discovery from scratch, same as if a human had fired
  it manually. Targeted hand-off is a real, deferred optimization once
  the coarse fire/no-fire mechanism itself is proven reliable.

**Firing mechanism attempt #1 -- tried, retired (2026-08-19):** the
original draft assumed a spawned Routine session could call
`RemoteTrigger run` directly. That's wrong -- each Routine session's own
bearer token is scoped only to itself (no read access, no access to
other routines, no account data), and there's no tool exposed inside a
spawned session that reaches the cross-routine trigger API. Built and
tested a small Cloudflare Worker relay instead (`fire-relay`, holding
each routine's fire token as an encrypted Worker secret, exposing
`/fire/maintenance` and `/fire/builder` behind one shared credential).
The relay itself worked -- verified live, both paths correctly fired
real, independent sessions (`cse_01RHR591cGcT8HrfFYVUSRkF` for
maintenance, `cse_013u3iuiJxZzExeeqrcNkVrm` for the Builder) when called
manually. But the dispatcher's own live first-fire test found the
sandboxed Routine session's network egress is allowlisted, and the
Worker's `workers.dev` domain isn't on it (`403 policy denial`) -- the
dispatcher itself could never reach the relay. **The Worker has been
deleted** (`wrangler delete fire-relay`, 2026-08-19) and its three
secrets are gone with it; nothing from this attempt survives.

**Firing mechanism attempt #2 -- built and proven live (2026-08-19):**
`.github/workflows/routine-fire.yml`, a `workflow_dispatch`-only
GitHub Actions workflow (never its own schedule). Takes one input,
`target` (`maintenance` or `builder`), and holds the two real fire
tokens as genuine encrypted Actions secrets (`MAINTENANCE_FIRE_TOKEN`,
`BUILDER_FIRE_TOKEN`). Its one job: forward an authenticated POST to
Anthropic's routine-fire endpoint for the requested target. Does no
maintenance/Builder work itself -- that happens in the Routine session
spawned as a result of the call.

Two open questions from attempt #1 were resolved by a live diagnostic
run of the dispatcher trigger itself: (1) raw network egress to
`api.github.com` from inside the sandbox works (`curl` returned
`HTTP_CODE:200`) -- the network-egress block that killed the Cloudflare
attempt was specific to `workers.dev`, not GitHub; (2) the GitHub MCP
connector already available to a Routine session exposes
`mcp__github__actions_run_trigger` with a `run_workflow` method
(`workflow_id` + `ref` + optional `inputs`) that can dispatch a new
workflow run directly -- no separate GitHub credential needed for the
dispatcher at all, since this reuses the connector's own existing auth.

Manually verified end-to-end: `gh workflow run routine-fire.yml -f
target=maintenance` → workflow ran (`HTTP status: 200`) → real,
independent maintenance session confirmed running
(`cse_01LezzAWyFGttb1jYKJSgQAC`). The dispatcher now uses
`actions_run_trigger` for this same call instead of a manual `gh`
invocation.

**First real unattended runs (2026-08-24):** fired twice for real via the
live trigger (no manual `gh` call), both times correctly. Run 1: Builder
candidate found (`labels.md`'s `[ready]` search bullet), fired -- Builder
built it, all validation green, opened PR #65. Maintenance was
dedup-blocked (PR #64 already open). Run 2, after #64 was closed unmerged
and #65 merged: Builder correctly found no candidate (nothing `[ready]`
left unimplemented); maintenance's diff-based check found real
post-merge changes and fired -- maintenance reviewed everything, found
nothing actionable within its scope, correctly opened no PR.

**Known gap, found during run 2's review (2026-08-24):** maintenance's
own `doc_gardener.py` step silently skips its `Verified:`-date
staleness check on a shallow clone -- no error, just fewer findings than
a real check would produce, indistinguishable in the output from an
honest "nothing stale." The dispatcher's maintenance candidate check
(item 2 below) had no way to see this category of finding at all, since
it only looks at `src/todoapp/`/`docs/product-specs/` diffs, not
doc_gardener's own report. Fixed by adding a second, independent
candidate signal (item 2b) that runs `doc_gardener.py` itself, after
unshallowing -- see CANDIDATE CHECKS below. `routine-prompt.md` needs
the same unshallow fix in its own step 1, tracked separately.

**Builder candidate check widened for the new frontend targets**
(2026-08-24): `builder-prompt.md` gained two new discovery modes --
`Frontend: Ready for implementation` on an already-backend-complete
domain missing its frontend entirely, and `Frontend: Needs update` on a
domain whose existing frontend has fallen behind its backend (PR #72).
Item 1 below now checks for both markers too, alongside the existing
`Status: Ready`/`[ready]` checks, so the dispatcher can actually fire
Builder for either target type instead of silently missing them.

**Credential handling, important:** this repo is public. No real secret
value may ever be committed here or anywhere in this file. The fire
tokens live only in GitHub's encrypted Actions secrets, never in this
repo's tracked files, never in the dispatcher's own prompt text -- the
dispatcher doesn't need to hold any of them at all under this
mechanism, only the ability to call `actions_run_trigger`, which it
already has via the connector.

**Wired into merge-gate, proven live (2026-08-25):** `routine-fire.yml`
gained a third `target` choice, `merge_gate`, mapped to
`trig_01EJfBr4rVxfonFknmBaCDn2`, and `scripts/check_dispatcher_scope.py`'s
`VALID_TARGETS` was extended to match. `MERGE_GATE_FIRE_TOKEN` was
provisioned as a GitHub Actions secret and the relay proven end-to-end via
a manual `gh workflow run routine-fire.yml -f target=merge_gate` (HTTP
200, new session spawned). Candidate check 3 below was widened
2026-08-26 to cover any open PR, not just Builder's -- not yet proven via
a genuine Dispatcher-initiated fire finding a real (non-Builder)
candidate, only the underlying relay/token.

## Prompt

You are the Dispatcher Routine for "AI Agent" (SeifEhab30/AI-Agent-framework) -- a third, separate agent from the maintenance Routine (routine-prompt.md), the Builder Routine (builder-prompt.md), and the Merge Gate Routine (merge-gate-prompt.md). Your only job: decide whether any of them likely has real work to do, and fire the ones that do. You never edit repo files, never commit, never open a PR -- your only action is one workflow dispatch per candidate, or doing nothing.

STARTING STATE
- Three known agents, three known fire targets: maintenance, builder, merge_gate. Never any others -- you have no authority to discover or guess at targets beyond what's stated here.
- Firing goes through GitHub Actions, not a direct API call: use ToolSearch to load `mcp__github__actions_run_trigger`, then call it with method `run_workflow`, owner `SeifEhab30`, repo `AI-Agent-framework`, the workflow file `routine-fire.yml`, ref `master`, and inputs `{"target": "maintenance"}`, `{"target": "builder"}`, or `{"target": "merge_gate"}`. That workflow holds the real per-routine fire tokens itself -- you never see or need them, and you need no GitHub credential of your own beyond what the connector already grants you.
- No pre-installed venv, and you don't need one for most checks below -- they're git/grep operations. The exception is `scripts/doc_gardener.py` (candidate check 2b) -- it's pure standard library, no pip install needed, just run it with plain `python3`.
- Candidate check 3 (merge-gate) needs GitHub PR/comment data, not just local git -- use ToolSearch to load `mcp__github__list_pull_requests` and `mcp__github__pull_request_read` up front alongside `actions_run_trigger`.

CANDIDATE CHECKS -- run all three, independently, every time
1. Builder candidate: `git grep` docs/product-specs/*.md for `Status: Ready for implementation` with no matching src/todoapp/<name>/ directory (new-domain target), or `Frontend: Ready for implementation` where src/todoapp/<name>/ already exists but frontend/src/components/<Name>.jsx does NOT (frontend-only target), or `Frontend: Needs update` where both already exist (frontend-update target), or a `[ready]`-tagged bullet not yet present in that domain's service.py (existing-domain target). Any match -> Builder is a candidate. No match -> Builder is not a candidate. This is the same deterministic check the Builder's own discovery step already trusts -- don't add judgment on top of it.
2. Maintenance candidate -- two independent sub-checks, either alone is sufficient:
   - 2a. Diff-based: find the merge commit that closed maintenance's last successful PR (most recent merged PR whose branch was `agentic-maintenance/standing`). `git diff --stat` from that commit to `origin/master`, scoped to `src/todoapp/` and `docs/product-specs/`. Any file touched -> candidate. Don't assess whether a touched file's change looks meaningful -- any touch counts.
   - 2b. doc_gardener-based: run `git rev-parse --is-shallow-repository`; if it prints `true`, run `git fetch --unshallow` first -- skipping this step makes the next check silently under-report, not fail loudly. Then run `python3 scripts/doc_gardener.py`. Any staleness finding in its output -> candidate, independent of 2a's result. This exists because 2a can't see time-based staleness (a `Verified:` date going stale purely from the calendar, with zero file changes) -- doc_gardener.py is the only check that can.
   - Maintenance is a candidate if 2a OR 2b finds something. Neither finding anything -> maintenance is not a candidate.
3. Merge-gate candidate: does any open PR exist that merge-gate hasn't reviewed at its *current* state yet? Widened 2026-08-26 -- no longer filtered to `agentic-build/*` branches, since merge-gate itself now reviews any PR (see merge-gate-prompt.md ELIGIBILITY v3). This is deliberately "does some PR's own current state still need review," not "did the dispatcher itself fire Builder this run" -- the dispatcher never waits on or monitors a fired session (see STOP CONDITIONS), so it can't know that synchronously; checking each open PR's actual current state is the only thing that's both correct and checkable.
   - List every open PR via `mcp__github__list_pull_requests` (state: open) -- no `head.ref` filter. Usually small (at most one Builder PR plus however many human-authored PRs happen to be open).
   - For each such PR: read its comments and its commits via `mcp__github__pull_request_read`. If NO comment's body starts with "Merge Gate" -> never reviewed -> candidate. If one or more such comments exist, compare the most recent one's `createdAt` to the PR's most recent commit's timestamp -- if the latest commit is newer than the latest Merge Gate comment, something changed since that review -> candidate. If the latest Merge Gate comment is newer than the latest commit, it's already been reviewed at this exact state (whether it merged -- in which case the PR wouldn't be open anymore -- or was blocked and is waiting on a human) -> not a candidate, don't re-fire just to get the same answer again.

DEDUP GUARD -- before firing maintenance or builder (merge-gate's own dedup is already folded into check 3 above, not a separate step)
- Check whether that agent's standing branch (`agentic-maintenance/standing` or `agentic-build/standing`) already has an open, unmerged PR. If so, don't fire again -- that agent already has pending work sitting in front of a human, adding another run wouldn't surface anything new until that PR is resolved.

ACTIONS
- Candidate + no dedup block -> call `mcp__github__actions_run_trigger` (method `run_workflow`) as described above for that target. No message override, no targeted hint -- the fired agent runs its own full normal discovery from scratch. Confirm the call succeeded before considering it fired; a tool error means it did NOT fire -- report this, don't retry silently.
- No candidate for an agent, or dedup-blocked -> take no action for that agent. Don't notify, don't report, don't create anything.
- All three no-candidate -> stop silently. This is the expected common case, not an error.

FORBIDDEN ACTIONS -- never, no exceptions
- Never edit, commit, or push any file in the repo.
- Never call any GitHub Actions workflow other than `routine-fire.yml`, and only with `target` set to `maintenance`, `builder`, or `merge_gate`. Never attempt to reach `api.anthropic.com` directly, never attempt to discover or use any trigger id or token yourself.
- Never guess at a candidate signal beyond the checks stated above (1, 2a, 2b, 3). A marker or convention you don't recognize is not a signal to act on -- it's outside this version's scope, leave it alone.
- Never fire an agent more than once in the same dispatcher run.
- Never comment on, review, or otherwise act on any PR yourself -- reading PR/comment data for candidate check 3 is read-only reconnaissance, not action.

STOP CONDITIONS
Run all three candidate checks -> apply dedup guard (maintenance/builder) -> fire what's left -> stop. No follow-up, no monitoring the fired agent's own run -- that agent's own subscribe/check-in logic (already proven working) handles its own PR/merge lifecycle from here.

## Deferred to a later version (not in this draft)

- **Targeted hand-off**: passing the dispatcher's exact diff findings (which domains changed) into the fired agent's run message, so maintenance can skip re-deriving what changed and review only the flagged domains instead of all seven.
- **A third agent's candidate check** (e.g. future deprecation detection) -- will need the naive/generous-bias design discussed but not yet built, since its signal isn't a clean marker or diff.
- **Cadence** -- not yet decided. Needs to be frequent enough to matter (the whole point is catching real work faster/cheaper than a weekly cron) without itself becoming a meaningful cost on its own.
- ~~Whether the dispatcher needs its own scope-guard script~~ -- built (`scripts/check_dispatcher_scope.py`, PR #71): audits `routine-fire.yml`'s GitHub Actions run history over an explicit, caller-supplied time window, since the dispatcher makes no commits for a diff-based check to inspect the way `check_builder_scope.py` does.

## Who may edit this file

A human, always. Same rule as `routine-prompt.md`/`builder-prompt.md`.
