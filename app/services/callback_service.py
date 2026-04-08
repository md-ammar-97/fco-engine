import time
from typing import Any, Dict

import requests

from app.core.logging import get_logger

logger = get_logger(__name__)


def post_callback(callback_url: str, callback_token: str, payload: Dict[str, Any], retries: int = 3) -> bool:
    headers = {
        "Content-Type": "application/json",
        "X-FCO-Callback-Token": callback_token,
    }

    for attempt in range(1, retries + 1):
        try:
            response = requests.post(callback_url, json=payload, headers=headers, timeout=20)
            if 200 <= response.status_code < 300:
                logger.info("Callback succeeded on attempt %s", attempt)
                return True
            logger.warning("Callback attempt %s failed with status %s", attempt, response.status_code)
        except Exception as exc:
            logger.warning("Callback attempt %s raised %s", attempt, exc)

        if attempt < retries:
            time.sleep(2 * attempt)

    return False
