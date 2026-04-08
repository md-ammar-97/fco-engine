import hmac
import secrets


def generate_callback_token() -> str:
    return secrets.token_urlsafe(24)


def secure_compare(left: str, right: str) -> bool:
    return hmac.compare_digest(left or "", right or "")
