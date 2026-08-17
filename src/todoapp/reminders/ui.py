from collections.abc import Callable

from fastapi import APIRouter, FastAPI, HTTPException

from todoapp.platform.errors import NotFoundError, ValidationError
from todoapp.reminders.runtime import build_runtime
from todoapp.reminders.service import ReminderService
from todoapp.reminders.types import Reminder, ReminderCreate


def build_router(service: ReminderService, emit_event: Callable[..., None]) -> APIRouter:
    router = APIRouter(prefix="/reminders", tags=["reminders"])

    @router.get("", response_model=list[Reminder])
    def list_reminders() -> list[Reminder]:
        return service.list_reminders()

    @router.post("", response_model=Reminder)
    def create_reminder(data: ReminderCreate) -> Reminder:
        try:
            reminder = service.create_reminder(data)
        except ValidationError as e:
            raise HTTPException(status_code=422, detail=str(e)) from e
        emit_event("reminder_created", reminder_id=reminder.id)
        return reminder

    @router.post("/{reminder_id}/done", response_model=Reminder)
    def mark_reminder_done(reminder_id: str) -> Reminder:
        try:
            return service.mark_done(reminder_id)
        except NotFoundError as e:
            raise HTTPException(status_code=404, detail=str(e)) from e

    @router.delete("/{reminder_id}", status_code=204)
    def delete_reminder(reminder_id: str) -> None:
        try:
            service.delete_reminder(reminder_id)
        except NotFoundError as e:
            raise HTTPException(status_code=404, detail=str(e)) from e

    return router


def build_app() -> FastAPI:
    runtime = build_runtime()
    router = build_router(runtime.service, runtime.providers.telemetry.event)
    runtime.app.include_router(router)
    return runtime.app


app = build_app()
