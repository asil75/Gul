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

    if not isinstance(init_data, str):
        raise InitDataInvalid("initData must be a string")

    pairs = dict(parse_qsl(init_data.strip(), keep_blank_values=True))
    
    if not pairs:
        raise InitDataInvalid("No valid parameters found in initData")

    recv_hash = pairs.pop("hash", None)
    if not recv_hash:
        raise InitDataInvalid("Missing hash")

    if not recv_hash.isalnum():
        raise InitDataInvalid("Invalid hash format")

    data_check_string = "\n".join(
        f"{k}={v}" for k, v in sorted(pairs.items())
    )
    
    calc_hash = hmac.new(
        _secret_key(bot_token),
        data_check_string.encode(),
        hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(calc_hash, recv_hash):
        raise InitDataInvalid("Bad hash")

    auth_date_str = pairs.get("auth_date")
    if not auth_date_str:
        raise InitDataInvalid("Missing auth_date")

    try:
        auth_date = int(auth_date_str)
    except ValueError:
        raise InitDataInvalid("Invalid auth_date format")

    if auth_date <= 0:
        raise InitDataInvalid("Invalid auth_date value")

    if max_age_seconds > 0:
        current_time = time.time()
        if current_time - auth_date > max_age_seconds:
            raise InitDataInvalid("initData expired")

    user = None
    user_raw = pairs.get("user")
    if user_raw:
        try:
            user = json.loads(user_raw)
            if not isinstance(user, dict):
                raise InitDataInvalid("User data must be a JSON object")
        except json.JSONDecodeError:
            raise InitDataInvalid("Invalid user JSON")

    return {**pairs, "user": user}
