from datetime import datetime

from pydantic import BaseModel


class Widget(BaseModel):
    id: str
    title: str
    done: bool
    created_at: datetime


class WidgetCreate(BaseModel):
    title: str


class WidgetUpdate(BaseModel):
    done: bool
