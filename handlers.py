import random
import asyncio
from telegram import Update, ChatPermissions
from telegram.ext import ContextTypes
from telegram.error import TelegramError

from config import (
    ADMIN_ID, CMD_BAN, CMD_MUTE, CMD_UNMUTE, GROUP_INTERVAL_SECONDS
)
from database import (
    save_group, get_group, get_user_groups, get_all_groups,
    add_reply, get_replies, find_reply, delete_reply,
    add_global_reply, get_global_replies, find_global_reply, delete_global_reply,
    add_interval, get_intervals, clear_intervals, get_all_intervals,
    save_user, get_all_users,
)
from admin_panel import (
    main_panel, owner_panel, owner_replies_panel, owner_interval_panel,
    global_panel, back_button, group_selector,
)
from roasts import ROASTS
from cleanup import cleanup_dead_groups

# ============ حالت انتظار ادمین ============
WAITING = {}


# ============ توابع کمکی ============
def is_admin(user_id):
    return user_id == ADMIN_ID


async def is_group_admin(bot, chat_id, user_id):
    try:
        member = await bot.get_chat_member(chat_id, user_id)
        return member.status in ("administrator", "creator")
    except TelegramError:
        return False


# ============ /start و /panel ============
async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await save_user(user.id, user.first_name)

    if is_admin(user.id):
        await update.message.reply_text(
            "👑 پنل مدیریت اصلی حمال:",
            reply_markup=main_panel()
        )
        return

    groups = await get_user_groups(user.id)
    if not groups:
        await update.message.reply_text(
            "⛔ تو مالک یا ادمین هیچ گروهی نیستی که ربات توش باشه.\n"
            "اگه مالک گروهی هستی، ربات رو به گروهت اضافه کن."
        )
        return

    if len(groups) == 1:
        g = groups[0]
        await update.message.reply_text(
            f"👥 پنل گروه: {g['title']}",
            reply_markup=owner_panel(g["chat_id"])
        )
    else:
        await update.message.reply_text(
            "🎯 کدوم گروه رو می‌خوای مدیریت کنی؟",
            reply_markup=group_selector(groups)
        )


# ============ دستور /cleanup (فقط ادمین) ============
async def cleanup_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    await update.message.reply_text("🧹 دارم گروه‌های مرده رو پاک می‌کنم...")
    removed = await cleanup_dead_groups(context.bot)
    await update.message.reply_text(f"✅ {removed} گروه پاک شد.")


