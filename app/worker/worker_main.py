import time

from app.core.db import init_db
from app.core.paths import ensure_base_dirs
from app.core.logging import get_logger
from app.worker.queue_service import claim_next_queued_run, update_run_status
from app.worker.run_executor import execute_run

logger = get_logger(__name__)


def main() -> None:
    ensure_base_dirs()
    init_db()
    logger.info("FCO worker started")

    while True:
        run_id = claim_next_queued_run()
        if not run_id:
            time.sleep(2)
            continue

        logger.info("Claimed run %s", run_id)
        try:
            execute_run(run_id)
        except Exception as exc:
            logger.exception("Run %s failed", run_id)
            update_run_status(run_id, "failed", str(exc))


if __name__ == "__main__":
    main()
