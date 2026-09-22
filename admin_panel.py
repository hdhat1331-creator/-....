from telegram import InlineKeyboardButton, InlineKeyboardMarkup


# ============ پنل ادمین اصلی ============
def main_panel():
    kb = [
        [InlineKeyboardButton("📋 جواب‌های گروه‌های من", callback_data="panel_myreplies")],
        [InlineKeyboardButton("⏰ پیام‌های دوره‌ای گروه‌ها", callback_data="panel_myintervals")],
        [InlineKeyboardButton("🌐 جواب‌های عمومی", callback_data="panel_global")],
        [InlineKeyboardButton("📢 پیام تبلیغاتی", callback_data="panel_broadcast")],
        [InlineKeyboardButton("📊 آمار کلی", callback_data="panel_stats")],
        [InlineKeyboardButton("🧹 پاک‌سازی گروه‌های مرده", callback_data="panel_cleanup")],
    ]
    return InlineKeyboardMarkup(kb)


# ============ پنل مالک گروه ============
def owner_panel(chat_id):
    kb = [
        [InlineKeyboardButton("📋 جواب‌ها", callback_data=f"op_replies_{chat_id}")],
        [InlineKeyboardButton("⏰ پیام دوره‌ای", callback_data=f"op_interval_{chat_id}")],
    ]
    return InlineKeyboardMarkup(kb)


def owner_replies_panel(chat_id):
    kb = [
        [InlineKeyboardButton("➕ افزودن جواب", callback_data=f"op_add_{chat_id}")],
        [InlineKeyboardButton("📋 لیست جواب‌ها", callback_data=f"op_list_{chat_id}")],
        [InlineKeyboardButton("🗑 حذف جواب", callback_data=f"op_del_{chat_id}")],
        [InlineKeyboardButton("🔙 برگشت", callback_data=f"op_back_{chat_id}")],
    ]
    return InlineKeyboardMarkup(kb)


def owner_interval_panel(chat_id):
    kb = [
        [InlineKeyboardButton("➕ افزودن پیام", callback_data=f"oi_add_{chat_id}")],
        [InlineKeyboardButton("📋 لیست", callback_data=f"oi_list_{chat_id}")],
        [InlineKeyboardButton("🗑 پاک کردن همه", callback_data=f"oi_clear_{chat_id}")],
        [InlineKeyboardButton("🔙 برگشت", callback_data=f"op_back_{chat_id}")],
    ]
    return InlineKeyboardMarkup(kb)


# ============ پنل جواب‌های عمومی ============
def global_panel():
    kb = [
        [InlineKeyboardButton("➕ افزودن جواب عمومی", callback_data="gp_add")],
        [InlineKeyboardButton("📋 لیست عمومی", callback_data="gp_list")],
        [InlineKeyboardButton("🗑 حذف عمومی", callback_data="gp_del")],
        [InlineKeyboardButton("🔙 برگشت", callback_data="panel_home")],
    ]
    return InlineKeyboardMarkup(kb)


# ============ دکمه‌ی برگشت ============
def back_button(cb="panel_home"):
    return InlineKeyboardMarkup([[InlineKeyboardButton("🔙 برگشت", callback_data=cb)]])


# ============ لیست گروه‌ها ============
def group_selector(groups):
    kb = []
    for g in groups:
        kb.append([InlineKeyboardButton(
            f"👥 {g['title']}",
            callback_data=f"sel_group_{g['chat_id']}"
        )])
    kb.append([InlineKeyboardButton("🔙 برگشت", callback_data="panel_home")])
    return InlineKeyboardMarkup(kb)
