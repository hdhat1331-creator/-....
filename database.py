from motor.motor_asyncio import AsyncIOMotorClient
from config import MONGO_URI, DB_NAME

_client = None
_db = None

def get_db():
    global _client, _db
    if _db is None:
        _client = AsyncIOMotorClient(MONGO_URI)
        _db = _client[DB_NAME]
    return _db

# ============ مجموعه‌ها ============
def groups_col():
    return get_db()["groups"]

def replies_col():
    return get_db()["replies"]

def interval_col():
    return get_db()["interval_msgs"]

def users_col():
    return get_db()["users"]

def global_replies_col():
    return get_db()["global_replies"]


# ============ گروه‌ها ============
async def save_group(chat_id, title, owner_id=None, owner_name=None):
    col = groups_col()
    existing = await col.find_one({"chat_id": chat_id})
    if not existing:
        await col.insert_one({
            "chat_id": chat_id,
            "title": title,
            "owner_id": owner_id,
            "owner_name": owner_name,
            "admins": [owner_id] if owner_id else [],
        })
    else:
        upd = {"title": title}
        if owner_id and not existing.get("owner_id"):
            upd["owner_id"] = owner_id
            upd["owner_name"] = owner_name
            admins = existing.get("admins", [])
            if owner_id not in admins:
                admins.append(owner_id)
            upd["admins"] = admins
        await col.update_one({"chat_id": chat_id}, {"$set": upd})


async def get_group(chat_id):
    return await groups_col().find_one({"chat_id": chat_id})


async def get_user_groups(user_id):
    """گروه‌هایی که کاربر مالک یا ادمینشونه"""
    col = groups_col()
    cursor = col.find({"$or": [{"owner_id": user_id}, {"admins": user_id}]})
    return await cursor.to_list(length=None)


async def get_all_groups():
    cursor = groups_col().find({})
    return await cursor.to_list(length=None)


# ============ جواب‌های مخصوص گروه ============
async def add_reply(chat_id, key, reply):
    await replies_col().insert_one({
        "chat_id": chat_id, "key": key, "reply": reply
    })


async def get_replies(chat_id):
    cursor = replies_col().find({"chat_id": chat_id})
    return await cursor.to_list(length=None)


async def find_reply(chat_id, text):
    cursor = replies_col().find({"chat_id": chat_id})
    async for r in cursor:
        if r["key"] in text:
            return r["reply"]
    return None


async def delete_reply(chat_id, key):
    res = await replies_col().delete_many({"chat_id": chat_id, "key": key})
    return res.deleted_count


# ============ جواب‌های عمومی (فقط ادمین ربات) ============
async def add_global_reply(key, reply):
    await global_replies_col().insert_one({"key": key, "reply": reply})


async def get_global_replies():
    cursor = global_replies_col().find({})
    return await cursor.to_list(length=None)


async def find_global_reply(text):
    cursor = global_replies_col().find({})
    async for r in cursor:
        if r["key"] in text:
            return r["reply"]
    return None


async def delete_global_reply(key):
    res = await global_replies_col().delete_many({"key": key})
    return res.deleted_count


# ============ پیام‌های دوره‌ای گروه ============
async def add_interval(chat_id, text):
    await interval_col().insert_one({"chat_id": chat_id, "text": text})


async def get_intervals(chat_id):
    cursor = interval_col().find({"chat_id": chat_id})
    return await cursor.to_list(length=None)


async def clear_intervals(chat_id):
    await interval_col().delete_many({"chat_id": chat_id})


async def get_all_intervals():
    cursor = interval_col().find({})
    return await cursor.to_list(length=None)


# ============ کاربران (برای تبلیغات پیوی) ============
async def save_user(user_id, first_name=None):
    col = users_col()
    existing = await col.find_one({"user_id": user_id})
    if not existing:
        await col.insert_one({"user_id": user_id, "first_name": first_name})
    else:
        await col.update_one({"user_id": user_id}, {"$set": {"first_name": first_name}})


async def get_all_users():
    cursor = users_col().find({})
    return await cursor.to_list(length=None)
