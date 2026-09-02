# AI Agent — Todoapp

> **Status: Work in progress, handed off.** The original author's internship
> ended and this project is now looking for its next maintainer. The app and
> the four agent Routines described below are functional and were proven
> live (see `docs/exec-plans/active/milestones.md` for the run history), but
> the framework itself — the pattern of autonomous agents maintaining and
> extending a codebase under mechanical guardrails — is an ongoing
> experiment, not a finished product. **Start with [TO_CONTINUE.md](TO_CONTINUE.md)**
> for the full picture (what's built, what's proven, what's still open) and
> [memory.md](memory.md) for ready-to-paste prompts if you're picking this
> up with Claude Code, Codex, or Cursor. **Fork this repo before working
> on it** — you won't have push access to the original, and a fork is
> what lets you set your own GitHub Actions secrets, branch protection,
> and RemoteTriggers without touching anyone else's.

A small FastAPI + SQLite demo app used as a reference implementation for an
agent-driven engineering workflow: enforced layered architecture, structured
docs, doc staleness checks, lint-enforced golden principles, and four
autonomous agent Routines (Maintenance, Builder, Dispatcher, Merge Gate)
that maintain and extend it with minimal human intervention.

## 📍 New here? Read these two files first

| File | What it's for |
|---|---|
| **[TO_CONTINUE.md](TO_CONTINUE.md)** | The actual handoff doc — architecture, the four agents' current state, open items, and approaches already tried and abandoned (with why). Read this before touching anything. |
| **[memory.md](memory.md)** | Ready-to-paste briefing prompts for Claude Code, Codex, and Cursor, so a fresh AI session gets oriented in one turn. |

Everything else below (`MAP.md`, this README's own setup steps) is
detail those two documents will send you to when you need it — they're
not a replacement for reading `TO_CONTINUE.md` first.

## Setup, step by step

This section is for someone picking up the project cold. It covers getting
the app running locally, then (optionally, once you're comfortable with the
codebase) standing up the four agent Routines against your own fork.

### 1. Fork, clone, and install

**Fork this repo first** (GitHub's "Fork" button, or `gh repo fork`) —
don't clone the original directly. You won't have write access to it,
and everything past step 5 below (secrets, branch protection,
RemoteTriggers) needs a repo you actually control.

```bash
git clone <your-fork-url>
cd <repo-directory>
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Set up pre-commit hooks

The repo enforces `ruff`, `ruff-format`, `import-linter`, `pytest`, and
`scripts/check_golden_rules.py` on every commit via `.pre-commit-config.yaml`.

```bash
pip install pre-commit
pre-commit install
```

### 3. Run the backend

```bash
cp .env.example .env   # optional -- defaults work as-is
uvicorn todoapp.app:app --reload
```

Runs todos, notes, bookmarks, widgets, reminders, labels, and tags together
under one app. Each domain is also independently runnable (e.g.
`uvicorn todoapp.todos.ui:app`) for isolated testing.

### 4. Run the frontend (optional)

```bash
cd frontend
npm install
npm run dev
```

React + Vite, talks to the backend at `http://localhost:8000` (CORS is
enabled for `http://localhost:5173`, the Vite dev server's default port).
Run the backend first. Not every domain has frontend wiring yet — see
`TO_CONTINUE.md` for which ones do.

### 5. Confirm the validation suite passes

```bash
ruff check .
ruff format --check .
lint-imports
pytest -q
python scripts/check_golden_rules.py
python scripts/doc_gardener.py
```

The first five should pass clean on a fresh checkout. `doc_gardener.py`
is the one exception worth knowing about up front: it currently reports
a handful of pre-existing "possibly stale" findings (exit code 0 —
findings, not failures) on spec docs whose `Verified:` date has fallen
behind a referenced source file's last change. This is normal, expected
output — it's exactly what the tool is for, and clearing that queue is
routine Maintenance-agent work, not a sign your checkout is broken. See
`docs/quality-score/findings-log.md`'s conventions for how findings are
tracked. The other five checks are pass/fail with no such caveat — if
any of *those* fail on a clean checkout, something is actually wrong.

### 6. (Optional) Stand up the agent Routines on your own fork

The four Routines — Maintenance, Builder, Dispatcher, Merge Gate — are
RemoteTrigger-based Claude Code sessions, not code that lives in this repo
in an executable form. Their instructions live as version-controlled
"source of truth" docs under `docs/references/`:

- `docs/references/routine-prompt.md` — Maintenance (finds and fixes
  spec-vs-code drift, doc staleness; never builds new features)
- `docs/references/builder-prompt.md` — Builder (implements new,
  human-authored, ready-marked specs; never touches existing behavior
  outside its one target)
- `docs/references/dispatcher-prompt.md` — Dispatcher (polls whether
  Maintenance/Builder have real work, fires them, then checks for
  mergeable PRs and fires Merge Gate)
- `docs/references/merge-gate-prompt.md` — Merge Gate (mechanically +
  semantically reviews open PRs, auto-merges the ones that are safe)

**Every one of these prompt docs currently has a `<OWNER>/<REPO>` placeholder**
where the original repo's GitHub path used to be hardcoded — replace it with
your fork's actual `owner/repo` before creating a trigger from it. This was
done deliberately as part of the handoff so the prompts are copy-paste-ready
for a new repo rather than silently pointing at someone else's fork. This
is one of *two* separate places that need your own values, not the only
one — `.github/workflows/routine-fire.yml` has its own placeholders
(trigger IDs, step 4 below) that are easy to miss since they're in a
workflow file, not a prompt doc.

To actually stand one up:

1. Read the target prompt doc in full — each one documents its own scope
   guard, forbidden actions, and (for Builder/Merge Gate/Dispatcher) how it
   was proven live, in its own "Status" section.
2. Create a RemoteTrigger with the doc's "Prompt" section as the trigger's
   message content, pointed at your fork. **Note down the trigger's ID**
   (`trig_...`, shown when you create it) — you'll need it in step 4.
3. Start manual-only (no cron) and run it by hand at least once, checking
   the resulting PR or action against the doc's own scope guard, before
   trusting it on a schedule — this is the same "prove narrow, then widen"
   discipline every Routine in this repo was built with.
4. For the Dispatcher to be able to fire Maintenance/Builder/Merge Gate
   (rather than you firing each one by hand), two things need to happen
   in `.github/workflows/routine-fire.yml`, **not just the secrets** —
   the trigger IDs in its `case` block are placeholders
   (`<MAINTENANCE_TRIGGER_ID>`, `<BUILDER_TRIGGER_ID>`,
   `<MERGE_GATE_TRIGGER_ID>`) and the workflow deliberately fails loudly
   if you fire it without replacing them:
   - **Edit the three `TRIGGER_ID=` lines** in that file's `case` block,
     replacing each placeholder with the actual trigger ID from step 2
     for that Routine.
   - **Add the three GitHub Actions secrets** — `MAINTENANCE_FIRE_TOKEN`,
     `BUILDER_FIRE_TOKEN`, `MERGE_GATE_FIRE_TOKEN`. Each one **is that
     Routine's own RemoteTrigger API token** — the same bearer token
     `routine-fire.yml` uses to call
     `POST https://api.anthropic.com/v1/claude_code/routines/<trigger_id>/fire`.
     It's shown once, when you create the trigger, in the claude.ai
     Routines/Automations UI (not retrievable from the CLI/API after the
     fact) — copy it then, or regenerate it from that UI if you missed it.
   Store each secret with:
   ```bash
   gh secret set MAINTENANCE_FIRE_TOKEN --body "<token from that trigger's page>"
   gh secret set BUILDER_FIRE_TOKEN --body "<token from that trigger's page>"
   gh secret set MERGE_GATE_FIRE_TOKEN --body "<token from that trigger's page>"
   ```
   Dispatcher doesn't need its own fire token — it's the one firing the
   others, via `mcp__github__actions_run_trigger` calling this workflow,
   not the reverse. Skip this step entirely if you're firing every
   Routine by hand instead of through the Dispatcher.

**Read `TO_CONTINUE.md` before doing any of this** — it has the full
history of what's been proven, what broke and how it was fixed, and what's
still an open question, so you're not rediscovering things the hard way.

## Frontend

See step 4 above.
