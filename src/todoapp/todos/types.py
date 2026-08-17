from datetime import datetime

from pydantic import BaseModel


class Todo(BaseModel):
    id: str
    title: str
    done: bool
    created_at: datetime


class TodoCreate(BaseModel):
    title: str


class TodoUpdate(BaseModel):
    done: bool
