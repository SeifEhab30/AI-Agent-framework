import sqlite3

from todoapp.labels.types import Label

_CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS labels (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    color TEXT NOT NULL
)
"""


class LabelRepo:
    def __init__(self, conn: sqlite3.Connection):
        self._conn = conn
        self._conn.execute(_CREATE_TABLE)
        self._conn.commit()

    def add(self, label: Label) -> None:
        self._conn.execute(
            "INSERT INTO labels (id, name, color) VALUES (?, ?, ?)",
            (label.id, label.name, label.color),
        )
        self._conn.commit()

    def list_all(self) -> list[Label]:
        rows = self._conn.execute("SELECT id, name, color FROM labels ORDER BY id").fetchall()
        return [self._to_label(row) for row in rows]

    def get(self, label_id: str) -> Label | None:
        row = self._conn.execute(
            "SELECT id, name, color FROM labels WHERE id = ?",
            (label_id,),
        ).fetchone()
        return self._to_label(row) if row else None

    def delete(self, label_id: str) -> None:
        self._conn.execute("DELETE FROM labels WHERE id = ?", (label_id,))
        self._conn.commit()

    @staticmethod
    def _to_label(row: tuple) -> Label:
        id_, name, color = row
        return Label(id=id_, name=name, color=color)
