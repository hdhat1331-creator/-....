import asyncio
import logging

from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    CallbackQueryHandler, ChatMemberHandler, filters
)

from config import (
    BOT_TOKEN, WEBHOOK_URL, PORT,
    GROUP_INTERVAL_SECONDS, CLEANUP_INTERVAL_SECONDS
)
from handlers import (
    start_cmd, panel_callback, private_text, cleanup_cmd,
    track_chat, on_group_message, group_interval_job,
)
from cleanup import cleanup_job

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)


async def main_async():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # ---- پیوی ----
    app.add_handler(CommandHandler("start", start_cmd, filters.ChatType.PRIVATE))
    app.add_handler(CommandHandler("panel", start_cmd, filters.ChatType.PRIVATE))
    app.add_handler(CommandHandler("cleanup", cleanup_cmd, filters.ChatType.PRIVATE))
    app.add_handler(CallbackQueryHandler(panel_callback))
    app.add_handler(MessageHandler(
        filters.TEXT & filters.ChatType.PRIVATE & ~filters.COMMAND,
        private_text
    ))

    # ---- گروه ----
    app.add_handler(ChatMemberHandler(track_chat, ChatMemberHandler.MY_CHAT_MEMBER))
    app.add_handler(MessageHandler(
        filters.TEXT & filters.ChatType.GROUPS,
        on_group_message
    ))

    # ---- جاب‌ها ----
    app.job_queue.run_repeating(
        group_interval_job,
        interval=GROUP_INTERVAL_SECONDS,
        first=60
    )
    app.job_queue.run_repeating(
        cleanup_job,
        interval=CLEANUP_INTERVAL_SECONDS,
        first=30
    )

    # ---- وب‌هوک ----
    await app.initialize()
    await app.bot.set_webhook(f"{WEBHOOK_URL}/{BOT_TOKEN}")
    await app.start()
    await app.updater.start_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=BOT_TOKEN,
        webhook_url=f"{WEBHOOK_URL}/{BOT_TOKEN}",
    )
    logger.info("🔥 حمال با MongoDB آنلاین شد...")
    stop = asyncio.Event()
    await stop.wait()


def main():
    asyncio.run(main_async())


if __name__ == "__main__":
    main()
