import asyncio
import logging

from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    CallbackQueryHandler, ChatMemberHandler, filters
)

from config import BOT_TOKEN, WEBHOOK_URL, PORT, INTERVAL_SECONDS
from handlers import (
    panel_cmd, panel_callback, games_callback,
    on_group_message, periodic_job, track_chat,
    admin_text_input
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)


async def private_text(update, context):
    # اگه ادمین داره ورودی پنل می‌ده، همون پردازش می‌کنه
    handled = await admin_text_input(update, context)
    if handled:
        return


async def main_async():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # پنل ادمین
    app.add_handler(CommandHandler("start", panel_cmd, filters.ChatType.PRIVATE))
    app.add_handler(CommandHandler("panel", panel_cmd, filters.ChatType.PRIVATE))
    app.add_handler(CallbackQueryHandler(panel_callback, pattern=r"^panel_"))
    app.add_handler(CallbackQueryHandler(games_callback, pattern=r"^(games_|game_|rps_)"))

    # گروه
    app.add_handler(MessageHandler(filters.TEXT & filters.ChatType.GROUPS, on_group_message))
    app.add_handler(ChatMemberHandler(track_chat, ChatMemberHandler.MY_CHAT_MEMBER))
    app.add_handler(MessageHandler(filters.ALL & filters.ChatType.GROUPS, track_chat))

    # پیوی (فقط برای ورودی‌های پنل)
    app.add_handler(MessageHandler(filters.TEXT & filters.ChatType.PRIVATE & ~filters.COMMAND, private_text))

    # جاب دوره‌ای
    app.job_queue.run_repeating(periodic_job, interval=INTERVAL_SECONDS, first=60)

    await app.initialize()
    await app.bot.set_webhook(f"{WEBHOOK_URL}/{BOT_TOKEN}")
    await app.start()
    await app.updater.start_webhook(
        listen="0.0.0.0", port=PORT,
        url_path=BOT_TOKEN,
        webhook_url=f"{WEBHOOK_URL}/{BOT_TOKEN}",
    )
    logger.info("🔥 حمال با پنل و بازی‌ها آنلاین شد...")
    stop = asyncio.Event()
    await stop.wait()


def main():
    asyncio.run(main_async())


if __name__ == "__main__":
    main()
