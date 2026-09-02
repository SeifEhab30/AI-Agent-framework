# memory.md — paste-and-continue prompts

This file exists so that whoever continues this project can hand one
prompt to their AI coding assistant and get it oriented in a single
turn, instead of re-deriving the project's context by trial and error.

Pick the block for your tool, paste it as your **first message** in a
fresh session/chat scoped to this repo, then let the assistant read
`TO_CONTINUE.md` and `README.md` as its first actions. Each prompt below
is written to front-load intent, constraints, and the exact reading
order — don't shorten it; the specificity is what keeps the assistant
from re-discovering things the hard way.

---

## Claude Code

```
You're picking up an existing project mid-stream — the original author's
internship ended and this repo was handed off. Before doing anything
else:

1. Read TO_CONTINUE.md in full — it's the authoritative handoff doc:
   what this project is, the core design principles it follows, current
   state of all four autonomous agent Routines (Maintenance, Builder,
   Dispatcher, Merge Gate), known open items, and a section on
   approaches that were tried and abandoned (with why) — read that
   section especially closely so you don't re-propose something already
   rejected for a real reason.
2. Read README.md and follow its setup steps to get the app running
   locally and confirm the validation suite passes
   (ruff/ruff-format/lint-imports/pytest/check_golden_rules.py all
   pass/fail cleanly; doc_gardener.py is the one exception — it may
   report pre-existing "possibly stale" findings on exit 0, which is
   normal, expected output, not a broken checkout — see README.md's own
   note on this before treating a doc_gardener finding as something you
   need to fix).
3. Read docs/exec-plans/active/milestones.md end to end — it's the real,
   chronological run history and answers most "why is it built this
   way" questions before you have to ask. It is also, itself, not fully
   up to date — TO_CONTINUE.md section 5 documents the specific places
   it currently contradicts reality (and contradicts itself between an
   M10 and an M14 entry). Read that caveat too, don't take every claim
   in milestones.md at face value.
4. Read MAP.md and docs/references/conventions.md before touching any
   code — this repo enforces a strict layering convention
   (types→config→repo→service→runtime→ui) via import-linter, plus
   golden-rule lints (scripts/check_golden_rules.py) for patterns ruff
   can't catch.

Do not create a new agent Routine, change scheduling/cron on any
existing one, or widen any Routine's scope guard until you've read
TO_CONTINUE.md section 5 (open items) and section 6 (approaches tried
and abandoned) — several tempting-looking changes there are already
known dead ends, with the specific reason documented.

Once you've done the above, tell me in a few sentences: what state the
project is actually in right now, and what you think the single most
valuable next step is. Don't start implementing anything yet — I want to
confirm direction with you first.
```

---

## Codex (OpenAI)

```
Context: continuing a handed-off project. The original author finished
their internship; this repo is now open for a new maintainer. Read
TO_CONTINUE.md first — it is the single source of truth for project
state, design principles, and a documented list of approaches already
tried and abandoned (with the specific reason each failed). Do not
propose re-trying anything listed there without addressing why it failed
last time.

After TO_CONTINUE.md, read README.md and run its setup steps exactly —
venv, pre-commit install, backend run, validation suite
(ruff/ruff-format/lint-imports/pytest/check_golden_rules.py). Confirm
those pass clean before treating the checkout as working.
doc_gardener.py is separate: it may report pre-existing "possibly
stale" findings on exit 0 — expected, not a failure, do not "fix" these
unprompted.

Then read docs/exec-plans/active/milestones.md for the full chronological
history — note that TO_CONTINUE.md section 5 documents specific claims
in this file that are currently stale or self-contradictory, so verify
against that section before relying on a specific milestones.md claim —
and MAP.md + docs/references/conventions.md for the architecture
rules (strict one-direction layering: types→config→repo→service→
runtime→ui, enforced by import-linter; golden-rule lints for anything
ruff can't catch).

This repo has four autonomous agent "Routines" (Maintenance, Builder,
Dispatcher, Merge Gate) — instructions for each live in
docs/references/*-prompt.md, not in this codebase's runtime code. Their
prompt docs use <OWNER>/<REPO> placeholders where this specific repo's
GitHub path used to be hardcoded; if you stand any of them up, replace
those placeholders with the actual fork path first.

Output format: after reading, give me a short status summary (project
state, what's proven vs. still open) and your recommended next step.
Do not start writing code or standing up any agent trigger until I
confirm direction.
```

---

## Cursor

```
I'm picking up someone else's project — read these files in this exact
order before we do anything else:

1. TO_CONTINUE.md — the handoff doc. Covers what this project is, the
   core design principles (mechanical enforcement over prompt promises,
   prove-narrow-then-widen, recurring-bug-becomes-a-check,
   full-inventory traceability), current state of all four autonomous
   agent Routines, open items, and — importantly — a section listing
   approaches that were tried and abandoned, with the actual reason each
   one failed. Treat that section as a list of known dead ends, not
   inspiration.
2. README.md — follow its numbered setup steps (venv, pre-commit,
   backend, frontend, validation suite) and confirm the pass/fail checks
   pass clean on this checkout. doc_gardener.py is the one step that
   isn't pass/fail — README explains why; don't treat its findings as a
   broken checkout or something to fix unprompted.
3. docs/exec-plans/active/milestones.md — full chronological project
   history, most "why is this built this way" answers are in here, BUT
   TO_CONTINUE.md section 5 documents specific, verified places where
   this file contradicts current reality (an M10 entry that disagrees
   with M14, and two stale Backlog claims) — read that caveat before
   trusting a specific claim in milestones.md over TO_CONTINUE.md.
4. MAP.md and docs/references/conventions.md — the architecture rules
   (strict layering, one direction only, import-linter-enforced) before
   touching any source file.

Constraints: don't change any agent Routine's scope guard, scheduling,
or eligibility rules, and don't stand up a new agent trigger, until
you've confirmed with me what we're actually doing next. The four
Routines' instructions live in docs/references/*-prompt.md as
version-controlled prompts (not application code) — each has its own
"Status" section, generally the most current source for what's proven
on that specific Routine. If a Status section and TO_CONTINUE.md ever
disagree, prefer whichever is more recently dated, and say so explicitly
rather than picking one silently — don't default to trusting either one
by rule alone.

After reading, summarize back to me: current project state, and the one
thing you'd recommend doing next and why. Wait for my go-ahead before
writing any code.
```

---

## Notes for whoever pastes these

- All three prompts deliberately end in "confirm before acting" — this
  project's own working discipline (see `TO_CONTINUE.md` §2 and §6) is
  to prove things narrowly and get explicit sign-off before widening
  scope, especially around the four autonomous agents. Keep that
  discipline with your own assistant too, not just the agents this repo
  already has.
- If your assistant asks whether it's safe to run one of the four
  Routines live (fire a RemoteTrigger, merge a PR automatically, etc.) —
  that's a real, hard-to-reverse action against a real GitHub repo. Read
  `TO_CONTINUE.md` §6's incident writeups before saying yes casually;
  more than one real mistake happened this way during development, all
  caught and fixed, but avoidable with a little more caution up front.
