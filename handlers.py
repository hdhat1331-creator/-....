import random
from telegram import Update
from telegram.ext import ContextTypes

from database import load_db, save_db
from config import ADMIN_ID
from games import (
    games_menu, DICE_EMOJIS, rps_menu, rps_result,
    slot_result, start_guess, GUESS_GAMES
)
from admin_panel import main_panel, back_button, interval_panel

# ============ حالت انتظار برای ورودی ادمین ============
WAITING = {}  # user_id -> action

# ---------- پنل ادمین ----------
async def panel_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("⛔ این ربات فقط برای ادمین کار می‌کنه.")
        return
    await update.message.reply_text("🎛 پنل مدیریت حمال:", reply_markup=main_panel())

async def panel_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    if q.from_user.id != ADMIN_ID:
        await q.answer("این پنل فقط برای ادمینه ❌", show_alert=True)
        return
    await q.answer()
    data = q.data
    db = load_db()

    # ---- خانه ----
    if data == "panel_home":
        await q.edit_message_text("🎛 پنل مدیریت حمال:", reply_markup=main_panel())
        return

    # ---- لیست جواب‌ها ----
    if data == "panel_list":
        if not db["replies"]:
            text = "📋 هیچ جوابی ثبت نشده."
        else:
            text = "📋 جواب‌های فعلی:\n\n"
            for k, v in db["replies"].items():
                text += f"🔹 {k}\n   " + "\n   ".join(v) + "\n\n"
        await q.edit_message_text(text, reply_markup=back_button())
        return

    # ---- افزودن جواب ----
    if data == "panel_add":
        WAITING[q.from_user.id] = "add"
        await q.edit_message_text(
            "✍️ الان بفرست:\nکلید | جواب\n\nمثال:\nحمال | جانممم عشقم",
            reply_markup=back_button()
        )
        return

    # ---- حذف جواب ----
    if data == "panel_del":
        WAITING[q.from_user.id] = "del"
        await q.edit_message_text(
            "🗑 اسم کلید رو بفرست تا حذف شه:", reply_markup=back_button()
        )
        return

    # ---- منوی دوره‌ای ----
    if data == "panel_interval":
        await q.edit_message_text("⏰ مدیریت پیام‌های دوره‌ای:", reply_markup=interval_panel())
        return

    if data == "panel_addint":
        WAITING[q.from_user.id] = "addint"
        await q.edit_message_text(
            "✍️ متن پیام دوره‌ای رو بفرست.\nبرای منشن کردن از {name} استفاده کن.",
            reply_markup=back_button()
        )
        return

    if data == "panel_listint":
        if not db["interval_messages"]:
            text = "📋 خالیه."
        else:
            text = "⏰ پیام‌های دوره‌ای:\n\n" + "\n".join(f"• {m}" for m in db["interval_messages"])
        await q.edit_message_text(text, reply_markup=interval_panel())
        return

    if data == "panel_clearint":
        db["interval_messages"] = []
        save_db(db)
        await q.edit_message_text("✅ پاک شد.", reply_markup=interval_panel())
        return

    # ---- هدف‌ها ----
    if data == "panel_targets":
        WAITING[q.from_user.id] = "targets"
        await q.edit_message_text(
            "🎯 اسم‌ها رو با کاما بفرست:\nعلی,رضا,محمد",
            reply_markup=back_button()
        )
        return

    # ---- وضعیت ربات ----
    if data == "panel_status":
        total = sum(len(v) for v in db["replies"].values())
        await q.edit_message_text(
            f"📊 وضعیت ربات:\n\n"
            f"📋 تعداد جواب‌ها: {total}\n"
            f"⏰ پیام‌های دوره‌ای: {len(db['interval_messages'])}\n"
            f"🎯 هدف‌ها: {len(db['targets'])}\n"
            f"👥 گروه‌های فعال: {len(db['seen_groups'])}",
            reply_markup=back_button()
        )
        return

