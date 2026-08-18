from datetime import UTC, datetime

from todoapp.platform.errors import ValidationError
from todoapp.platform.ids import new_id
from todoapp.tags.repo import TagRepo
from todoapp.tags.types import Tag, TagCreate


class TagService:
    def __init__(self, repo: TagRepo):
        self._repo = repo

    def create_tag(self, data: TagCreate) -> Tag:
        name = data.name.strip()
        if not name:
            raise ValidationError("name must not be empty")
        tag = Tag(id=new_id(), name=name, created_at=datetime.now(UTC))
        self._repo.add(tag)
        return tag

    def list_tags_alphabetical(self) -> list[Tag]:
        return self._repo.list_by_name()

    def list_tags_recent(self) -> list[Tag]:
        return self._repo.list_by_created()
