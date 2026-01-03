from fastapi import Header, HTTPException
from app.core.settings import settings
from app.core.tma_init_data import validate_init_data, InitDataInvalid


async def get_tma_user(authorization: str | None = Header(default=None)) -> dict:
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization")
    if not authorization.startswith("tma "):
        raise HTTPException(status_code=401, detail="Bad Authorization format")

    init_data = authorization[4:]
    try:
        parsed = validate_init_data(init_data, settings.bot_token)
    except InitDataInvalid as e:
        raise HTTPException(status_code=401, detail=str(e))

    user = parsed.get("user")
    if not user or "id" not in user:
        raise HTTPException(status_code=401, detail="Missing user in initData")

    return {"tg_id": int(user["id"]), "user": user}