"""Combined entrypoint: mounts all domains under one FastAPI app.

Each domain remains independently runnable via its own <domain>.ui:app
(useful for isolated testing); this module composes them together for
running the product as a single service.

Run: uvicorn todoapp.app:app --reload
"""

from fastapi import FastAPI

from todoapp.bookmarks.runtime import build_runtime as build_bookmarks_runtime
from todoapp.bookmarks.ui import build_router as build_bookmarks_router
from todoapp.notes.runtime import build_runtime as build_notes_runtime
from todoapp.notes.ui import build_router as build_notes_router
from todoapp.widgets.runtime import build_runtime as build_widgets_runtime
from todoapp.widgets.ui import build_router as build_widgets_router


def build_app() -> FastAPI:
    app = FastAPI(title="Todoapp")

    widgets = build_widgets_runtime()
    app.include_router(build_widgets_router(widgets.service, widgets.providers.telemetry.event))

    notes = build_notes_runtime()
    app.include_router(build_notes_router(notes.service, notes.providers.telemetry.event))

    bookmarks = build_bookmarks_runtime()
    app.include_router(
        build_bookmarks_router(bookmarks.service, bookmarks.providers.telemetry.event)
    )

    return app


app = build_app()
