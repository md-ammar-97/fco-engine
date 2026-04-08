import sqlite3
from contextlib import contextmanager

from app.core.config import settings
from app.core.paths import ensure_base_dirs


def init_db() -> None:
    ensure_base_dirs()
    with sqlite3.connect(settings.db_path) as conn:
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA synchronous=NORMAL;")
        conn.execute("PRAGMA busy_timeout=5000;")

        conn.execute(
            '''
            CREATE TABLE IF NOT EXISTS runs (
                run_id TEXT PRIMARY KEY,
                status TEXT NOT NULL,
                callback_url TEXT,
                callback_token TEXT,
                input_dir TEXT,
                output_dir TEXT,
                config_json TEXT,
                mappings_json TEXT,
                error_message TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            '''
        )
        conn.commit()


@contextmanager
def get_conn():
    ensure_base_dirs()
    conn = sqlite3.connect(settings.db_path, timeout=5)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous=NORMAL;")
    conn.execute("PRAGMA busy_timeout=5000;")
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()
