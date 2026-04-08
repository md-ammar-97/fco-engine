import json
from pathlib import Path

from fastapi import APIRouter, HTTPException

from app.core.db import get_conn
from app.core.paths import get_run_output_dir

router = APIRouter()


@router.get("/runs/{run_id}")
def get_run_status(run_id: str):
    with get_conn() as conn:
        row = conn.execute(
            "SELECT run_id, status, error_message, created_at, updated_at FROM runs WHERE run_id = ?",
            (run_id,),
        ).fetchone()

    if not row:
        raise HTTPException(status_code=404, detail="Run not found")

    payload = dict(row)

    manifest_path = get_run_output_dir(run_id) / "manifest.json"
    if manifest_path.exists():
        try:
            payload["manifest"] = json.loads(manifest_path.read_text(encoding="utf-8"))
        except Exception:
            payload["manifest"] = None

    return payload
