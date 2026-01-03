import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo, Update
from telegram.ext import Application, CommandHandler, ContextTypes

from app.core.settings import settings
from app.db.repos_users import is_blocked

logger = logging.getLogger("gul")


async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not user:
        return

    if await is_blocked(user.id):
        await update.message.reply_text("Доступ ограничен.")
        return

    kb = [[InlineKeyboardButton("Открыть приложение", web_app=WebAppInfo(url=settings.miniapp_url))]]
    await update.message.reply_text("Открой Mini App для работы:", reply_markup=InlineKeyboardMarkup(kb))


def build_bot() -> Application:
    app = Application.builder().token(settings.bot_token).build()
    app.add_handler(CommandHandler("start", start))
    return app