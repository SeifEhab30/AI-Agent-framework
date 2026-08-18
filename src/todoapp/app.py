"""Combined entrypoint: mounts all domains under one FastAPI app.

Each domain remains independently runnable via its own <domain>.ui:app
(useful for isolated testing); this module composes them together for
running the product as a single service.

Run: uvicorn todoapp.app:app --reload
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from todoapp.bookmarks.runtime import build_runtime as build_bookmarks_runtime
from todoapp.bookmarks.ui import build_router as build_bookmarks_router
from todoapp.labels.runtime import build_runtime as build_labels_runtime
from todoapp.labels.ui import build_router as build_labels_router
from todoapp.notes.runtime import build_runtime as build_notes_runtime
from todoapp.notes.ui import build_router as build_notes_router
from todoapp.reminders.runtime import build_runtime as build_reminders_runtime
from todoapp.reminders.ui import build_router as build_reminders_router
from todoapp.todos.runtime import build_runtime as build_todos_runtime
from todoapp.todos.ui import build_router as build_todos_router
from todoapp.widgets.runtime import build_runtime as build_widgets_runtime
from todoapp.widgets.ui import build_router as build_widgets_router


def build_app() -> FastAPI:
    app = FastAPI(title="Todoapp")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    todos = build_todos_runtime()
    app.include_router(build_todos_router(todos.service, todos.providers.telemetry.event))

    notes = build_notes_runtime()
    app.include_router(build_notes_router(notes.service, notes.providers.telemetry.event))

    bookmarks = build_bookmarks_runtime()
    app.include_router(
        build_bookmarks_router(bookmarks.service, bookmarks.providers.telemetry.event)
    )

    widgets = build_widgets_runtime()
    app.include_router(build_widgets_router(widgets.service, widgets.providers.telemetry.event))

    reminders = build_reminders_runtime()
    app.include_router(
        build_reminders_router(reminders.service, reminders.providers.telemetry.event)
    )

    labels = build_labels_runtime()
    app.include_router(build_labels_router(labels.service, labels.providers.telemetry.event))

    return app


app = build_app()
