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
    service.create_widget(WidgetCreate(label="Signups today", value=42))
    widgets = service.list_widgets()
    assert len(widgets) == 1
    assert widgets[0].label == "Signups today"
    assert widgets[0].value == 42


def test_create_defaults_value_to_zero(service: WidgetService):
    widget = service.create_widget(WidgetCreate(label="Errors"))
    assert widget.value == 0


def test_create_rejects_blank_label(service: WidgetService):
    with pytest.raises(ValidationError):
        service.create_widget(WidgetCreate(label="   "))


def test_set_value(service: WidgetService):
    widget = service.create_widget(WidgetCreate(label="Signups today", value=42))
    updated = service.set_value(widget.id, 100)
    assert updated.value == 100


def test_set_value_missing_raises(service: WidgetService):
    with pytest.raises(NotFoundError):
        service.set_value("nope", 1)


def test_set_value_to_zero(service: WidgetService):
    widget = service.create_widget(WidgetCreate(label="Signups today", value=42))
    updated = service.set_value(widget.id, 0)
    assert updated.value == 0


def test_search_matches_case_insensitive_substring(service: WidgetService):
    service.create_widget(WidgetCreate(label="Signups today", value=42))
    service.create_widget(WidgetCreate(label="Errors", value=0))
    results = service.search("signups")
    assert len(results) == 1
    assert results[0].label == "Signups today"


def test_search_no_match_returns_empty(service: WidgetService):
    service.create_widget(WidgetCreate(label="Signups today", value=42))
    assert service.search("nope") == []


def test_delete_widget(service: WidgetService):
    widget = service.create_widget(WidgetCreate(label="Signups today", value=42))
    service.delete_widget(widget.id)
    assert service.list_widgets() == []


def test_delete_widget_missing_raises(service: WidgetService):
    with pytest.raises(NotFoundError):
        service.delete_widget("nope")
