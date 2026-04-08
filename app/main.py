from fastapi import FastAPI

from app.api.download import router as download_router
from app.api.health import router as health_router
from app.api.submit_run import router as submit_run_router
from app.api.run_status import router as run_status_router
from app.core.db import init_db
from app.core.paths import ensure_base_dirs

app = FastAPI(title="FCO Engine API")


@app.on_event("startup")
def startup() -> None:
    ensure_base_dirs()
    init_db()


app.include_router(health_router)
app.include_router(submit_run_router)
app.include_router(run_status_router)
app.include_router(download_router)
