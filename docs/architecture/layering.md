# Layering

Verified: 2026-08-12

Every domain under `src/todoapp/<domain>/` has exactly six files, imported in
one direction only:

```
types → config → repo → service → runtime → ui
```

A lower layer must never import a higher one. `types.py` imports nothing
from its own domain; `ui.py` may import everything below it.

## Providers

Cross-cutting concerns (auth, logging, telemetry) live in
`src/todoapp/providers/` and are never imported directly by `types`,
`config`, `repo`, or `service`. Only `runtime.py` imports `providers`; it
builds a `Providers` instance and passes the pieces each layer needs into
constructors (explicit dependency injection, no DI framework).

## Enforcement

`import-linter` (`lint-imports`) enforces this mechanically via contracts in
`pyproject.toml`:
- a `layers` contract on `types < config < repo < service < runtime < ui`
- a `forbidden` contract restricting `providers` imports to `runtime.py`

Run `lint-imports` locally or via `pre-commit run --all-files`.

## Entrypoint note

Because `runtime.py` sits below `ui.py`, it must not import `ui.py` to mount
routes. Instead `runtime.py` exposes a `build_runtime()` function returning
the app instance, service, and providers; `ui.py` (the top layer) imports
`runtime`, builds the router, and mounts it. `ui.py` is therefore the actual
ASGI entrypoint (e.g. `uvicorn todoapp.widgets.ui:app`), not `runtime.py`.
