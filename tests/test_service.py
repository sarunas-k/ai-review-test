import pytest

from app.models import TodoCreate, TodoUpdate
from app.service import TodoNotFoundError, TodoService
from app.storage import TodoStore


@pytest.fixture
def service() -> TodoService:
    return TodoService(TodoStore())


def test_create_assigns_incrementing_ids_and_strips_title(service):
    first = service.create(TodoCreate(title="  buy milk  "))
    second = service.create(TodoCreate(title="walk dog"))
    assert (first.id, second.id) == (1, 2)
    assert first.title == "buy milk"
    assert first.done is False


def test_get_missing_raises(service):
    with pytest.raises(TodoNotFoundError):
        service.get(42)


def test_list_filters_by_done(service):
    a = service.create(TodoCreate(title="a"))
    service.create(TodoCreate(title="b"))
    service.update(a.id, TodoUpdate(done=True))
    assert [t.title for t in service.list(done=True)] == ["a"]
    assert [t.title for t in service.list(done=False)] == ["b"]
    assert len(service.list()) == 2


def test_partial_update_only_changes_given_fields(service):
    todo = service.create(TodoCreate(title="a", description="keep me"))
    updated = service.update(todo.id, TodoUpdate(done=True))
    assert updated.done is True
    assert updated.description == "keep me"


def test_delete(service):
    todo = service.create(TodoCreate(title="a"))
    service.delete(todo.id)
    with pytest.raises(TodoNotFoundError):
        service.delete(todo.id)
