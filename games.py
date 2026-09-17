import random
from telegram import InlineKeyboardButton, InlineKeyboardMarkup


# ============ منوی بازی‌ها (پنل ادمین) ============
def games_menu():
    kb = [
        [InlineKeyboardButton("🎲 تاس", callback_data="game_dice"),
         InlineKeyboardButton("🎯 دارت", callback_data="game_dart")],
        [InlineKeyboardButton("🏀 بسکتبال", callback_data="game_basket"),
         InlineKeyboardButton("⚽ فوتبال", callback_data="game_football")],
        [InlineKeyboardButton("🎳 بولینگ", callback_data="game_bowling"),
         InlineKeyboardButton("🎰 اسلات", callback_data="game_slot")],
        [InlineKeyboardButton("✊ سنگ کاغذ قیچی", callback_data="game_rps")],
        [InlineKeyboardButton("🔢 حدس عدد", callback_data="game_guess")],
        [InlineKeyboardButton("🔙 برگشت به پنل", callback_data="panel_home")],
    ]
    return InlineKeyboardMarkup(kb)


# ============ ایموجی تاس‌ها ============
DICE_EMOJIS = {
    "game_dice": "🎲",
    "game_dart": "🎯",
    "game_basket": "🏀",
    "game_football": "⚽",
    "game_bowling": "🎳",
}


# ============ منوی سنگ کاغذ قیچی ============
def rps_menu():
    kb = [[
        InlineKeyboardButton("✊ سنگ", callback_data="rps_rock"),
        InlineKeyboardButton("✋ کاغذ", callback_data="rps_paper"),
        InlineKeyboardButton("✌️ قیچی", callback_data="rps_scissors"),
    ], [
        InlineKeyboardButton("🔙 برگشت", callback_data="games_home"),
    ]]
    return InlineKeyboardMarkup(kb)


def rps_result(user_choice, bot_choice):
    rules = {"rock": "scissors", "paper": "rock", "scissors": "paper"}
    fa = {"rock": "✊ سنگ", "paper": "✋ کاغذ", "scissors": "✌️ قیچی"}
    if user_choice == bot_choice:
        return f"🤝 مساوی!\nتو: {fa[user_choice]}\nمن: {fa[bot_choice]}"
    if rules[user_choice] == bot_choice:
        return f"🎉 بردی!\nتو: {fa[user_choice]}\nمن: {fa[bot_choice]}"
    return f"😂 باختی!\nتو: {fa[user_choice]}\nمن: {fa[bot_choice]}"


# ============ اسلات ============
def slot_result():
    symbols = ["🍒", "🍋", "🔔", "⭐", "💎", "7️⃣"]
    spin = [random.choice(symbols) for _ in range(3)]
    line = " | ".join(spin)
    if spin[0] == spin[1] == spin[2]:
        return f"🎰 {line}\n🔥 جکپات! سه‌تا یکی!"
    if spin[0] == spin[1] or spin[1] == spin[2] or spin[0] == spin[2]:
        return f"🎰 {line}\n😎 دو تا یکی، خوبه!"
    return f"🎰 {line}\n😢 باختی، بازم امتحان کن"


# ============ حدس عدد ============
GUESS_GAMES = {}


def start_guess(user_id):
    GUESS_GAMES[user_id] = random.randint(1, 100)
    return "🔢 یه عدد بین ۱ تا ۱۰۰ انتخاب کردم. حدس بزن!\nعدد رو توی چت بنویس."
