from fastapi import FastAPI

from .config import config
from .items import items

app = FastAPI(
    title="preview-api",
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
)


@app.get("/api/healthz")
def healthz():
    return {"status": "ok"}


@app.get("/api/readyz")
def readyz():
    return {"status": "ready"}


@app.get("/api/version")
def version():
    return {"pr": config.pr, "commit": config.commit, "builtAt": config.built_at}


@app.get("/api/items")
def list_items():
    return {"items": items}
