import sqlite3
from datetime import datetime

from todoapp.notes.types import Note

_CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS notes (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    body TEXT NOT NULL,
    created_at TEXT NOT NULL
)
"""


class NoteRepo:
    def __init__(self, conn: sqlite3.Connection):
        self._conn = conn
        self._conn.execute(_CREATE_TABLE)
        self._conn.commit()

    def add(self, note: Note) -> None:
        self._conn.execute(
            "INSERT INTO notes (id, title, body, created_at) VALUES (?, ?, ?, ?)",
            (note.id, note.title, note.body, note.created_at.isoformat()),
        )
        self._conn.commit()

    def list_all(self) -> list[Note]:
        rows = self._conn.execute(
            "SELECT id, title, body, created_at FROM notes ORDER BY created_at"
        ).fetchall()
        return [self._to_note(row) for row in rows]

    def get(self, note_id: str) -> Note | None:
        row = self._conn.execute(
            "SELECT id, title, body, created_at FROM notes WHERE id = ?",
            (note_id,),
        ).fetchone()
        return self._to_note(row) if row else None

    def set_body(self, note_id: str, body: str) -> None:
        self._conn.execute("UPDATE notes SET body = ? WHERE id = ?", (body, note_id))
        self._conn.commit()

    @staticmethod
    def _to_note(row: tuple) -> Note:
        id_, title, body, created_at = row
        return Note(id=id_, title=title, body=body, created_at=datetime.fromisoformat(created_at))
