import sqlite3
from datetime import datetime

from todoapp.bookmarks.types import Bookmark

_CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS bookmarks (
    id TEXT PRIMARY KEY,
    url TEXT NOT NULL,
    title TEXT NOT NULL,
    created_at TEXT NOT NULL
)
"""


class BookmarkRepo:
    def __init__(self, conn: sqlite3.Connection):
        self._conn = conn
        self._conn.execute(_CREATE_TABLE)
        self._conn.commit()

    def add(self, bookmark: Bookmark) -> None:
        self._conn.execute(
            "INSERT INTO bookmarks (id, url, title, created_at) VALUES (?, ?, ?, ?)",
            (bookmark.id, bookmark.url, bookmark.title, bookmark.created_at.isoformat()),
        )
        self._conn.commit()

    def list_all(self) -> list[Bookmark]:
        rows = self._conn.execute(
            "SELECT id, url, title, created_at FROM bookmarks ORDER BY created_at"
        ).fetchall()
        return [self._to_bookmark(row) for row in rows]

    def get(self, bookmark_id: str) -> Bookmark | None:
        row = self._conn.execute(
            "SELECT id, url, title, created_at FROM bookmarks WHERE id = ?",
            (bookmark_id,),
        ).fetchone()
        return self._to_bookmark(row) if row else None

    def set_title(self, bookmark_id: str, title: str) -> None:
        self._conn.execute("UPDATE bookmarks SET title = ? WHERE id = ?", (title, bookmark_id))
        self._conn.commit()

    @staticmethod
    def _to_bookmark(row: tuple) -> Bookmark:
        id_, url, title, created_at = row
        return Bookmark(id=id_, url=url, title=title, created_at=datetime.fromisoformat(created_at))
