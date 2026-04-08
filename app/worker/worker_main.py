import time

from app.core.db import init_db
from app.core.paths import ensure_base_dirs
from app.worker.queue_service import claim_next_queued_run, update_run_status
from app.worker.run_executor import execute_run


def main() -> None:
    ensure_base_dirs()
    init_db()

    while True:
        run_id = claim_next_queued_run()
        if not run_id:
            time.sleep(2)
            continue

        try:
            execute_run(run_id)
        except Exception as exc:
            update_run_status(run_id, "failed", str(exc))


if __name__ == "__main__":
    main()
