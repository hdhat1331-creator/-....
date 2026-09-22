import asyncio
from telegram.error import TelegramError
from database import get_all_groups, groups_col


async def remove_dead_group(chat_id):
    await groups_col().delete_one({"chat_id": chat_id})


async def cleanup_dead_groups(bot):
    """پاک کردن گروه‌هایی که ربات دیگه عضوشون نیست"""
    groups = await get_all_groups()
    removed = 0
    for g in groups:
        try:
            member = await bot.get_chat_member(g["chat_id"], bot.id)
            if member.status in ("left", "kicked"):
                await remove_dead_group(g["chat_id"])
                removed += 1
        except TelegramError:
            await remove_dead_group(g["chat_id"])
            removed += 1
        await asyncio.sleep(0.05)
    return removed


async def cleanup_job(context):
    await cleanup_dead_groups(context.bot)
