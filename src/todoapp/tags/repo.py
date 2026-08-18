import sqlite3
from datetime import datetime

from todoapp.tags.types import Tag

_CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS tags (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    created_at TEXT NOT NULL
)
"""


class TagRepo:
    def __init__(self, conn: sqlite3.Connection):
        self._conn = conn
        self._conn.execute(_CREATE_TABLE)
        self._conn.commit()

    def add(self, tag: Tag) -> None:
        self._conn.execute(
            "INSERT INTO tags (id, name, created_at) VALUES (?, ?, ?)",
            (tag.id, tag.name, tag.created_at.isoformat()),
        )
        self._conn.commit()

    def list_by_created(self) -> list[Tag]:
        rows = self._conn.execute(
            "SELECT id, name, created_at FROM tags ORDER BY created_at DESC"
        ).fetchall()
        return [self._to_tag(row) for row in rows]

    @staticmethod
    def _to_tag(row: tuple) -> Tag:
        id_, name, created_at = row
        return Tag(id=id_, name=name, created_at=datetime.fromisoformat(created_at))