# ============ Callback اصلی پنل ============
async def panel_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    uid = q.from_user.id
    data = q.data

    # ---- خانه ----
    if data == "panel_home":
        if not is_admin(uid):
            await q.answer("دسترسی نداری", show_alert=True)
            return
        await q.answer()
        await q.edit_message_text("👑 پنل مدیریت اصلی حمال:", reply_markup=main_panel())
        return

    # ---- آمار ----
    if data == "panel_stats":
        if not is_admin(uid):
            await q.answer("دسترسی نداری", show_alert=True)
            return
        await q.answer()
        groups = await get_all_groups()
        users = await get_all_users()
        g_replies = await get_global_replies()
        text = (
            f"📊 آمار کلی:\n\n"
            f"👥 گروه‌ها: {len(groups)}\n"
            f"👤 کاربران: {len(users)}\n"
            f"🌐 جواب‌های عمومی: {len(g_replies)}"
        )
        await q.edit_message_text(text, reply_markup=back_button())
        return

    # ---- جواب‌های عمومی ----
    if data == "panel_global":
        if not is_admin(uid):
            await q.answer("دسترسی نداری", show_alert=True)
            return
        await q.answer()
        await q.edit_message_text(
            "🌐 جواب‌های عمومی (برای همه گروه‌ها):",
            reply_markup=global_panel()
        )
        return

    if data == "gp_add":
        if not is_admin(uid): return
        await q.answer()
        WAITING[uid] = {"action": "gp_add"}
        await q.edit_message_text(
            "فرمت بفرست:\nکلید | جواب",
            reply_markup=back_button("panel_global")
        )
        return

    if data == "gp_list":
        if not is_admin(uid): return
        await q.answer()
        items = await get_global_replies()
        if not items:
            text = "خالیه."
        else:
            text = "🌐 جواب‌های عمومی:\n\n"
            for r in items:
                text += f"🔹 {r['key']} → {r['reply']}\n"
        await q.edit_message_text(text, reply_markup=global_panel())
        return

    if data == "gp_del":
        if not is_admin(uid): return
        await q.answer()
        WAITING[uid] = {"action": "gp_del"}
        await q.edit_message_text(
            "کلید عمومی رو بفرست:",
            reply_markup=back_button("panel_global")
        )
        return

    # ---- پیام تبلیغاتی ----
    if data == "panel_broadcast":
        if not is_admin(uid):
            await q.answer("دسترسی نداری", show_alert=True)
            return
        await q.answer()
        WAITING[uid] = {"action": "broadcast"}
        await q.edit_message_text(
            "📢 متن پیام تبلیغاتی رو بفرست.\n"
            "به همه گروه‌ها و کاربران پیوی ارسال میشه.",
            reply_markup=back_button()
        )
        return

    # ---- جواب‌های گروه‌های من ----
    if data == "panel_myreplies":
        if not is_admin(uid): return
        await q.answer()
        groups = await get_user_groups(uid)
        if not groups:
            await q.edit_message_text("هیچ گروهی نداری.", reply_markup=back_button())
            return
        await q.edit_message_text("کدوم گروه؟", reply_markup=group_selector(groups))
        return

    # ---- پیام‌های دوره‌ای گروه‌های من ----
    if data == "panel_myintervals":
        if not is_admin(uid): return
        await q.answer()
        groups = await get_user_groups(uid)
        if not groups:
            await q.edit_message_text("هیچ گروهی نداری.", reply_markup=back_button())
            return
        await q.edit_message_text("کدوم گروه؟", reply_markup=group_selector(groups))
        return

    # ---- انتخاب گروه ----
    if data.startswith("sel_group_"):
        chat_id = int(data.replace("sel_group_", ""))
        g = await get_group(chat_id)
        if not g:
            await q.answer("گروه پیدا نشد", show_alert=True)
            return
        if not is_admin(uid):
            ok = (g.get("owner_id") == uid) or (uid in g.get("admins", []))
            if not ok:
                await q.answer("دسترسی نداری", show_alert=True)
                return
        await q.answer()
        await q.edit_message_text(
            f"👥 گروه: {g['title']}",
            reply_markup=owner_panel(chat_id)
        )
        return

    # ---- پنل مالک گروه ----
    if data.startswith("op_replies_"):
        chat_id = int(data.replace("op_replies_", ""))
        await q.answer()
        await q.edit_message_text(
            "📋 مدیریت جواب‌ها:",
            reply_markup=owner_replies_panel(chat_id)
        )
        return

    if data.startswith("op_interval_"):
        chat_id = int(data.replace("op_interval_", ""))
        await q.answer()
        await q.edit_message_text(
            "⏰ پیام‌های دوره‌ای (هر ۱ ساعت):",
            reply_markup=owner_interval_panel(chat_id)
        )
        return

    if data.startswith("op_back_"):
        chat_id = int(data.replace("op_back_", ""))
        await q.answer()
        await q.edit_message_text("👥 پنل گروه:", reply_markup=owner_panel(chat_id))
        return

    # ---- افزودن جواب گروه ----
    if data.startswith("op_add_"):
        chat_id = int(data.replace("op_add_", ""))
        await q.answer()
        WAITING[uid] = {"action": "add_reply", "chat_id": chat_id}
        await q.edit_message_text(
            "فرمت بفرست:\nکلید | جواب\n\nمثال:\nحمال | جانممم عشقم",
            reply_markup=back_button(f"op_replies_{chat_id}")
        )
        return

    if data.startswith("op_list_"):
        chat_id = int(data.replace("op_list_", ""))
        await q.answer()
        items = await get_replies(chat_id)
        if not items:
            text = "خالیه."
        else:
            text = "📋 جواب‌های این گروه:\n\n"
            for r in items:
                text += f"🔹 {r['key']} → {r['reply']}\n"
        await q.edit_message_text(text, reply_markup=owner_replies_panel(chat_id))
        return

    if data.startswith("op_del_"):
        chat_id = int(data.replace("op_del_", ""))
        await q.answer()
        WAITING[uid] = {"action": "del_reply", "chat_id": chat_id}
        await q.edit_message_text(
            "کلید جواب رو بفرست تا حذف شه:",
            reply_markup=back_button(f"op_replies_{chat_id}")
        )
        return

    # ---- پیام دوره‌ای ----
    if data.startswith("oi_add_"):
        chat_id = int(data.replace("oi_add_", ""))
        await q.answer()
        WAITING[uid] = {"action": "add_interval", "chat_id": chat_id}
        await q.edit_message_text(
            "متن پیام دوره‌ای رو بفرست:\n(هر ۱ ساعت یه بار ارسال میشه)",
            reply_markup=back_button(f"op_interval_{chat_id}")
        )
        return

    if data.startswith("oi_list_"):
        chat_id = int(data.replace("oi_list_", ""))
        await q.answer()
        items = await get_intervals(chat_id)
        if not items:
            text = "خالیه."
        else:
            text = "⏰ پیام‌های دوره‌ای:\n\n"
            for r in items:
                text += f"• {r['text']}\n"
        await q.edit_message_text(text, reply_markup=owner_interval_panel(chat_id))
        return

    if data.startswith("oi_clear_"):
        chat_id = int(data.replace("oi_clear_", ""))
        await q.answer()
        await clear_intervals(chat_id)
        await q.edit_message_text("✅ پاک شد.", reply_markup=owner_interval_panel(chat_id))
        return


