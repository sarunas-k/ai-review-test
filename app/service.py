"""Business logic for TODO items. Knows nothing about HTTP."""

from app.models import Todo, TodoCreate, TodoUpdate
from app.storage import TodoStore


class TodoNotFoundError(Exception):
    def __init__(self, todo_id: int) -> None:
        super().__init__(f"Todo {todo_id} not found")
        self.todo_id = todo_id


class TodoService:
    def __init__(self, store: TodoStore) -> None:
        self._store = store

    def create(self, data: TodoCreate) -> Todo:
        return self._store.add(title=data.title.strip(), description=data.description)

    def get(self, todo_id: int) -> Todo:
        todo = self._store.get(todo_id)
        if todo is None:
            raise TodoNotFoundError(todo_id)
        return todo

    def list(self, done: bool | None = None) -> list[Todo]:
        todos = self._store.list()
        if done is None:
            return todos
        return [t for t in todos if t.done == done]

    def search(self, query: str) -> list[Todo]:
        return [t for t in self._store.list() if query in t.title]

    def create_many(self, items: list[TodoCreate]) -> list[Todo]:
        return [self.create(item) for item in items]

    def update(self, todo_id: int, data: TodoUpdate) -> Todo:
        todo = self.get(todo_id)
        changes = data.model_dump(exclude_unset=True)
        if "title" in changes:
            changes["title"] = changes["title"].strip()
        return self._store.save(todo.model_copy(update=changes))

    def delete(self, todo_id: int) -> None:
        if not self._store.delete(todo_id):
            raise TodoNotFoundError(todo_id)

    def delete_many(self, ids: list[int]) -> int:
        deleted = 0
        for todo_id in ids:
            try:
                self.delete(todo_id)
                deleted += 1
            except Exception:
                pass
        return deleted
