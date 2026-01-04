import logging

from fastapi import FastAPI, Request, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.core.settings import settings
from app.db.db import init_pool, close_pool
from app.db.migrate import migrate
from app.api.routes import router as api_router
from app.bot.bot_app import build_bot

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("gul")

app = FastAPI(title="Gul MiniApp Backend")

# CORS для фронта на GitHub Pages
# Важно: origin — это только схема+домен, без /Gul
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://asil75.github.io",
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем API роуты (/api/...)
app.include_router(api_router)

bot_app = None


@app.get("/")
async def root():
    return {"ok": True, "service": "gul-backend"}


@app.get("/ping")
async def ping():
    return {"ok": True}


@app.get("/health")
async def health():
    return {"ok": True}


@app.on_event("startup")
async def on_startup():
    global bot_app
    await init_pool(settings.database_url)
    await migrate()

    bot_app = build_bot()
    await bot_app.initialize()
    await bot_app.start()
    logger.info("Backend started")


@app.on_event("shutdown")
async def on_shutdown():
    global bot_app
    if bot_app:
        await bot_app.stop()
        await bot_app.shutdown()
    await close_pool()


@app.post("/tg/webhook")
async def telegram_webhook(
    request: Request,
    x_telegram_bot_api_secret_token: str | None = Header(default=None),
):
    if x_telegram_bot_api_secret_token != settings.webhook_secret:
        raise HTTPException(status_code=403, detail="Bad secret token")

    payload = await request.json()
    from telegram import Update

    update = Update.de_json(payload, bot_app.bot)
    await bot_app.process_update(update)
    return {"ok": True}
