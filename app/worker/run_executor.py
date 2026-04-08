"""Run execution placeholder. Replace with full FCO pipeline modules later."""

import json
from pathlib import Path

from app.core.db import get_conn
from app.core.paths import ensure_run_dirs
from app.worker.queue_service import update_run_status


def execute_run(run_id: str) -> None:
    ensure_run_dirs(run_id)

    with get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM runs WHERE run_id = ?",
            (run_id,),
        ).fetchone()

    if not row:
        raise ValueError(f"Run not found: {run_id}")

    output_dir = Path(row["output_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)

    manifest = {
        "success": False,
        "run_id": run_id,
        "status": "placeholder",
        "message": "FCO executor scaffold created. Replace app.worker.run_executor.execute_run with the full production pipeline.",
        "workbook_path": str(output_dir / "final_workbook.xlsx"),
        "pdf_path": str(output_dir / "final_report.pdf"),
    }

    (output_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2),
        encoding="utf-8",
    )

    update_run_status(run_id, "completed")
