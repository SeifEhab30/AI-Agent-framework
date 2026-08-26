import sqlite3

import pytest

from todoapp.labels.repo import LabelRepo
from todoapp.labels.service import LabelService
from todoapp.labels.types import LabelCreate
from todoapp.platform.errors import NotFoundError, ValidationError


@pytest.fixture
def service() -> LabelService:
    conn = sqlite3.connect(":memory:")
    return LabelService(LabelRepo(conn))


def test_create_and_list(service: LabelService):
    service.create_label(LabelCreate(name="urgent", color="#FF0000"))
    labels = service.list_labels()
    assert len(labels) == 1
    assert labels[0].name == "urgent"
    assert labels[0].color == "#FF0000"


def test_create_rejects_blank_name(service: LabelService):
    with pytest.raises(ValidationError):
        service.create_label(LabelCreate(name="   ", color="#FF0000"))


def test_create_rejects_invalid_color(service: LabelService):
    with pytest.raises(ValidationError):
        service.create_label(LabelCreate(name="urgent", color="red"))


def test_create_rejects_short_hex_color(service: LabelService):
    with pytest.raises(ValidationError):
        service.create_label(LabelCreate(name="urgent", color="#FFF"))


def test_create_rejects_color_with_trailing_newline(service: LabelService):
    with pytest.raises(ValidationError):
        service.create_label(LabelCreate(name="urgent", color="#FF0000\n"))


def test_delete_removes_label(service: LabelService):
    label = service.create_label(LabelCreate(name="urgent", color="#FF0000"))
    service.delete_label(label.id)
    assert service.list_labels() == []


def test_delete_missing_raises(service: LabelService):
    with pytest.raises(NotFoundError):
        service.delete_label("nope")


def test_search_matches_case_insensitive_substring(service: LabelService):
    service.create_label(LabelCreate(name="Urgent", color="#FF0000"))
    service.create_label(LabelCreate(name="Later", color="#00FF00"))
    results = service.search("urg")
    assert len(results) == 1
    assert results[0].name == "Urgent"


def test_search_no_match_returns_empty(service: LabelService):
    service.create_label(LabelCreate(name="Urgent", color="#FF0000"))
    assert service.search("nope") == []


def test_rename_label(service: LabelService):
    label = service.create_label(LabelCreate(name="urgent", color="#FF0000"))
    renamed = service.rename(label.id, "important")
    assert renamed.id == label.id
    assert renamed.color == "#FF0000"


def test_rename_rejects_blank_name(service: LabelService):
    label = service.create_label(LabelCreate(name="urgent", color="#FF0000"))
    with pytest.raises(ValidationError):
        service.rename(label.id, "   ")
