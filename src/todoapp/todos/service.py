from datetime import UTC, datetime

from todoapp.platform.errors import NotFoundError, ValidationError
from todoapp.platform.ids import new_id
from todoapp.todos.repo import TodoRepo
from todoapp.todos.types import Todo, TodoCreate


class TodoService:
    def __init__(self, repo: TodoRepo):
        self._repo = repo

    def create_todo(self, data: TodoCreate) -> Todo:
        title = data.title.strip()
        if not title:
            raise ValidationError("title must not be empty")
        todo = Todo(id=new_id(), title=title, done=False, created_at=datetime.now(UTC))
        self._repo.add(todo)
        return todo

    def list_todos(self) -> list[Todo]:
        return self._repo.list_all()

    def toggle_done(self, todo_id: str) -> Todo:
        todo = self._repo.get(todo_id)
        if todo is None:
            raise NotFoundError(f"todo {todo_id} not found")
        self._repo.set_done(todo_id, True)
        return self._repo.get(todo_id)
