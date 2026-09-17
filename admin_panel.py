from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def main_panel():
    kb = [
        [InlineKeyboardButton("📋 لیست جواب‌ها", callback_data="panel_list")],
        [InlineKeyboardButton("➕ افزودن جواب", callback_data="panel_add")],
        [InlineKeyboardButton("🗑 حذف جواب", callback_data="panel_del")],
        [InlineKeyboardButton("⏰ پیام‌های دوره‌ای", callback_data="panel_interval")],
        [InlineKeyboardButton("🎯 هدف‌ها", callback_data="panel_targets")],
        [InlineKeyboardButton("📊 وضعیت ربات", callback_data="panel_status")],
        [InlineKeyboardButton("🎮 بازی‌ها", callback_data="games_home")],
    ]
    return InlineKeyboardMarkup(kb)

def back_button(cb="panel_home"):
    return InlineKeyboardMarkup([[InlineKeyboardButton("🔙 برگشت", callback_data=cb)]])

def interval_panel():
    kb = [
        [InlineKeyboardButton("➕ افزودن پیام", callback_data="panel_addint")],
        [InlineKeyboardButton("📋 لیست پیام‌ها", callback_data="panel_listint")],
        [InlineKeyboardButton("🗑 پاک کردن همه", callback_data="panel_clearint")],
        [InlineKeyboardButton("🔙 برگشت", callback_data="panel_home")],
    ]
    return InlineKeyboardMarkup(kb)
