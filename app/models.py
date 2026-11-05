"""Pydantic models (API schemas) for the TODO app."""

from datetime import datetime, timezone

from pydantic import BaseModel, Field


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class TodoCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str = Field(default="", max_length=2000)


class TodoUpdate(BaseModel):
    """Partial update: only fields that are set are changed."""

    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=2000)
    done: bool | None = None


class Todo(BaseModel):
    id: int
    title: str
    description: str = ""
    done: bool = False
    created_at: datetime = Field(default_factory=_utcnow)
