from typing import Callable

from fastapi import APIRouter, FastAPI, HTTPException

from todoapp.platform.errors import NotFoundError, ValidationError
from todoapp.widgets.runtime import build_runtime
from todoapp.widgets.service import WidgetService
from todoapp.widgets.types import Widget, WidgetCreate


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
            raise HTTPException(status_code=422, detail=str(e))
        emit_event("widget_created", widget_id=widget.id)
        return widget

    @router.post("/{widget_id}/toggle", response_model=Widget)
    def toggle_widget(widget_id: str) -> Widget:
        try:
            return service.toggle_done(widget_id)
        except NotFoundError as e:
            raise HTTPException(status_code=404, detail=str(e))

    return router


def build_app() -> FastAPI:
    runtime = build_runtime()
    router = build_router(runtime.service, runtime.providers.telemetry.event)
    runtime.app.include_router(router)
    return runtime.app


app = build_app()
