import sqlite3

import pytest

from todoapp.platform.errors import NotFoundError, ValidationError
from todoapp.widgets.repo import WidgetRepo
from todoapp.widgets.service import WidgetService
from todoapp.widgets.types import WidgetCreate


@pytest.fixture
def service() -> WidgetService:
    conn = sqlite3.connect(":memory:")
    return WidgetService(WidgetRepo(conn))


def test_create_and_list(service: WidgetService):
    service.create_widget(WidgetCreate(title="buy milk"))
    widgets = service.list_widgets()
    assert len(widgets) == 1
    assert widgets[0].title == "buy milk"
    assert widgets[0].done is False


def test_create_rejects_blank_title(service: WidgetService):
    with pytest.raises(ValidationError):
        service.create_widget(WidgetCreate(title="   "))


def test_toggle_done(service: WidgetService):
    widget = service.create_widget(WidgetCreate(title="buy milk"))
    toggled = service.toggle_done(widget.id)
    assert toggled.done is True


def test_toggle_missing_raises(service: WidgetService):
    with pytest.raises(NotFoundError):
        service.toggle_done("nope")


def test_toggle_done_flips_back_off(service: WidgetService):
    widget = service.create_widget(WidgetCreate(title="buy milk"))
    service.toggle_done(widget.id)
    toggled_again = service.toggle_done(widget.id)
    assert toggled_again.done is False
