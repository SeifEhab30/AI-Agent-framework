from datetime import UTC, datetime

from todoapp.platform.errors import NotFoundError, ValidationError
from todoapp.platform.ids import new_id
from todoapp.widgets.repo import WidgetRepo
from todoapp.widgets.types import Widget, WidgetCreate


class WidgetService:
    def __init__(self, repo: WidgetRepo):
        self._repo = repo

    def create_widget(self, data: WidgetCreate) -> Widget:
        label = data.label.strip()
        if not label:
            raise ValidationError("label must not be empty")
        widget = Widget(id=new_id(), label=label, value=data.value, created_at=datetime.now(UTC))
        self._repo.add(widget)
        return widget

    def list_widgets(self) -> list[Widget]:
        return self._repo.list_all()

    def search(self, query: str) -> list[Widget]:
        query = query.lower()
        return [widget for widget in self._repo.list_all() if query in widget.label.lower()]

    def set_value(self, widget_id: str, value: int) -> Widget:
        widget = self._repo.get(widget_id)
        if widget is None:
            raise NotFoundError(f"widget {widget_id} not found")
        self._repo.set_value(widget_id, value)
        return self._repo.get(widget_id)

    def delete_widget(self, widget_id: str) -> None:
        widget = self._repo.get(widget_id)
        if widget is None:
            raise NotFoundError(f"widget {widget_id} not found")
        self._repo.delete(widget_id)
