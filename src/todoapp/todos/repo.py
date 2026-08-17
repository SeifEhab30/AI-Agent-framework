import sqlite3
from datetime import datetime

from todoapp.todos.types import Todo

_CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS todos (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    done INTEGER NOT NULL,
    created_at TEXT NOT NULL
)
"""


class TodoRepo:
    def __init__(self, conn: sqlite3.Connection):
        self._conn = conn
        self._conn.execute(_CREATE_TABLE)
        self._conn.commit()

    def add(self, todo: Todo) -> None:
        self._conn.execute(
            "INSERT INTO todos (id, title, done, created_at) VALUES (?, ?, ?, ?)",
            (todo.id, todo.title, int(todo.done), todo.created_at.isoformat()),
        )
        self._conn.commit()

    def list_all(self) -> list[Todo]:
        rows = self._conn.execute(
            "SELECT id, title, done, created_at FROM todos ORDER BY created_at"
        ).fetchall()
        return [self._to_todo(row) for row in rows]

    def get(self, todo_id: str) -> Todo | None:
        row = self._conn.execute(
            "SELECT id, title, done, created_at FROM todos WHERE id = ?",
            (todo_id,),
        ).fetchone()
        return self._to_todo(row) if row else None

    def set_done(self, todo_id: str, done: bool) -> None:
        self._conn.execute("UPDATE todos SET done = ? WHERE id = ?", (int(done), todo_id))
        self._conn.commit()

    @staticmethod
    def _to_todo(row: tuple) -> Todo:
        id_, title, done, created_at = row
        return Todo(
            id=id_, title=title, done=bool(done), created_at=datetime.fromisoformat(created_at)
        )
