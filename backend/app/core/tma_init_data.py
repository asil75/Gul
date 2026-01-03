import hmac
import hashlib
import time
import json
from urllib.parse import parse_qsl


class InitDataInvalid(Exception):
    pass


def _secret_key(bot_token: str) -> bytes:
    return hmac.new(b"WebAppData", bot_token.encode(), hashlib.sha256).digest()


def validate_init_data(init_data: str, bot_token: str, max_age_seconds: int = 24 * 60 * 60) -> dict:
    if not init_data:
        raise InitDataInvalid("Empty initData")

    pairs = dict(parse_qsl(init_data, keep_blank_values=True))
    recv_hash = pairs.pop("hash", None)
    if not recv_hash:
        raise InitDataInvalid("Missing hash")

    # Важно: разделитель должен быть "
"
    data_check_string = "
".join(f"{k}={v}" for k, v in sorted(pairs.items()))

    calc_hash = hmac.new(
        _secret_key(bot_token),
        data_check_string.encode(),
        hashlib.sha256
    ).hexdigest()

    if calc_hash != recv_hash:
        raise InitDataInvalid("Bad hash")

    try:
        auth_date = int(pairs.get("auth_date", "0"))
    except ValueError:
        auth_date = 0

    if auth_date and max_age_seconds:
        if time.time() - auth_date > max_age_seconds:
            raise InitDataInvalid("initData expired")

    user_raw = pairs.get("user")
    user = json.loads(user_raw) if user_raw else None

    return {**pairs, "user": user}
