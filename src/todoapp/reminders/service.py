from datetime import UTC, datetime

from todoapp.platform.errors import NotFoundError, ValidationError
from todoapp.platform.ids import new_id
from todoapp.reminders.repo import ReminderRepo
from todoapp.reminders.types import Reminder, ReminderCreate


class ReminderService:
    def __init__(self, repo: ReminderRepo):
        self._repo = repo

    def create_reminder(self, data: ReminderCreate) -> Reminder:
        message = data.message.strip()
        if not message:
            raise ValidationError("message must not be empty")
        due_at = data.due_at
        if due_at.tzinfo is None:
            # A due_at submitted without a UTC offset parses as naive; comparing
            # that directly against datetime.now(UTC) raises TypeError instead
            # of the intended ValidationError. Treat a naive value as UTC.
            due_at = due_at.replace(tzinfo=UTC)
        if due_at <= datetime.now(UTC):
            raise ValidationError("due_at must be in the future")
        reminder = Reminder(
            id=new_id(),
            message=message,
            due_at=due_at,
            done=False,
            created_at=datetime.now(UTC),
        )
        self._repo.add(reminder)
        return reminder

    def list_reminders(self) -> list[Reminder]:
        return self._repo.list_all()

    def mark_done(self, reminder_id: str) -> Reminder:
        reminder = self._repo.get(reminder_id)
        if reminder is None:
            raise NotFoundError(f"reminder {reminder_id} not found")
        self._repo.set_done(reminder_id, True)
        return self._repo.get(reminder_id)

    def delete_reminder(self, reminder_id: str) -> None:
        reminder = self._repo.get(reminder_id)
        if reminder is None:
            raise NotFoundError(f"reminder {reminder_id} not found")
        self._repo.delete(reminder_id)
