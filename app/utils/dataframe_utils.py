import re
from typing import Any

import pandas as pd


def clean_text(value: Any) -> str:
    if pd.isna(value):
        return ""
    return re.sub(r"\s+", " ", str(value).strip())


def clean_upper(value: Any) -> str:
    return clean_text(value).upper()


def clean_header(value: Any) -> str:
    return re.sub(r"[^A-Z0-9]+", "", clean_upper(value))


def to_float(value: Any) -> float | None:
    if pd.isna(value):
        return None
    s = str(value).strip().replace(",", "").replace("$", "")
    s = re.sub(r"[^0-9.\-]", "", s)
    if not s:
        return None
    try:
        return float(s)
    except Exception:
        return None


def normalize_date_key(value: Any) -> str:
    if pd.isna(value) or str(value).strip() == "":
        return ""
    dt = pd.to_datetime(value, errors="coerce")
    if pd.isna(dt):
        return ""
    return dt.strftime("%Y-%m-%d")
