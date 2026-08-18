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


def test_delete_removes_label(service: LabelService):
    label = service.create_label(LabelCreate(name="urgent", color="#FF0000"))
    service.delete_label(label.id)
    assert service.list_labels() == []


def test_delete_missing_raises(service: LabelService):
    with pytest.raises(NotFoundError):
        service.delete_label("nope")
