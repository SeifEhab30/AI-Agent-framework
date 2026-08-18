from collections.abc import Callable

from fastapi import APIRouter, FastAPI, HTTPException

from todoapp.bookmarks.runtime import build_runtime
from todoapp.bookmarks.service import BookmarkService
from todoapp.bookmarks.types import Bookmark, BookmarkCreate, BookmarkUpdate
from todoapp.platform.errors import NotFoundError, ValidationError


def build_router(service: BookmarkService, emit_event: Callable[..., None]) -> APIRouter:
    router = APIRouter(prefix="/bookmarks", tags=["bookmarks"])

    @router.get("", response_model=list[Bookmark])
    def list_bookmarks() -> list[Bookmark]:
        return service.list_bookmarks()

    @router.post("", response_model=Bookmark)
    def create_bookmark(data: BookmarkCreate) -> Bookmark:
        try:
            bookmark = service.create_bookmark(data)
        except ValidationError as e:
            raise HTTPException(status_code=422, detail=str(e)) from e
        emit_event("bookmark_created", bookmark_id=bookmark.id)
        return bookmark

    @router.get("/search", response_model=list[Bookmark])
    def search_bookmarks(q: str) -> list[Bookmark]:
        return service.search(q)

    @router.post("/{bookmark_id}", response_model=Bookmark)
    def rename_bookmark(bookmark_id: str, data: BookmarkUpdate) -> Bookmark:
        try:
            return service.rename(bookmark_id, data.title)
        except NotFoundError as e:
            raise HTTPException(status_code=404, detail=str(e)) from e
        except ValidationError as e:
            raise HTTPException(status_code=422, detail=str(e)) from e

    return router


def build_app() -> FastAPI:
    runtime = build_runtime()
    router = build_router(runtime.service, runtime.providers.telemetry.event)
    runtime.app.include_router(router)
    return runtime.app


app = build_app()
