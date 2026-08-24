from collections.abc import Callable

from fastapi import APIRouter, FastAPI, HTTPException

from todoapp.labels.runtime import build_runtime
from todoapp.labels.service import LabelService
from todoapp.labels.types import Label, LabelCreate
from todoapp.platform.errors import NotFoundError, ValidationError


def build_router(service: LabelService, emit_event: Callable[..., None]) -> APIRouter:
    router = APIRouter(prefix="/labels", tags=["labels"])

    @router.get("", response_model=list[Label])
    def list_labels() -> list[Label]:
        return service.list_labels()

    @router.get("/search", response_model=list[Label])
    def search_labels(q: str) -> list[Label]:
        return service.search(q)

    @router.post("", response_model=Label)
    def create_label(data: LabelCreate) -> Label:
        try:
            label = service.create_label(data)
        except ValidationError as e:
            raise HTTPException(status_code=422, detail=str(e)) from e
        emit_event("label_created", label_id=label.id)
        return label

    @router.delete("/{label_id}", status_code=204)
    def delete_label(label_id: str) -> None:
        try:
            service.delete_label(label_id)
        except NotFoundError as e:
            raise HTTPException(status_code=404, detail=str(e)) from e

    return router


def build_app() -> FastAPI:
    runtime = build_runtime()
    router = build_router(runtime.service, runtime.providers.telemetry.event)
    runtime.app.include_router(router)
    return runtime.app


app = build_app()
