from datetime import UTC, datetime

from todoapp.bookmarks.repo import BookmarkRepo
from todoapp.bookmarks.types import Bookmark, BookmarkCreate
from todoapp.platform.errors import NotFoundError, ValidationError
from todoapp.platform.ids import new_id


class BookmarkService:
    def __init__(self, repo: BookmarkRepo):
        self._repo = repo

    def create_bookmark(self, data: BookmarkCreate) -> Bookmark:
        url = data.url.strip()
        title = data.title.strip()
        if not url:
            raise ValidationError("url must not be empty")
        if not title:
            raise ValidationError("title must not be empty")
        bookmark = Bookmark(id=new_id(), url=url, title=title, created_at=datetime.now(UTC))
        self._repo.add(bookmark)
        return bookmark

    def list_bookmarks(self) -> list[Bookmark]:
        return self._repo.list_all()

    def search(self, query: str) -> list[Bookmark]:
        query = query.lower()
        return [b for b in self._repo.list_all() if query in b.title.lower()]

    def rename(self, bookmark_id: str, title: str) -> Bookmark:
        bookmark = self._repo.get(bookmark_id)
        if bookmark is None:
            raise NotFoundError(f"bookmark {bookmark_id} not found")
        title = title.strip()
        if not title:
            raise ValidationError("title must not be empty")
        self._repo.set_title(bookmark_id, title)
        return self._repo.get(bookmark_id)
