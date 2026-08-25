from collections.abc import Callable

from fastapi import APIRouter, FastAPI, HTTPException

from todoapp.notes.runtime import build_runtime
from todoapp.notes.service import NoteService
from todoapp.notes.types import Note, NoteCreate, NoteUpdate
from todoapp.platform.errors import NotFoundError, ValidationError


def build_router(service: NoteService, emit_event: Callable[..., None]) -> APIRouter:
    router = APIRouter(prefix="/notes", tags=["notes"])

    @router.get("", response_model=list[Note])
    def list_notes() -> list[Note]:
        return service.list_notes()

    @router.post("", response_model=Note)
    def create_note(data: NoteCreate) -> Note:
        try:
            note = service.create_note(data)
        except ValidationError as e:
            raise HTTPException(status_code=422, detail=str(e)) from e
        emit_event("note_created", note_id=note.id)
        return note

    @router.get("/search", response_model=list[Note])
    def search_notes(q: str) -> list[Note]:
        return service.search(q)

    @router.post("/{note_id}", response_model=Note)
    def update_note(note_id: str, data: NoteUpdate) -> Note:
        try:
            return service.update_body(note_id, data.body)
        except NotFoundError as e:
            raise HTTPException(status_code=404, detail=str(e)) from e

    return router


def build_app() -> FastAPI:
    runtime = build_runtime()
    router = build_router(runtime.service, runtime.providers.telemetry.event)
    runtime.app.include_router(router)
    return runtime.app


app = build_app()
