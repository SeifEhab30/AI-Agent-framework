from datetime import UTC, datetime

from todoapp.notes.repo import NoteRepo
from todoapp.notes.types import Note, NoteCreate
from todoapp.platform.errors import NotFoundError, ValidationError
from todoapp.platform.ids import new_id


class NoteService:
    def __init__(self, repo: NoteRepo):
        self._repo = repo

    def create_note(self, data: NoteCreate) -> Note:
        title = data.title.strip()
        if not title:
            raise ValidationError("title must not be empty")
        note = Note(id=new_id(), title=title, body=data.body, created_at=datetime.now(UTC))
        self._repo.add(note)
        return note

    def list_notes(self) -> list[Note]:
        return self._repo.list_all()

    def update_body(self, note_id: str, body: str) -> Note:
        note = self._repo.get(note_id)
        if note is None:
            raise NotFoundError(f"note {note_id} not found")
        self._repo.set_body(note_id, body)
        return self._repo.get(note_id)

    def delete_note(self, note_id: str) -> None:
        note = self._repo.get(note_id)
        if note is None:
            raise NotFoundError(f"note {note_id} not found")
        self._repo.delete(note_id)
