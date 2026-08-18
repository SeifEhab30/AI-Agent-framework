import sqlite3
from datetime import datetime

from todoapp.widgets.types import Widget

_CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS widgets (
    id TEXT PRIMARY KEY,
    label TEXT NOT NULL,
    value INTEGER NOT NULL,
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
            "INSERT INTO widgets (id, label, value, created_at) VALUES (?, ?, ?, ?)",
            (widget.id, widget.label, widget.value, widget.created_at.isoformat()),
        )
        self._conn.commit()

    def list_all(self) -> list[Widget]:
        rows = self._conn.execute(
            "SELECT id, label, value, created_at FROM widgets ORDER BY created_at"
        ).fetchall()
        return [self._to_widget(row) for row in rows]

    def get(self, widget_id: str) -> Widget | None:
        row = self._conn.execute(
            "SELECT id, label, value, created_at FROM widgets WHERE id = ?",
            (widget_id,),
        ).fetchone()
        return self._to_widget(row) if row else None

    def set_value(self, widget_id: str, value: int) -> None:
        self._conn.execute("UPDATE widgets SET value = ? WHERE id = ?", (value, widget_id))
        self._conn.commit()

    def delete(self, widget_id: str) -> None:
        self._conn.execute("DELETE FROM widgets WHERE id = ?", (widget_id,))
        self._conn.commit()

    @staticmethod
    def _to_widget(row: tuple) -> Widget:
        id_, label, value, created_at = row
        return Widget(
            id=id_, label=label, value=value, created_at=datetime.fromisoformat(created_at)
        )
