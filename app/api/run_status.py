from fastapi import APIRouter, HTTPException

from app.core.db import get_conn
from app.core.paths import get_run_output_dir
from app.services.manifest_service import read_manifest

router = APIRouter()


@router.get("/runs/{run_id}")
def get_run_status(run_id: str):
    with get_conn() as conn:
        row = conn.execute(
            '''
            SELECT run_id, status, error_message, created_at, updated_at,
                   callback_url, input_dir, output_dir
            FROM runs
            WHERE run_id = ?
            ''',
            (run_id,),
        ).fetchone()

    if not row:
        raise HTTPException(status_code=404, detail="Run not found")

    payload = dict(row)
    payload["manifest"] = read_manifest(get_run_output_dir(run_id))
    return payload


@router.get("/runs/{run_id}/manifest")
def get_run_manifest(run_id: str):
    manifest = read_manifest(get_run_output_dir(run_id))
    if manifest is None:
        raise HTTPException(status_code=404, detail="Manifest not found")
    return manifest