# ============ دریافت متن از ادمین ============
async def admin_text_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if uid not in WAITING:
        return False

    info = WAITING.pop(uid)
    action = info.get("action")
    text = update.message.text.strip() if update.message.text else ""

    if action == "gp_add":
        if "|" not in text:
            await update.message.reply_text("فرمت درست نیست. باید: کلید | جواب")
            return True
        key, reply = [p.strip() for p in text.split("|", 1)]
        await add_global_reply(key, reply)
        await update.message.reply_text(f"✅ اضافه شد:\n«{key}» → {reply}", reply_markup=global_panel())
        return True

    if action == "gp_del":
        n = await delete_global_reply(text)
        if n:
            await update.message.reply_text(f"🗑 حذف شد: {text}", reply_markup=global_panel())
        else:
            await update.message.reply_text("نبود!", reply_markup=global_panel())
        return True

    if action == "broadcast":
        await update.message.reply_text("📢 دارم می‌فرستم... صبر کن.")
        groups = await get_all_groups()
        users = await get_all_users()
        sent_g = 0
        sent_u = 0
        for g in groups:
            try:
                await context.bot.send_message(g["chat_id"], text)
                sent_g += 1
                await asyncio.sleep(0.1)
            except Exception:
                pass
        for u in users:
            try:
                if u["user_id"] == ADMIN_ID:
                    continue
                await context.bot.send_message(u["user_id"], text)
                sent_u += 1
                await asyncio.sleep(0.1)
            except Exception:
                pass
        await update.message.reply_text(
            f"✅ ارسال شد:\n👥 به {sent_g} گروه\n👤 به {sent_u} کاربر",
            reply_markup=main_panel()
        )
        return True

    if action == "add_reply":
        chat_id = info["chat_id"]
        if "|" not in text:
            await update.message.reply_text("فرمت درست نیست. باید: کلید | جواب")
            return True
        key, reply = [p.strip() for p in text.split("|", 1)]
        await add_reply(chat_id, key, reply)
        await update.message.reply_text(
            f"✅ اضافه شد:\n«{key}» → {reply}",
            reply_markup=owner_replies_panel(chat_id)
        )
        return True

    if action == "del_reply":
        chat_id = info["chat_id"]
        n = await delete_reply(chat_id, text)
        if n:
            await update.message.reply_text(f"🗑 حذف شد: {text}", reply_markup=owner_replies_panel(chat_id))
        else:
            await update.message.reply_text("نبود!", reply_markup=owner_replies_panel(chat_id))
        return True

    if action == "add_interval":
        chat_id = info["chat_id"]
        await add_interval(chat_id, text)
        await update.message.reply_text(
            f"⏰ اضافه شد:\n{text}",
            reply_markup=owner_interval_panel(chat_id)
        )
        return True

    return False


# ============ پیوی ============
async def private_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return
    if update.message.text.startswith("/"):
        return
    if update.effective_user.id != ADMIN_ID:
        return
    await admin_text_input(update, context)


