import random
import time
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

# ============ استور بازی‌ها ============
# {game_id: {owner, opponent, game_type, round, scores, data, chat_id, msg_id}}
ACTIVE_GAMES = {}
GAME_COUNTER = [0]


def new_game_id():
    GAME_COUNTER[0] += 1
    return GAME_COUNTER[0]


# ============ منوی شروع بازی ============
def start_menu():
    kb = [
        [InlineKeyboardButton("🎲 تاس", callback_data="bg_pick_dice"),
         InlineKeyboardButton("🎯 دارت", callback_data="bg_pick_dart")],
        [InlineKeyboardButton("🏀 بسکتبال", callback_data="bg_pick_basket"),
         InlineKeyboardButton("⚽ فوتبال", callback_data="bg_pick_football")],
        [InlineKeyboardButton("🎳 بولینگ", callback_data="bg_pick_bowling"),
         InlineKeyboardButton("🎰 اسلات", callback_data="bg_pick_slot")],
        [InlineKeyboardButton("✊ سنگ کاغذ قیچی", callback_data="bg_pick_rps")],
    ]
    return InlineKeyboardMarkup(kb)


def join_button(game_id):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🎮 پیوستن به بازی", callback_data=f"bg_join_{game_id}")]
    ])


GAME_NAMES = {
    "dice": "🎲 تاس",
    "dart": "🎯 دارت",
    "basket": "🏀 بسکتبال",
    "football": "⚽ فوتبال",
    "bowling": "🎳 بولینگ",
    "slot": "🎰 اسلات",
    "rps": "✊ سنگ کاغذ قیچی",
}


def dice_emoji(game_type):
    return {
        "dice": "🎲", "dart": "🎯", "basket": "🏀",
        "football": "⚽", "bowling": "🎳",
    }.get(game_type)


# ============ ساخت بازی جدید ============
def create_game(chat_id, owner_id, owner_name, game_type):
    gid = new_game_id()
    ACTIVE_GAMES[gid] = {
        "chat_id": chat_id,
        "owner": owner_id,
        "owner_name": owner_name,
        "opponent": None,
        "opponent_name": None,
        "type": game_type,
        "round": 1,
        "max_rounds": 3,
        "scores": {owner_id: 0},
        "owner_points": 0,
        "opponent_points": 0,
        "state": "waiting",  # waiting | playing | done
        "data": {},
        "created_at": time.time(),
    }
    return gid


# ============ پیام انتظار ============
def waiting_text(game):
    return (
        f"🎮 {game['owner_name']} می‌خواد *{GAME_NAMES[game['type']]}* بازی کنه!\n"
        f"🥊 کی حریفش می‌شه؟\n\n"
        f"🏁 سه راند\n"
        f"🎯 روی دکمه زیر بزن تا وارد شی"
    )


# ============ شروع راند ============
def round_header(game):
    return (
        f"⚔️ *{game['owner_name']}* vs *{game['opponent_name']}*\n"
        f"🎮 {GAME_NAMES[game['type']]} — راند {game['round']} از {game['max_rounds']}\n"
        f"📊 امتیاز: {game['owner_name']} {game['owner_points']} - {game['opponent_points']} {game['opponent_name']}"
)
