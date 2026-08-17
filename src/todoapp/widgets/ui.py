from collections.abc import Callable

from fastapi import APIRouter, FastAPI, HTTPException

from todoapp.platform.errors import NotFoundError, ValidationError
from todoapp.widgets.runtime import build_runtime
from todoapp.widgets.service import WidgetService
from todoapp.widgets.types import Widget, WidgetCreate, WidgetUpdate


def build_router(service: WidgetService, emit_event: Callable[..., None]) -> APIRouter:
    router = APIRouter(prefix="/widgets", tags=["widgets"])

    @router.get("", response_model=list[Widget])
    def list_widgets() -> list[Widget]:
        return service.list_widgets()

    @router.post("", response_model=Widget)
    def create_widget(data: WidgetCreate) -> Widget:
        try:
            widget = service.create_widget(data)
        except ValidationError as e:
            raise HTTPException(status_code=422, detail=str(e)) from e
        emit_event("widget_created", widget_id=widget.id)
        return widget

    @router.post("/{widget_id}", response_model=Widget)
    def set_widget_value(widget_id: str, data: WidgetUpdate) -> Widget:
        try:
            return service.set_value(widget_id, data.value)
        except NotFoundError as e:
            raise HTTPException(status_code=404, detail=str(e)) from e

    return router


def build_app() -> FastAPI:
    runtime = build_runtime()
    router = build_router(runtime.service, runtime.providers.telemetry.event)
    runtime.app.include_router(router)
    return runtime.app


app = build_app()
