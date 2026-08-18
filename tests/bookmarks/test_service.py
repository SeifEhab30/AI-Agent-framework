import sqlite3

import pytest

from todoapp.bookmarks.repo import BookmarkRepo
from todoapp.bookmarks.service import BookmarkService
from todoapp.bookmarks.types import BookmarkCreate
from todoapp.platform.errors import NotFoundError, ValidationError


@pytest.fixture
def service() -> BookmarkService:
    conn = sqlite3.connect(":memory:")
    return BookmarkService(BookmarkRepo(conn))


def test_create_and_list(service: BookmarkService):
    service.create_bookmark(BookmarkCreate(url="https://example.com", title="Example"))
    bookmarks = service.list_bookmarks()
    assert len(bookmarks) == 1
    assert bookmarks[0].url == "https://example.com"
    assert bookmarks[0].title == "Example"


def test_create_rejects_blank_url(service: BookmarkService):
    with pytest.raises(ValidationError):
        service.create_bookmark(BookmarkCreate(url="   ", title="Example"))


def test_create_rejects_blank_title(service: BookmarkService):
    with pytest.raises(ValidationError):
        service.create_bookmark(BookmarkCreate(url="https://example.com", title="   "))


def test_rename(service: BookmarkService):
    bookmark = service.create_bookmark(BookmarkCreate(url="https://example.com", title="Example"))
    renamed = service.rename(bookmark.id, "New Title")
    assert renamed.title == "New Title"


def test_rename_missing_raises(service: BookmarkService):
    with pytest.raises(NotFoundError):
        service.rename("nope", "x")


def test_search_matches_case_insensitive_substring(service: BookmarkService):
    service.create_bookmark(BookmarkCreate(url="https://example.com", title="Example Docs"))
    service.create_bookmark(BookmarkCreate(url="https://other.com", title="Other Site"))
    results = service.search("exam")
    assert len(results) == 1
    assert results[0].title == "Example Docs"


def test_search_no_match_returns_empty(service: BookmarkService):
    service.create_bookmark(BookmarkCreate(url="https://example.com", title="Example Docs"))
    assert service.search("nope") == []
