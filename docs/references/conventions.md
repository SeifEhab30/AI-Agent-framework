# Conventions

Verified: 2026-08-12

- Boundary validation: any function crossing a layer boundary (`service.py`,
  `ui.py`) takes a pydantic model, never a bare `dict`/`Any`.
- Reuse before rewriting: shared helpers (id generation, error types) live in
  `src/todoapp/platform/`. Check there before writing a new helper.
- Every doc in `docs/` carries a `Verified: YYYY-MM-DD` line near the top,
  updated whenever the doc is checked against the code it describes.
- Secrets never get committed. Document required env vars in `.env.example`,
  never in a real `.env`.
- Providers isolation (only `runtime.py` may import `providers/`) is enforced
  by the import-linter `forbidden` contract only — not duplicated as a
  separate check in `scripts/check_golden_rules.py`.
- CI (`.github/workflows/ci.yml`) runs the same checks as pre-commit
  (ruff, ruff format, import-linter, pytest, golden-rules). Pre-commit is
  the fast local gate; CI is the one that can't be skipped with
  `--no-verify`.
