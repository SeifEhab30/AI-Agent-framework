import sqlite3

import pytest

from todoapp.notes.repo import NoteRepo
from todoapp.notes.service import NoteService
from todoapp.notes.types import NoteCreate
from todoapp.platform.errors import NotFoundError, ValidationError


@pytest.fixture
def service() -> NoteService:
    conn = sqlite3.connect(":memory:")
    return NoteService(NoteRepo(conn))


def test_create_and_list(service: NoteService):
    service.create_note(NoteCreate(title="groceries", body="milk"))
    notes = service.list_notes()
    assert len(notes) == 1
    assert notes[0].title == "groceries"
    assert notes[0].body == "milk"


def test_create_rejects_blank_title(service: NoteService):
    with pytest.raises(ValidationError):
        service.create_note(NoteCreate(title="   "))


def test_update_body(service: NoteService):
    note = service.create_note(NoteCreate(title="groceries"))
    updated = service.update_body(note.id, "milk, eggs")
    assert updated.body == "milk, eggs"


def test_update_missing_raises(service: NoteService):
    with pytest.raises(NotFoundError):
        service.update_body("nope", "x")


def test_update_body_can_clear_to_empty(service: NoteService):
    note = service.create_note(NoteCreate(title="groceries", body="milk"))
    updated = service.update_body(note.id, "")
    assert updated.body == ""


def test_delete_note(service: NoteService):
    note = service.create_note(NoteCreate(title="groceries"))
    service.delete_note(note.id)
    assert service.list_notes() == []


def test_delete_missing_raises(service: NoteService):
    with pytest.raises(NotFoundError):
        service.delete_note("nope")
