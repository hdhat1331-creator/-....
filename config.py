import os

BOT_TOKEN = os.getenv("BOT_TOKEN", "8778309418:AAEv8Y32v1_8gQkZUHiQqZbQjStmNRAGv6A")
ADMIN_ID = int(os.getenv("ADMIN_ID", "8235703809"))
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "https://hamal-bot-6lpf.onrender.com")
PORT = int(os.getenv("PORT", "10000"))
INTERVAL_SECONDS = 13 * 60
