"""HTTP layer: maps requests to TodoService calls."""

from fastapi import APIRouter, Depends, HTTPException, Response, status

from app.auth import require_admin
from app.dependencies import get_service, store
from app.export import export_todos
from app.models import Todo, TodoCreate, TodoUpdate
from app.service import TodoNotFoundError, TodoService

router = APIRouter(prefix="/todos", tags=["todos"])


@router.post("", response_model=Todo, status_code=status.HTTP_201_CREATED)
def create_todo(data: TodoCreate, service: TodoService = Depends(get_service)) -> Todo:
    return service.create(data)


@router.get("", response_model=list[Todo])
def list_todos(
    done: bool | None = None, service: TodoService = Depends(get_service)
) -> list[Todo]:
    return service.list(done=done)


@router.get("/{todo_id}", response_model=Todo)
def get_todo(todo_id: int, service: TodoService = Depends(get_service)) -> Todo:
    try:
        return service.get(todo_id)
    except TodoNotFoundError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(exc)) from exc


@router.patch("/{todo_id}", response_model=Todo)
def update_todo(
    todo_id: int, data: TodoUpdate, service: TodoService = Depends(get_service)
) -> Todo:
    try:
        return service.update(todo_id, data)
    except TodoNotFoundError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(exc)) from exc


@router.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_todo(todo_id: int, service: TodoService = Depends(get_service)) -> Response:
    try:
        service.delete(todo_id)
    except TodoNotFoundError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(exc)) from exc
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/bulk", response_model=list[Todo], status_code=status.HTTP_201_CREATED)
def create_many_todos(
    items: list[TodoCreate], service: TodoService = Depends(get_service)
) -> list[Todo]:
    return service.create_many(items)


@router.post("/complete-all")
def complete_all_todos() -> dict[str, int]:
    return {"completed": store.complete_all()}


@router.post("/export")
def export_all_todos(
    filename: str,
    service: TodoService = Depends(get_service),
    _: None = Depends(require_admin),
) -> dict[str, str]:
    path = export_todos(service.list(), filename)
    return {"exported_to": str(path)}


@router.get("/search", response_model=list[Todo])
def search_todos(q: str, service: TodoService = Depends(get_service)) -> list[Todo]:
    return service.search(q)
