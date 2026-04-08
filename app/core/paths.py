from pathlib import Path

from app.core.config import settings


def ensure_base_dirs() -> None:
    Path(settings.base_shared_dir).mkdir(parents=True, exist_ok=True)
    Path(settings.runs_dir).mkdir(parents=True, exist_ok=True)
    Path(settings.cache_dir).mkdir(parents=True, exist_ok=True)
    Path(settings.logs_dir).mkdir(parents=True, exist_ok=True)
    Path(settings.db_path).parent.mkdir(parents=True, exist_ok=True)


def get_run_dir(run_id: str) -> Path:
    return Path(settings.runs_dir) / run_id


def get_run_input_dir(run_id: str) -> Path:
    return get_run_dir(run_id) / "input"


def get_run_output_dir(run_id: str) -> Path:
    return get_run_dir(run_id) / "output"


def get_run_logs_dir(run_id: str) -> Path:
    return get_run_dir(run_id) / "logs"


def get_run_state_dir(run_id: str) -> Path:
    return get_run_dir(run_id) / "state"


def ensure_run_dirs(run_id: str) -> None:
    get_run_input_dir(run_id).mkdir(parents=True, exist_ok=True)
    get_run_output_dir(run_id).mkdir(parents=True, exist_ok=True)
    get_run_logs_dir(run_id).mkdir(parents=True, exist_ok=True)
    get_run_state_dir(run_id).mkdir(parents=True, exist_ok=True)
