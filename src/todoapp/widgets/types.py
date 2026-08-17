from datetime import datetime

from pydantic import BaseModel


class Widget(BaseModel):
    id: str
    label: str
    value: int
    created_at: datetime


class WidgetCreate(BaseModel):
    label: str
    value: int = 0


class WidgetUpdate(BaseModel):
    value: int
