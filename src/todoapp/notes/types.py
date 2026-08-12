from datetime import datetime

from pydantic import BaseModel


class Note(BaseModel):
    id: str
    title: str
    body: str
    created_at: datetime


class NoteCreate(BaseModel):
    title: str
    body: str = ""


class NoteUpdate(BaseModel):
    body: str
