import logging
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from config import OWNER_ID
from database.connection import db

logger = logging.getLogger("TGStorageBot.plugins.admin")
router = Router()

async def get_user_name(message: Message, user_id: int) -> str:
    try:
        chat = await message.bot.get_chat(user_id)
        if chat.first_name:
            name = chat.first_name
            if chat.last_name:
                name += f" {chat.last_name}"
            return name
        elif chat.title:
            return chat.title
        else:
            return "User"
    except Exception as e:
        logger.error(f"Error getting user name for {user_id}: {e}")
        return "User"

@router.message(Command("add_admin"))
async def add_admin_command(message: Message):
    if message.from_user.id != OWNER_ID:
        return

    args = message.text.split()
    if len(args) < 2:
        return

    try:
        user_id = int(args[1])
    except ValueError:
        return

    await db["admins"].update_one({"user_id": user_id}, {"$set": {"user_id": user_id}}, upsert=True)
    user_name = await get_user_name(message, user_id)

    text = f"<b>ADMIN ADDED</b>\n<b><a href=\"tg://user?id={user_id}\">{user_name}</a></b>\nID: <code>{user_id}</code>"
    await message.answer(text, parse_mode="HTML")

@router.message(Command("remove_admin"))
async def remove_admin_command(message: Message):
    if message.from_user.id != OWNER_ID:
        return

    args = message.text.split()
    if len(args) < 2:
        return

    try:
        user_id = int(args[1])
    except ValueError:
        return

    await db["admins"].delete_one({"user_id": user_id})
    user_name = await get_user_name(message, user_id)

    text = f"<b>ADMIN REMOVED</b>\n<b><a href=\"tg://user?id={user_id}\">{user_name}</a></b>\nID: <code>{user_id}</code>"
    await message.answer(text, parse_mode="HTML")

@router.message(Command("list_admin"))
async def list_admin_command(message: Message):
    if message.from_user.id != OWNER_ID:
        return

    cursor = db["admins"].find({})
    admins = await cursor.to_list(length=100)

    if not admins:
        await message.answer("<b>ADMIN LIST</b>", parse_mode="HTML")
        return

    lines = ["<b>ADMIN LIST</b>"]

    for admin in admins:
        admin_id = admin["user_id"]
        admin_name = await get_user_name(message, admin_id)

        lines.append(f"<b><a href=\"tg://user?id={admin_id}\">{admin_name}</a></b>\nID: <code>{admin_id}</code>")

    text = "\n\n".join(lines)
    await message.answer(text, parse_mode="HTML")
