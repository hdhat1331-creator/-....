import random
import time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from battle_games import (
    ACTIVE_GAMES, GAME_NAMES, create_game, start_menu,
    join_button, waiting_text, round_header, dice_emoji,
)


# ============ ورود کاربر: نوشتن "بازی" ============
async def battle_entry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    if not msg or not msg.text: return
    if msg.chat.type not in ("group", "supergroup"): return
    if "بازی" not in msg.text: return

    await msg.reply_text(
        "🎮 چه بازی‌ای می‌خوای؟",
        reply_markup=start_menu(),
    )


# ============ انتخاب نوع بازی ============
async def pick_game_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    data = q.data  # bg_pick_<type>
    game_type = data.replace("bg_pick_", "")
    user = q.from_user

    gid = create_game(
        chat_id=q.message.chat_id,
        owner_id=user.id,
        owner_name=user.first_name,
        game_type=game_type,
    )
    game = ACTIVE_GAMES[gid]

    await q.edit_message_text(
        waiting_text(game),
        reply_markup=join_button(gid),
        parse_mode="Markdown",
    )


# ============ پیوستن به بازی ============
async def join_game_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    data = q.data
    try:
        gid = int(data.replace("bg_join_", ""))
    except ValueError:
        await q.answer("بازی پیدا نشد")
        return

    game = ACTIVE_GAMES.get(gid)
    if not game:
        await q.answer("این بازی دیگه فعال نیست", show_alert=True)
        return

    user = q.from_user
    if user.id == game["owner"]:
        await q.answer("خودت صاحب بازی هستی 😂 منتظر حریف باش", show_alert=True)
        return

    if game["opponent"] is not None:
        await q.answer("یکی دیگه زودتر پیوست 😎", show_alert=True)
        return

    game["opponent"] = user.id
    game["opponent_name"] = user.first_name
    game["scores"][user.id] = 0
    game["state"] = "playing"
    game["round"] = 1

    await q.answer("🎮 وارد شدی!")
    await start_round(q.message, game, context)


# ============ شروع راند ============
async def start_round(msg, game, context):
    header = round_header(game)
    gtype = game["type"]

    # برای بازی‌های تاس‌مانند، دکمه پرتاب
    if gtype in ("dice", "dart", "basket", "football", "bowling"):
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton(
                f"🎲 پرتاب ({game['owner_name']})",
                callback_data=f"bg_throw_{game['owner']}_{id(game)}"
            )],
            [InlineKeyboardButton(
                f"🎲 پرتاب ({game['opponent_name']})",
                callback_data=f"bg_throw_{game['opponent']}_{id(game)}"
            )],
        ])
        await msg.reply_text(header, reply_markup=kb, parse_mode="Markdown")
        return

    if gtype == "slot":
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton(
                f"🎰 اسپین ({game['owner_name']})",
                callback_data=f"bg_spin_{game['owner']}_{id(game)}"
            )],
            [InlineKeyboardButton(
                f"🎰 اسپین ({game['opponent_name']})",
                callback_data=f"bg_spin_{game['opponent']}_{id(game)}"
            )],
        ])
        await msg.reply_text(header, reply_markup=kb, parse_mode="Markdown")
        return

    if gtype == "rps":
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton(
                f"✊✋✌️ انتخاب ({game['owner_name']})",
                callback_data=f"bg_rps_{game['owner']}_{id(game)}"
            )],
            [InlineKeyboardButton(
                f"✊✋✌️ انتخاب ({game['opponent_name']})",
                callback_data=f"bg_rps_{game['opponent']}_{id(game)}"
            )],
        ])
        await msg.reply_text(header, reply_markup=kb, parse_mode="Markdown")
        return


# پیدا کردن بازی با id تابع
def find_game_by_pyid(pyid):
    for gid, g in ACTIVE_GAMES.items():
        if id(g) == pyid:
            return gid, g
    return None, None
