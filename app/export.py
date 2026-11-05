"""Export TODO items to JSON files on disk."""

import json
from pathlib import Path

from app.models import Todo

EXPORT_DIR = Path("/tmp/exports")


def export_todos(todos: list[Todo], filename: str) -> Path:
    EXPORT_DIR.mkdir(parents=True, exist_ok=True)
    path = EXPORT_DIR / filename
    path.write_text(json.dumps([t.model_dump(mode="json") for t in todos]))
    return path
