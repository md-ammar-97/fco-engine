import json
from pathlib import Path
from datetime import datetime, timezone

from app.core.logging import get_logger
from app.worker.queue_service import get_run_record, update_run_status
from app.services.manifest_service import write_manifest
from app.services.callback_service import post_callback

logger = get_logger(__name__)


def execute_run(run_id: str) -> None:
    row = get_run_record(run_id)
    if not row:
        raise ValueError(f"Run not found: {run_id}")

    input_dir = Path(row["input_dir"])
    output_dir = Path(row["output_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)

    workbook_path = output_dir / "final_workbook.xlsx"
    pdf_path = output_dir / "final_report.pdf"

    # Placeholder artifacts for Step 3
    workbook_path.write_bytes(b"")
    pdf_path.write_bytes(b"")

    manifest = {
        "success": True,
        "run_id": run_id,
        "status": "completed",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "message": "Step 3 scaffold run completed. Replace placeholder logic with full FCO pipeline in Step 4.",
        "workbook_path": str(workbook_path),
        "pdf_path": str(pdf_path),
        "google_sheet_url": None,
        "summary": {
            "eligible_trips": 0,
            "eligible_miles": 0,
            "old_cpg": None,
            "avg_new_cpg": None,
            "savings_abs": None,
            "savings_pct": None,
        },
        "exceptions": {
            "unmapped_cities": 0,
            "unmatched_fuel_rows": 0,
        },
        "error": None,
    }

    write_manifest(output_dir, manifest)

    update_run_status(run_id, "callback_pending")

    callback_ok = post_callback(
        callback_url=row["callback_url"],
        callback_token=row["callback_token"],
        payload=manifest,
    )

    if callback_ok:
        update_run_status(run_id, "completed")
    else:
        logger.warning("Callback failed for run %s; leaving status as callback_pending", run_id)
