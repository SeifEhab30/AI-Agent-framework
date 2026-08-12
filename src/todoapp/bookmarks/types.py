from datetime import datetime

from pydantic import BaseModel


class Bookmark(BaseModel):
    id: str
    url: str
    title: str
    created_at: datetime


class BookmarkCreate(BaseModel):
    url: str
    title: str


class BookmarkUpdate(BaseModel):
    title: str