# ---------- دریافت متن از ادمین (بعد از دکمه) ----------
async def admin_text_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if uid != ADMIN_ID: return False
    if uid not in WAITING: return False

    action = WAITING.pop(uid)
    text = update.message.text.strip()
    db = load_db()

    if action == "add":
        if "|" not in text:
            await update.message.reply_text("❌ فرمت درست نیست. باید: کلید | جواب")
            return True
        key, reply = [p.strip() for p in text.split("|", 1)]
        db["replies"].setdefault(key, []).append(reply)
        save_db(db)
        await update.message.reply_text(f"✅ اضافه شد:\n«{key}» → {reply}", reply_markup=main_panel())
        return True

    if action == "del":
        if text in db["replies"]:
            del db["replies"][text]
            save_db(db)
            await update.message.reply_text(f"🗑 حذف شد: {text}", reply_markup=main_panel())
        else:
            await update.message.reply_text("نبود!", reply_markup=main_panel())
        return True

    if action == "addint":
        db["interval_messages"].append(text)
        save_db(db)
        await update.message.reply_text(f"⏰ اضافه شد:\n{text}", reply_markup=interval_panel())
        return True

    if action == "targets":
        db["targets"] = [n.strip() for n in text.split(",") if n.strip()]
        save_db(db)
        await update.message.reply_text("🎯 ثبت شد:\n" + "\n".join(db["targets"]), reply_markup=main_panel())
        return True

    return False

# ---------- بازی‌ها ----------
async def games_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    data = q.data

    if data == "games_home":
        await q.edit_message_text("🎮 بازی‌ها:", reply_markup=games_menu())
        return

    if data in DICE_EMOJIS:
        await q.message.reply_dice(emoji=DICE_EMOJIS[data])
        return

    if data == "game_slot":
        await q.message.reply_text(slot_result())
        return

    if data == "game_rps":
        await q.edit_message_text("✊✋✌️ انتخاب کن:", reply_markup=rps_menu())
        return

    if data.startswith("rps_"):
        user_choice = data.replace("rps_", "")
        bot_choice = random.choice(["rock", "paper", "scissors"])
        result = rps_result(user_choice, bot_choice)
        await q.edit_message_text(result, reply_markup=games_menu())
        return

    if data == "game_guess":
        msg = start_guess(q.from_user.id)
        await q.edit_message_text(msg, reply_markup=games_menu())
        return

# ---------- گروه ----------
async def on_group_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.effective_message
    if not msg or not msg.text: return
    if msg.chat.type not in ("group", "supergroup"): return

    db = load_db()
    if msg.chat.id not in db["seen_groups"]:
        db["seen_groups"].append(msg.chat.id); save_db(db)

    # ---- حدس عدد ----
    uid = msg.from_user.id
    if uid in GUESS_GAMES and msg.text.strip().isdigit():
        guess = int(msg.text.strip())
        target = GUESS_GAMES[uid]
        if guess == target:
            del GUESS_GAMES[uid]
            await msg.reply_text(f"🎉 آفرین! درست حدس زدی: {target}")
        elif guess < target:
            await msg.reply_text("⬆️ بالاتره")
        else:
            await msg.reply_text("⬇️ پایین‌تره")
        return

    # ---- ریپلای روی پیام ربات → جواب تیکه ----
    if msg.reply_to_message and msg.reply_to_message.from_user.id == context.bot.id:
        replies = db["replies"].get("__reply_back__") or [
            "داداش تو چرا هنوز بیداری؟ 😂",
            "برو بابا تو کجا بودی اصلاً 🔥",
            "حرفت مثل خودت بی‌ارزشه 😎",
            "با من شوخی نکن، لهت می‌کنم 😂",
            "بچه جون برو بزرگ شو بعد بیا حرف بزن 🔥",
        ]
        await msg.reply_text(random.choice(replies))
        return

    # ---- کلمات کلیدی ----
    for key, answers in db["replies"].items():
        if key == "__reply_back__": continue
        if key in msg.text:
            await msg.reply_text(random.choice(answers))
            return

# ---------- پیام دوره‌ای ----------
async def periodic_job(context: ContextTypes.DEFAULT_TYPE):
    db = load_db()
    msgs = db["interval_messages"]; targets = db["targets"]; groups = db["seen_groups"]
    if not groups or not msgs: return
    for gid in groups:
        try:
            text = random.choice(msgs)
            if targets and "{name}" in text:
                text = text.replace("{name}", random.choice(targets))
            await context.bot.send_message(gid, text)
        except Exception:
            pass

async def track_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    if chat.type in ("group", "supergroup"):
        db = load_db()
        if chat.id not in db["seen_groups"]:
            db["seen_groups"].append(chat.id); save_db(db)
