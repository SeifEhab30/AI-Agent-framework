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
