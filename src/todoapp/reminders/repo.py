import sqlite3
from datetime import datetime

from todoapp.reminders.types import Reminder

_CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS reminders (
    id TEXT PRIMARY KEY,
    message TEXT NOT NULL,
    due_at TEXT NOT NULL,
    done INTEGER NOT NULL,
    created_at TEXT NOT NULL
)
"""


class ReminderRepo:
    def __init__(self, conn: sqlite3.Connection):
        self._conn = conn
        self._conn.execute(_CREATE_TABLE)
        self._conn.commit()

    def add(self, reminder: Reminder) -> None:
        self._conn.execute(
            "INSERT INTO reminders (id, message, due_at, done, created_at) VALUES (?, ?, ?, ?, ?)",
            (
                reminder.id,
                reminder.message,
                reminder.due_at.isoformat(),
                int(reminder.done),
                reminder.created_at.isoformat(),
            ),
        )
        self._conn.commit()

    def list_all(self) -> list[Reminder]:
        rows = self._conn.execute(
            "SELECT id, message, due_at, done, created_at FROM reminders ORDER BY created_at"
        ).fetchall()
        return [self._to_reminder(row) for row in rows]

    def get(self, reminder_id: str) -> Reminder | None:
        row = self._conn.execute(
            "SELECT id, message, due_at, done, created_at FROM reminders WHERE id = ?",
            (reminder_id,),
        ).fetchone()
        return self._to_reminder(row) if row else None

    def set_done(self, reminder_id: str, done: bool) -> None:
        self._conn.execute("UPDATE reminders SET done = ? WHERE id = ?", (int(done), reminder_id))
        self._conn.commit()

    def delete(self, reminder_id: str) -> None:
        self._conn.execute("DELETE FROM reminders WHERE id = ?", (reminder_id,))
        self._conn.commit()

    @staticmethod
    def _to_reminder(row: tuple) -> Reminder:
        id_, message, due_at, done, created_at = row
        return Reminder(
            id=id_,
            message=message,
            due_at=datetime.fromisoformat(due_at),
            done=bool(done),
            created_at=datetime.fromisoformat(created_at),
        )
