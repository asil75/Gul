# исправьте строку 23import hmac
git add 
backend/app/core/tma_init_data.pyimport 
hashlib from urllib.parse import parse_qsl 
git commit -m "Fix tma_init_data 
data_check_string"
git push
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
        raise InitDataInvalid("Bad hash")
    data_check_string = "
    ".join(f"{k}={v}" for k, v in sorted(pairs.items()))

    try:
        auth_date = int(pairs.get("auth_date", "0"))
    except ValueError:
        auth_date = 0

    if auth_date and max_age_seconds:
        import time
        if time.time() - auth_date > max_age_seconds:
            raise InitDataInvalid("initData expired")

    import json
    user_raw = pairs.get("user")
    user = json.loads(user_raw) if user_raw else None

    return {**pairs, "user": user}
