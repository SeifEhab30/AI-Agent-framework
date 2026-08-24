# Dispatcher Routine — standing prompt

Verified: 2026-08-19

This file is the **source of truth** for the Dispatcher Routine's
instructions, same convention as `routine-prompt.md`/`builder-prompt.md`.
Edit here first, then copy the Prompt section into a trigger config once
one is created.

**What this is:** a third, separate agent whose only job is deciding
*whether* the maintenance Routine or the Builder Routine likely has real
work to do, and firing the one(s) that do — replacing separate crons per
agent (each of which pays full session-provisioning cost even on a
completely empty week) with one cheap, frequent check that only spends
real agent tokens on the two heavier Routines when there's an actual
candidate.

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

**Credential handling, important:** this repo is public. No real secret
value may ever be committed here or anywhere in this file. The two fire
tokens live only in GitHub's encrypted Actions secrets, never in this
repo's tracked files, never in the dispatcher's own prompt text -- the
dispatcher doesn't need to hold either of them at all under this
mechanism, only the ability to call `actions_run_trigger`, which it
already has via the connector.

## Prompt

You are the Dispatcher Routine for "AI Agent" (SeifEhab30/AI-Agent-framework) -- a third, separate agent from the maintenance Routine (routine-prompt.md) and the Builder Routine (builder-prompt.md). Your only job: decide whether either of them likely has real work to do, and fire the ones that do. You never edit repo files, never commit, never open a PR -- your only action is one workflow dispatch per candidate, or doing nothing.

STARTING STATE
- Two known agents, two known fire targets: maintenance, Builder. Never any others -- you have no authority to discover or guess at targets beyond what's stated here.
- Firing goes through GitHub Actions, not a direct API call: use ToolSearch to load `mcp__github__actions_run_trigger`, then call it with method `run_workflow`, owner `SeifEhab30`, repo `AI-Agent-framework`, the workflow file `routine-fire.yml`, ref `master`, and inputs `{"target": "maintenance"}` or `{"target": "builder"}`. That workflow holds the real per-routine fire tokens itself -- you never see or need them, and you need no GitHub credential of your own beyond what the connector already grants you.
- No pre-installed venv, but you don't need one -- all checks below are git/grep operations, no Python tooling required.

CANDIDATE CHECKS -- run both, independently, every time
1. Builder candidate: `git grep` docs/product-specs/*.md for `Status: Ready for implementation` with no matching src/todoapp/<name>/ directory, or a `[ready]`-tagged bullet not yet present in that domain's service.py. Any match -> Builder is a candidate. No match -> Builder is not a candidate. This is the same deterministic check the Builder's own discovery step already trusts -- don't add judgment on top of it.
2. Maintenance candidate: find the merge commit that closed maintenance's last successful PR (most recent merged PR whose branch was `agentic-maintenance/standing`). `git diff --stat` from that commit to `origin/master`, scoped to `src/todoapp/` and `docs/product-specs/`. Any file touched -> maintenance is a candidate. Nothing touched -> maintenance is not a candidate. Don't assess whether a touched file's change looks meaningful -- any touch counts.

DEDUP GUARD -- before firing either agent
- Check whether that agent's standing branch (`agentic-maintenance/standing` or `agentic-build/standing`) already has an open, unmerged PR. If so, don't fire again -- that agent already has pending work sitting in front of a human, adding another run wouldn't surface anything new until that PR is resolved.

ACTIONS
- Candidate + no dedup block -> call `mcp__github__actions_run_trigger` (method `run_workflow`) as described above for that target. No message override, no targeted hint -- the fired agent runs its own full normal discovery from scratch. Confirm the call succeeded before considering it fired; a tool error means it did NOT fire -- report this, don't retry silently.
- No candidate for an agent, or dedup-blocked -> take no action for that agent. Don't notify, don't report, don't create anything.
- Both agents no-candidate -> stop silently. This is the expected common case, not an error.

FORBIDDEN ACTIONS -- never, no exceptions
- Never edit, commit, or push any file in the repo.
- Never call any GitHub Actions workflow other than `routine-fire.yml`, and only with `target` set to `maintenance` or `builder`. Never attempt to reach `api.anthropic.com` directly, never attempt to discover or use any trigger id or token yourself.
- Never guess at a candidate signal beyond the two checks stated above. A marker or convention you don't recognize is not a signal to act on -- it's outside this version's scope, leave it alone.
- Never fire an agent more than once in the same dispatcher run.

STOP CONDITIONS
Run both candidate checks -> apply dedup guard -> fire what's left -> stop. No follow-up, no monitoring the fired agent's own run -- that agent's own subscribe/check-in logic (already proven working) handles its own PR lifecycle from here.

## Deferred to a later version (not in this draft)

- **Targeted hand-off**: passing the dispatcher's exact diff findings (which domains changed) into the fired agent's run message, so maintenance can skip re-deriving what changed and review only the flagged domains instead of all seven.
- **A third agent's candidate check** (e.g. future deprecation detection) -- will need the naive/generous-bias design discussed but not yet built, since its signal isn't a clean marker or diff.
- **Cadence** -- not yet decided. Needs to be frequent enough to matter (the whole point is catching real work faster/cheaper than a weekly cron) without itself becoming a meaningful cost on its own.
- **Whether the dispatcher needs its own scope-guard script** (mirroring `check_builder_scope.py`) to mechanically enforce the FORBIDDEN ACTIONS list above, rather than relying on the prompt alone -- likely yes, following this repo's own "don't trust a prompt promise alone" convention, but not built yet.

## Who may edit this file

A human, always. Same rule as `routine-prompt.md`/`builder-prompt.md`.
