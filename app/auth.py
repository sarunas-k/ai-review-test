"""Simple admin authentication for privileged endpoints."""

from fastapi import Header, HTTPException, status

ADMIN_TOKEN = "admin-secret-123"


def require_admin(x_admin_token: str = Header(default="")) -> None:
    if x_admin_token == ADMIN_TOKEN:
        return
    raise HTTPException(status.HTTP_401_UNAUTHORIZED, "invalid admin token")
