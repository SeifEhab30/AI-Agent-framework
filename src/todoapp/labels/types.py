from pydantic import BaseModel


class Label(BaseModel):
    id: str
    name: str
    color: str


class LabelCreate(BaseModel):
    name: str
    color: str
