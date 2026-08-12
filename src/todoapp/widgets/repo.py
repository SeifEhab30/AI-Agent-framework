import sqlite3
from datetime import datetime

from todoapp.widgets.types import Widget

_CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS widgets (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    done INTEGER NOT NULL,
    created_at TEXT NOT NULL
)
"""


class WidgetRepo:
    def __init__(self, conn: sqlite3.Connection):
        self._conn = conn
        self._conn.execute(_CREATE_TABLE)
        self._conn.commit()

    def add(self, widget: Widget) -> None:
        self._conn.execute(
            "INSERT INTO widgets (id, title, done, created_at) VALUES (?, ?, ?, ?)",
            (widget.id, widget.title, int(widget.done), widget.created_at.isoformat()),
        )
        self._conn.commit()

    def list_all(self) -> list[Widget]:
        rows = self._conn.execute(
            "SELECT id, title, done, created_at FROM widgets ORDER BY created_at"
        ).fetchall()
        return [self._to_widget(row) for row in rows]

    def get(self, widget_id: str) -> Widget | None:
        row = self._conn.execute(
            "SELECT id, title, done, created_at FROM widgets WHERE id = ?",
            (widget_id,),
        ).fetchone()
        return self._to_widget(row) if row else None

    def set_done(self, widget_id: str, done: bool) -> None:
        self._conn.execute("UPDATE widgets SET done = ? WHERE id = ?", (int(done), widget_id))
        self._conn.commit()

    @staticmethod
    def _to_widget(row: tuple) -> Widget:
        id_, title, done, created_at = row
        return Widget(
            id=id_, title=title, done=bool(done), created_at=datetime.fromisoformat(created_at)
        )
