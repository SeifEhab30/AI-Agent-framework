import re

from todoapp.labels.repo import LabelRepo
from todoapp.labels.types import Label, LabelCreate
from todoapp.platform.errors import NotFoundError, ValidationError
from todoapp.platform.ids import new_id

_COLOR_PATTERN = re.compile(r"^#[0-9A-Fa-f]{3,6}$")


class LabelService:
    def __init__(self, repo: LabelRepo):
        self._repo = repo

    def create_label(self, data: LabelCreate) -> Label:
        name = data.name.strip()
        if not name:
            raise ValidationError("name must not be empty")
        if not _COLOR_PATTERN.match(data.color):
            raise ValidationError("color must be in #RRGGBB hex format")
        label = Label(id=new_id(), name=name, color=data.color)
        self._repo.add(label)
        return label

    def list_labels(self) -> list[Label]:
        return self._repo.list_all()

    def delete_label(self, label_id: str) -> None:
        label = self._repo.get(label_id)
        if label is None:
            raise NotFoundError(f"label {label_id} not found")
        self._repo.delete(label_id)
