from datetime import datetime, timezone
import json
from pathlib import Path

from fastapi import APIRouter, HTTPException

from app.core.db import get_conn
from app.core.paths import ensure_run_dirs
from app.schemas.submit_models import SubmitRunRequest

router = APIRouter()


@router.post("/run-fco", status_code=202)
def submit_run(payload: SubmitRunRequest):
    input_dir = Path(payload.input_dir)
    output_dir = Path(payload.output_dir)

    if not input_dir.exists():
        raise HTTPException(status_code=400, detail=f"Input directory does not exist: {input_dir}")

    output_dir.mkdir(parents=True, exist_ok=True)
    ensure_run_dirs(payload.run_id)

    now = datetime.now(timezone.utc).isoformat()

    with get_conn() as conn:
        conn.execute(
            '''
            INSERT OR REPLACE INTO runs (
                run_id, status, callback_url, callback_token,
                input_dir, output_dir, config_json, mappings_json,
                error_message, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''',
            (
                payload.run_id,
                "queued",
                payload.callback_url,
                payload.callback_token,
                payload.input_dir,
                payload.output_dir,
                json.dumps(payload.config),
                json.dumps(payload.mappings),
                None,
                now,
                now,
            ),
        )

    return {
        "run_id": payload.run_id,
        "status": "accepted",
        "message": "Run queued successfully",
    }
