import sqlite3

import pytest

from todoapp.platform.errors import NotFoundError, ValidationError
from todoapp.todos.repo import TodoRepo
from todoapp.todos.service import TodoService
from todoapp.todos.types import TodoCreate


@pytest.fixture
def service() -> TodoService:
    conn = sqlite3.connect(":memory:")
    return TodoService(TodoRepo(conn))


def test_create_and_list(service: TodoService):
    service.create_todo(TodoCreate(title="buy milk"))
    todos = service.list_todos()
    assert len(todos) == 1
    assert todos[0].title == "buy milk"
    assert todos[0].done is False


def test_create_rejects_blank_title(service: TodoService):
    with pytest.raises(ValidationError):
        service.create_todo(TodoCreate(title="   "))


def test_toggle_done(service: TodoService):
    todo = service.create_todo(TodoCreate(title="buy milk"))
    toggled = service.toggle_done(todo.id)
    assert toggled.done is True


def test_toggle_done_flips_back_off(service: TodoService):
    todo = service.create_todo(TodoCreate(title="buy milk"))
    service.toggle_done(todo.id)
    toggled_again = service.toggle_done(todo.id)
    assert toggled_again.done is False


def test_toggle_missing_raises(service: TodoService):
    with pytest.raises(NotFoundError):
        service.toggle_done("nope")


def test_delete_todo(service: TodoService):
    todo = service.create_todo(TodoCreate(title="buy milk"))
    service.delete_todo(todo.id)
    assert service.list_todos() == []


def test_delete_missing_raises(service: TodoService):
    with pytest.raises(NotFoundError):
        service.delete_todo("nope")
