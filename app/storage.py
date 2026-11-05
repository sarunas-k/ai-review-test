"""In-memory storage for TODO items.

Deliberately simple: data is lost on restart and the store is not safe for
multiple worker processes. Swap this module out to add real persistence.
"""

from threading import Lock

from app.models import Todo


class TodoStore:
    def __init__(self) -> None:
        self._items: dict[int, Todo] = {}
        self._next_id = 1
        self._lock = Lock()

    def add(self, title: str, description: str = "") -> Todo:
        with self._lock:
            todo = Todo(id=self._next_id, title=title, description=description)
            self._items[todo.id] = todo
            self._next_id += 1
            return todo

    def get(self, todo_id: int) -> Todo | None:
        return self._items.get(todo_id)

    def list(self) -> list[Todo]:
        return sorted(self._items.values(), key=lambda t: t.id)

    def save(self, todo: Todo) -> Todo:
        with self._lock:
            self._items[todo.id] = todo
            return todo

    def delete(self, todo_id: int) -> bool:
        with self._lock:
            return self._items.pop(todo_id, None) is not None

    def complete_all(self) -> int:
        count = 0
        for todo in self._items.values():
            if not todo.done:
                todo.done = True
                count += 1
        return count

    def clear(self) -> None:
        with self._lock:
            self._items.clear()
            self._next_id = 1
