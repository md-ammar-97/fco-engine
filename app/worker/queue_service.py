from datetime import datetime, timezone
from typing import Optional

from app.core.db import get_conn


def claim_next_queued_run() -> Optional[str]:
    now = datetime.now(timezone.utc).isoformat()

    with get_conn() as conn:
        row = conn.execute(
            "SELECT run_id FROM runs WHERE status = 'queued' ORDER BY created_at ASC LIMIT 1"
        ).fetchone()

        if not row:
            return None

        run_id = row["run_id"]
        conn.execute(
            "UPDATE runs SET status = ?, updated_at = ? WHERE run_id = ?",
            ("running", now, run_id),
        )
        return run_id


def update_run_status(run_id: str, status: str, error_message: str | None = None) -> None:
    now = datetime.now(timezone.utc).isoformat()
    with get_conn() as conn:
        conn.execute(
            "UPDATE runs SET status = ?, error_message = ?, updated_at = ? WHERE run_id = ?",
            (status, error_message, now, run_id),
        )


def get_run_record(run_id: str):
    with get_conn() as conn:
        return conn.execute("SELECT * FROM runs WHERE run_id = ?", (run_id,)).fetchone()
