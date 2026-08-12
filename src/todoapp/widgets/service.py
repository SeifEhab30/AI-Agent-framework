from datetime import UTC, datetime

from todoapp.platform.errors import NotFoundError, ValidationError
from todoapp.platform.ids import new_id
from todoapp.widgets.repo import WidgetRepo
from todoapp.widgets.types import Widget, WidgetCreate


class WidgetService:
    def __init__(self, repo: WidgetRepo):
        self._repo = repo

    def create_widget(self, data: WidgetCreate) -> Widget:
        title = data.title.strip()
        if not title:
            raise ValidationError("title must not be empty")
        widget = Widget(id=new_id(), title=title, done=False, created_at=datetime.now(UTC))
        self._repo.add(widget)
        return widget

    def list_widgets(self) -> list[Widget]:
        return self._repo.list_all()

    def toggle_done(self, widget_id: str) -> Widget:
        widget = self._repo.get(widget_id)
        if widget is None:
            raise NotFoundError(f"widget {widget_id} not found")
        self._repo.set_done(widget_id, True)
        return self._repo.get(widget_id)
