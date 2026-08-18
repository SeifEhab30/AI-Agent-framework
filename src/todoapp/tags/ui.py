from collections.abc import Callable

from fastapi import APIRouter, FastAPI, HTTPException

from todoapp.platform.errors import ValidationError
from todoapp.tags.runtime import build_runtime
from todoapp.tags.service import TagService
from todoapp.tags.types import Tag, TagCreate


def build_router(service: TagService, emit_event: Callable[..., None]) -> APIRouter:
    router = APIRouter(prefix="/tags", tags=["tags"])

    @router.get("", response_model=list[Tag])
    def list_tags() -> list[Tag]:
        return service.list_tags_alphabetical()

    @router.get("/recent", response_model=list[Tag])
    def list_tags_recent() -> list[Tag]:
        return service.list_tags_recent()

    @router.post("", response_model=Tag)
    def create_tag(data: TagCreate) -> Tag:
        try:
            tag = service.create_tag(data)
        except ValidationError as e:
            raise HTTPException(status_code=422, detail=str(e)) from e
        emit_event("tag_created", tag_id=tag.id)
        return tag

    return router


def build_app() -> FastAPI:
    runtime = build_runtime()
    router = build_router(runtime.service, runtime.providers.telemetry.event)
    runtime.app.include_router(router)
    return runtime.app


app = build_app()
