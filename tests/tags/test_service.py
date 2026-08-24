import sqlite3

import pytest

from todoapp.platform.errors import ValidationError
from todoapp.tags.repo import TagRepo
from todoapp.tags.service import TagService
from todoapp.tags.types import TagCreate


@pytest.fixture
def service() -> TagService:
    conn = sqlite3.connect(":memory:")
    return TagService(TagRepo(conn))


def test_create_tag(service: TagService):
    tag = service.create_tag(TagCreate(name="urgent"))
    assert tag.name == "urgent"
    assert tag.id


def test_create_rejects_blank_name(service: TagService):
    with pytest.raises(ValidationError):
        service.create_tag(TagCreate(name="   "))


def test_create_allows_duplicate_names(service: TagService):
    service.create_tag(TagCreate(name="urgent"))
    service.create_tag(TagCreate(name="urgent"))
    tags = service.list_tags_recent()
    assert len(tags) == 2
    assert all(t.name == "urgent" for t in tags)


def test_list_tags_recent_first(service: TagService):
    first = service.create_tag(TagCreate(name="first"))
    second = service.create_tag(TagCreate(name="second"))
    ids = [t.id for t in service.list_tags_recent()]
    assert ids[0] == second.id
    assert ids[-1] == first.id


def test_search_matches_case_insensitive_substring(service: TagService):
    service.create_tag(TagCreate(name="Urgent"))
    service.create_tag(TagCreate(name="Later"))
    results = service.search("URG")
    assert len(results) == 1
    assert results[0].name == "Urgent"


def test_search_no_match_returns_empty(service: TagService):
    service.create_tag(TagCreate(name="Urgent"))
    assert service.search("nope") == []
