import json
from typing import Any, Dict


def parse_mapping_json(raw: Any, label: str) -> Dict[str, str]:
    if isinstance(raw, dict):
        return {str(k): str(v) for k, v in raw.items()}
    if raw is None:
        raise ValueError(f"{label} mapping is missing")
    try:
        parsed = json.loads(raw)
    except Exception as exc:
        raise ValueError(f"{label} mapping is not valid JSON: {exc}") from exc
    if not isinstance(parsed, dict):
        raise ValueError(f"{label} mapping must be a JSON object")
    return {str(k): str(v) for k, v in parsed.items()}
