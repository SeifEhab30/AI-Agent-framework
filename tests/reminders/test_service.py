import sqlite3
from datetime import UTC, datetime, timedelta

import pytest

from todoapp.platform.errors import NotFoundError, ValidationError
from todoapp.reminders.repo import ReminderRepo
from todoapp.reminders.service import ReminderService
from todoapp.reminders.types import ReminderCreate


@pytest.fixture
def service() -> ReminderService:
    conn = sqlite3.connect(":memory:")
    return ReminderService(ReminderRepo(conn))


def future() -> datetime:
    return datetime.now(UTC) + timedelta(days=1)


def test_create_and_list(service: ReminderService):
    service.create_reminder(ReminderCreate(message="call mom", due_at=future()))
    reminders = service.list_reminders()
    assert len(reminders) == 1
    assert reminders[0].message == "call mom"
    assert reminders[0].done is False


def test_create_rejects_blank_message(service: ReminderService):
    with pytest.raises(ValidationError):
        service.create_reminder(ReminderCreate(message="   ", due_at=future()))


def test_create_rejects_past_due_at(service: ReminderService):
    past = datetime.now(UTC) - timedelta(days=1)
    with pytest.raises(ValidationError):
        service.create_reminder(ReminderCreate(message="call mom", due_at=past))


def test_create_rejects_present_due_at(service: ReminderService):
    now = datetime.now(UTC)
    with pytest.raises(ValidationError):
        service.create_reminder(ReminderCreate(message="call mom", due_at=now))


def test_create_accepts_naive_future_due_at(service: ReminderService):
    # A due_at with no UTC offset parses as timezone-naive; this must not
    # raise TypeError when compared against the (aware) current time.
    naive_future = (datetime.now(UTC) + timedelta(days=1)).replace(tzinfo=None)
    reminder = service.create_reminder(ReminderCreate(message="call mom", due_at=naive_future))
    assert reminder.due_at.tzinfo is not None


def test_create_rejects_naive_past_due_at(service: ReminderService):
    naive_past = (datetime.now(UTC) - timedelta(days=1)).replace(tzinfo=None)
    with pytest.raises(ValidationError):
        service.create_reminder(ReminderCreate(message="call mom", due_at=naive_past))


def test_mark_done(service: ReminderService):
    reminder = service.create_reminder(ReminderCreate(message="call mom", due_at=future()))
    marked = service.mark_done(reminder.id)
    assert marked.done is True


def test_mark_done_missing_raises(service: ReminderService):
    with pytest.raises(NotFoundError):
        service.mark_done("nope")


def test_delete_removes_reminder(service: ReminderService):
    reminder = service.create_reminder(ReminderCreate(message="call mom", due_at=future()))
    service.delete_reminder(reminder.id)
    assert service.list_reminders() == []


def test_delete_missing_raises(service: ReminderService):
    with pytest.raises(NotFoundError):
        service.delete_reminder("nope")
