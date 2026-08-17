from collections.abc import Callable

from fastapi import APIRouter, FastAPI, HTTPException

from todoapp.platform.errors import NotFoundError, ValidationError
from todoapp.todos.runtime import build_runtime
from todoapp.todos.service import TodoService
from todoapp.todos.types import Todo, TodoCreate


def build_router(service: TodoService, emit_event: Callable[..., None]) -> APIRouter:
    router = APIRouter(prefix="/todos", tags=["todos"])

    @router.get("", response_model=list[Todo])
    def list_todos() -> list[Todo]:
        return service.list_todos()

    @router.post("", response_model=Todo)
    def create_todo(data: TodoCreate) -> Todo:
        try:
            todo = service.create_todo(data)
        except ValidationError as e:
            raise HTTPException(status_code=422, detail=str(e)) from e
        emit_event("todo_created", todo_id=todo.id)
        return todo

    @router.post("/{todo_id}/toggle", response_model=Todo)
    def toggle_todo(todo_id: str) -> Todo:
        try:
            return service.toggle_done(todo_id)
        except NotFoundError as e:
            raise HTTPException(status_code=404, detail=str(e)) from e

    return router


def build_app() -> FastAPI:
    runtime = build_runtime()
    router = build_router(runtime.service, runtime.providers.telemetry.event)
    runtime.app.include_router(router)
    return runtime.app


app = build_app()
