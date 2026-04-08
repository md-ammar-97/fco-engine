import os
from dataclasses import dataclass


@dataclass
class Settings:
    app_env: str = os.getenv("APP_ENV", "local")
    app_host: str = os.getenv("APP_HOST", "0.0.0.0")
    app_port: int = int(os.getenv("APP_PORT", "8000"))

    base_shared_dir: str = os.getenv("BASE_SHARED_DIR", "/shared/fco")
    runs_dir: str = os.getenv("RUNS_DIR", "/shared/fco/runs")
    cache_dir: str = os.getenv("CACHE_DIR", "/shared/fco/cache")
    logs_dir: str = os.getenv("LOGS_DIR", "/shared/fco/logs")
    db_path: str = os.getenv("DB_PATH", "/shared/fco/queue/jobs.db")

    ors_api_key: str = os.getenv("ORS_API_KEY", "")
    google_service_account_json: str = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON", "")
    callback_shared_secret: str = os.getenv("CALLBACK_SHARED_SECRET", "")

    retention_input_days: int = int(os.getenv("RETENTION_INPUT_DAYS", "7"))
    retention_output_days: int = int(os.getenv("RETENTION_OUTPUT_DAYS", "30"))
    retention_debug_days: int = int(os.getenv("RETENTION_DEBUG_DAYS", "3"))

    max_concurrent_runs: int = int(os.getenv("MAX_CONCURRENT_RUNS", "1"))


settings = Settings()