# ============ ردیابی گروه ============
async def track_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    if chat.type not in ("group", "supergroup"):
        return

    try:
        member = await context.bot.get_chat_member(chat.id, context.bot.id)
        if member.status in ("left", "kicked"):
            return
    except TelegramError:
        return

    owner_id = None
    owner_name = None
    try:
        admins = await context.bot.get_chat_administrators(chat.id)
        for a in admins:
            if a.status == "creator":
                owner_id = a.user.id
                owner_name = a.user.first_name
                break
    except TelegramError:
        pass

    await save_group(chat.id, chat.title or "بدون اسم", owner_id, owner_name)


# ============ پیام گروه ============
async def on_group_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.effective_message
    if not msg or not msg.text:
        return
    if msg.chat.type not in ("group", "supergroup"):
        return

    g = await get_group(msg.chat.id)
    if not g:
        await track_chat(update, context)

    text = msg.text.strip()
    sender_id = msg.from_user.id

    # ============ دستورات مدیریتی ============
    if msg.reply_to_message and msg.reply_to_message.from_user:
        target = msg.reply_to_message.from_user
        target_id = target.id
        target_name = target.first_name

        admin_ok = await is_group_admin(context.bot, msg.chat.id, sender_id)
        if admin_ok:
            # 1) حذف سکوت
            if any(cmd in text for cmd in CMD_UNMUTE):
                try:
                    perms = ChatPermissions(
                        can_send_messages=True,
                        can_send_audios=True,
                        can_send_documents=True,
                        can_send_photos=True,
                        can_send_videos=True,
                        can_send_video_notes=True,
                        can_send_voice_notes=True,
                        can_send_polls=True,
                        can_send_other_messages=True,
                        can_add_web_page_previews=True,
                    )
                    await context.bot.restrict_chat_member(msg.chat.id, target_id, perms)
                    await msg.reply_text(f"🔊 {target_name} آزاد شد.")
                except TelegramError as e:
                    await msg.reply_text(f"❌ نشد: {e}")
                return

            # 2) سکوت
            if any(cmd in text for cmd in CMD_MUTE):
                try:
                    perms = ChatPermissions(
                        can_send_messages=False,
                        can_send_audios=False,
                        can_send_documents=False,
                        can_send_photos=False,
                        can_send_videos=False,
                        can_send_video_notes=False,
                        can_send_voice_notes=False,
                        can_send_polls=False,
                        can_send_other_messages=False,
                        can_add_web_page_previews=False,
                    )
                    await context.bot.restrict_chat_member(msg.chat.id, target_id, perms)
                    await msg.reply_text(f"🔇 {target_name} سکوت شد.")
                except TelegramError as e:
                    await msg.reply_text(f"❌ نشد: {e}")
                return

            # 3) بن
            if any(cmd in text for cmd in CMD_BAN):
                try:
                    await context.bot.ban_chat_member(msg.chat.id, target_id)
                    await msg.reply_text(f"🚫 {target_name} بن شد.")
                except TelegramError as e:
                    await msg.reply_text(f"❌ نشد: {e}")
                return

    # ============ ریپلای روی پیام ربات ============
    if msg.reply_to_message and msg.reply_to_message.from_user.id == context.bot.id:
        await msg.reply_text(random.choice(ROASTS))
        return

    # ============ جواب گروه ============
    r = await find_reply(msg.chat.id, text)
    if r:
        await msg.reply_text(r)
        return

    # ============ جواب عمومی ============
    r = await find_global_reply(text)
    if r:
        await msg.reply_text(r)
        return

    # ============ حمال ============
    if "حمال" in text.lower() or "hamal" in text.lower():
        await msg.reply_text(random.choice(ROASTS))
        return


# ============ جاب دوره‌ای ============
async def group_interval_job(context: ContextTypes.DEFAULT_TYPE):
    intervals = await get_all_intervals()
    if not intervals:
        return
    by_group = {}
    for it in intervals:
        by_group.setdefault(it["chat_id"], []).append(it["text"])
    for chat_id, texts in by_group.items():
        try:
            text = random.choice(texts)
            await context.bot.send_message(chat_id, text)
            await asyncio.sleep(0.5)
        except Exception:
            pass
