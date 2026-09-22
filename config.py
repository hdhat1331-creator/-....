import os

# --- اصلی ---
BOT_TOKEN = os.getenv("BOT_TOKEN", "8778309418:AAEv8Y32v1_8gQkZUHiQqZbQjStmNRAGv6A")
ADMIN_ID = int(os.getenv("ADMIN_ID", "8235703809"))
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "https://hamal-bot-6lpf.onrender.com")
PORT = int(os.getenv("PORT", "10000"))

# --- MongoDB ---
MONGO_URI = os.getenv(
    "MONGO_URI",
    "mongodb+srv://Amirkingef6677:Amirkingef6677@cluster0.bzg2v4m.mongodb.net/?appName=Cluster0"
)
DB_NAME = "hamal_bot"

# --- تنظیمات ---
GROUP_INTERVAL_SECONDS = 60 * 60  # ۱ ساعت
CLEANUP_INTERVAL_SECONDS = 6 * 60 * 60  # ۶ ساعت

# --- کلمات دستوری مدیریتی ---
CMD_UNMUTE = ["حذف سکوت", "آزاد"]
CMD_MUTE = ["سکوت"]
CMD_BAN = ["بن", "اخراج"]
