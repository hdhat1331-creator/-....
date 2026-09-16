import json
import random
import logging
import asyncio
from pathlib import Path
from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread

from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    ContextTypes, filters, ChatMemberHandler
)
from config import BOT_TOKEN, ADMIN_ID, WEBHOOK_URL, PORT, INTERVAL_SECONDS

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

DB_PATH = Path("database.json")

# ---------- دیتابیس ----------
def load_db():
    if not DB_PATH.exists():
        return {"replies": {}, "interval_messages": [], "targets": [], "seen_groups": []}
    return json.loads(DB_PATH.read_text(encoding="utf-8"))

def save_db(db):
    DB_PATH.write_text(json.dumps(db, ensure_ascii=False, indent=2), encoding="utf-8")

# ---------- سرور HTTP برای health check ----------
class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Hammal is alive :)")

    def log_message(self, *args):
        pass

def run_health_server():
    server = HTTPServer(("0.0.0.0", PORT), HealthHandler)
    server.serve_forever()

# ---------- دستورات ادمین (پیوی) ----------
async def add_reply(update, context):
    if update.effective_user.id != ADMIN_ID: return
    text = update.message.text.replace("/add ", "", 1)
    if "|" not in text:
        await update.message.reply_text("فرمت: /add کلید | جواب")
        return
    key, reply = [p.strip() for p in text.split("|", 1)]
    db = load_db()
    db["replies"].setdefault(key, []).append(reply)
    save_db(db)
    await update.message.reply_text(f"✅ اضافه شد:\n«{key}» → {reply}")

async def del_reply(update, context):
    if update.effective_user.id != ADMIN_ID: return
    key = update.message.text.replace("/del ", "", 1).strip()
    db = load_db()
    if key in db["replies"]:
        del db["replies"][key]
        save_db(db)
        await update.message.reply_text(f"🗑 حذف شد: {key}")
    else:
        await update.message.reply_text("نبود اصلاً 😂")

async def list_replies(update, context):
    if update.effective_user.id != ADMIN_ID: return
    db = load_db()
    if not db["replies"]:
        await update.message.reply_text("خالیه!")
        return
    out = "📋 جواب‌ها:\n\n"
    for k, v in db["replies"].items():
        out += f"🔹 {k}:\n   " + "\n   ".join(v) + "\n\n"
    await update.message.reply_text(out)

async def add_interval(update, context):
    if update.effective_user.id != ADMIN_ID: return
    msg = update.message.text.replace("/addint ", "", 1).strip()
    db = load_db()
    db["interval_messages"].append(msg)
    save_db(db)
    await update.message.reply_text(f"⏰ اضافه شد:\n{msg}")

async def clear_interval(update, context):
    if update.effective_user.id != ADMIN_ID: return
    db = load_db()
    db["interval_messages"] = []
    save_db(db)
    await update.message.reply_text("پاک شد ✅")

async def set_targets(update, context):
    if update.effective_user.id != ADMIN_ID: return
    names = update.message.text.replace("/targets ", "", 1).strip()
    db = load_db()
    db["targets"] = [n.strip() for n in names.split(",") if n.strip()]
    save_db(db)
    await update.message.reply_text("🎯 هدف‌ها:\n" + "\n".join(db["targets"]))

async def help_cmd(update, context):
    if update.effective_user.id != ADMIN_ID: return
    await update.message.reply_text(
        "🎛 دستورات:\n\n"
        "/add کلید | جواب\n/del کلید\n/list\n"
        "/addint متن\n/clearint\n/targets اسم1,اسم2\n"
    )

# ---------- گروه ----------
async def on_group_message(update, context):
    msg = update.effective_message
    if not msg or not msg.text: return
    if msg.chat.type not in ("group", "supergroup"): return

    db = load_db()
    if msg.chat.id not in db["seen_groups"]:
        db["seen_groups"].append(msg.chat.id)
        save_db(db)

    if msg.reply_to_message and msg.reply_to_message.from_user.id == context.bot.id:
        await smart_reply(update, context)
        return

    for key, answers in db["replies"].items():
        if key == "__reply_back__": continue
        if key in msg.text:
            await msg.reply_text(random.choice(answers))
            return

async def smart_reply(update, context):
    db = load_db()
    replies = db["replies"].get("__reply_back__")
    if replies:
        await update.message.reply_text(random.choice(replies))
    else:
        defaults = [
            "داداش تو چرا هنوز بیداری؟ 😂",
            "برو بابا تو کجا بودی اصلاً 🔥",
            "حرفت مثل خودت بی‌ارزشه 😎",
            "با من شوخی نکن، لهت می‌کنم 😂",
            "بچه جون برو بزرگ شو بعد بیا حرف بزن 🔥",
        ]
        await update.message.reply_text(random.choice(defaults))

# ---------- پیام دوره‌ای ----------
async def periodic_job(context):
    db = load_db()
    msgs = db["interval_messages"]
    targets = db["targets"]
    groups = db["seen_groups"]

    if not groups or not msgs: return

    for gid in groups:
        try:
            text = random.choice(msgs)
            if targets and "{name}" in text:
                text = text.replace("{name}", random.choice(targets))
            await context.bot.send_message(gid, text)
        except Exception as e:
            logger.warning(f"خطا در ارسال به {gid}: {e}")

async def track_chat(update, context):
    chat = update.effective_chat
    if chat.type in ("group", "supergroup"):
        db = load_db()
        if chat.id not in db["seen_groups"]:
            db["seen_groups"].append(chat.id)
            save_db(db)

# ---------- اجرا ----------
async def main_async():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("add", add_reply, filters.ChatType.PRIVATE))
    app.add_handler(CommandHandler("del", del_reply, filters.ChatType.PRIVATE))
    app.add_handler(CommandHandler("list", list_replies, filters.ChatType.PRIVATE))
    app.add_handler(CommandHandler("addint", add_interval, filters.ChatType.PRIVATE))
    app.add_handler(CommandHandler("clearint", clear_interval, filters.ChatType.PRIVATE))
    app.add_handler(CommandHandler("targets", set_targets, filters.ChatType.PRIVATE))
    app.add_handler(CommandHandler("help", help_cmd, filters.ChatType.PRIVATE))

    app.add_handler(MessageHandler(filters.TEXT & filters.ChatType.GROUPS, on_group_message))
    app.add_handler(ChatMemberHandler(track_chat, ChatMemberHandler.MY_CHAT_MEMBER))
    app.add_handler(MessageHandler(filters.ALL & filters.ChatType.GROUPS, track_chat))

    app.job_queue.run_repeating(periodic_job, interval=INTERVAL_SECONDS, first=60)

    await app.initialize()
    await app.bot.set_webhook(f"{WEBHOOK_URL}/{BOT_TOKEN}")
    await app.start()
    await app.updater.start_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=BOT_TOKEN,
        webhook_url=f"{WEBHOOK_URL}/{BOT_TOKEN}",
    )
    logger.info("🔥 حمال آنلاین شد...")
    stop_signal = asyncio.Event()
    await stop_signal.wait()

def main():
    Thread(target=run_health_server, daemon=True).start()
    asyncio.run(main_async())

if __name__ == "__main__":
    main()
