# MAP

This file is an index, not documentation. If you need detail, follow a link
below — do not expand this file with prose. Keep it short.

## How to work here

- Read [docs/references/conventions.md](docs/references/conventions.md) before writing code.
- Layering rule: `types → config → repo → service → runtime → ui`, one direction only.
  Details: [docs/architecture/layering.md](docs/architecture/layering.md).
- Cross-cutting concerns (auth, logging, telemetry) are only ever reached through
  `src/todoapp/providers/`, and only `runtime.py` may import from it.

## Standing rules for agents

- Do not delete existing docs or lint/config files without asking first.
- Do not perform destructive git operations (force-push, reset --hard, etc.) without asking first.
- Never commit a real `.env` — only `.env.example` is tracked.
- Run `pre-commit run --all-files` before declaring work done.
- One domain = one folder under `src/todoapp/<domain>/`, with all six layer files.
- Keep this file (`MAP.md`) short. Add detail to `docs/`, not here.

## docs/ index

- `docs/architecture/` — how the system is structured and why (layering rules, module boundaries).
- `docs/design-docs/` — proposals/decisions for a specific piece of work, one file per topic.
- `docs/product-specs/` — what a domain/feature is supposed to do, from a user's perspective.
- `docs/exec-plans/active/` — plans currently being executed.
- `docs/exec-plans/completed/` — finished plans, kept for history.
- `docs/references/` — conventions, style rules, and other lookup material.
- `docs/quality-score/` — output of doc-gardener and other automated health checks.

## Repo layout

```
src/todoapp/
├── app.py       # combined entrypoint — mounts every domain's router under one app
├── providers/   # cross-cutting: DI container, auth, logging, telemetry
├── platform/    # shared utilities (ids, errors) — reuse before hand-rolling
└── <domain>/    # types.py, config.py, repo.py, service.py, runtime.py, ui.py
```

Each domain is also independently runnable via its own `<domain>.ui:app`,
useful for isolated testing.

`frontend/` — separate React + Vite app, calls the backend API at
`localhost:8000`. Not part of the Python layering system; its own
top-level concern. See README.md for dev setup.

## Tooling index

- `ruff` — lint + format. Run: `ruff check .`
- `import-linter` — enforces the layering contract. Run: `lint-imports`
- `pytest` — tests. Run: `pytest -q`
- `scripts/doc_gardener.py` — flags stale docs; `--fix` unlinks broken
  markdown links only. Runs weekly via
  `.github/workflows/doc-gardener.yml`, opening a PR — nothing auto-merges.
- `scripts/check_golden_rules.py` — golden-principle checks not covered by ruff.
  Run: `python scripts/check_golden_rules.py`
- CI (`.github/workflows/ci.yml`) — runs the same checks as pre-commit on
  every push/PR; catches anything a local `--no-verify` skipped.

## Current domains

| Domain    | Spec                                                              |
|-----------|--------------------------------------------------------------------|
| widgets   | [docs/product-specs/widgets-todo.md](docs/product-specs/widgets-todo.md) |
| notes     | [docs/product-specs/notes.md](docs/product-specs/notes.md)         |
| bookmarks | [docs/product-specs/bookmarks.md](docs/product-specs/bookmarks.md) |

## Progress

See [docs/exec-plans/active/milestones.md](docs/exec-plans/active/milestones.md)
for what's done and what's next.

---
Last updated: 2026-08-12. Keep this file short — expand docs/, not this file.
