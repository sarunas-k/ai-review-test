"""Application entrypoint: `uvicorn app.main:app`."""

from fastapi import FastAPI

from app.routes import router

app = FastAPI(title="Sample TODO API", version="0.1.0")
app.include_router(router)


@app.get("/healthz", tags=["meta"])
def healthz() -> dict[str, str]:
    return {"status": "ok"}
