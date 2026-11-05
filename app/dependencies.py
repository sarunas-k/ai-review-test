"""Shared singletons / FastAPI dependencies."""

from app.service import TodoService
from app.storage import TodoStore

store = TodoStore()
_service = TodoService(store)


def get_service() -> TodoService:
    return _service
