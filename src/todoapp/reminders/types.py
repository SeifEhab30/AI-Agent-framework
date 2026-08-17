from datetime import datetime

from pydantic import BaseModel


class Reminder(BaseModel):
    id: str
    message: str
    due_at: datetime
    done: bool
    created_at: datetime


class ReminderCreate(BaseModel):
    message: str
    due_at: datetime
