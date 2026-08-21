# =====================================================================================##
#
#  ██╗░░██╗███╗░░██╗██████╗░░█████╗░████████╗███████╗██████╗░
#  ██║░░██║████╗░██║██╔══██╗██╔══██╗╚══██╔══╝██╔════╝██╔══██╗
#  ██║░░██║██╔██╗██║██████╔╝███████║░░░██║░░░█████╗░░██║░░██║
#  ██║░░██║██║╚████║██╔══██╗██╔══██║░░░██║░░░██╔══╝░░██║░░██║
#  ╚█████╔╝██║░╚███║██║░░██║██║░░██║░░░██║░░░███████╗██████╔╝
#  ░╚════╝░╚═╝░░╚══╝╚═╝░░╚═╝╚═╝░░╚═╝░░░╚═╝░░░╚══════╝╚═════╝░
#
#  ░██████╗░██████╗░██████╗░███████╗██████╗░
#  ██╔════╝██╔═══██╗██╔══██╗██╔════╝██╔══██╗
#  ██║░░░░░██║░░░██║██║░░██║█████╗░░██████╔╝
#  ██║░░░░░██║░░░██║██║░░██║██╔══╝░░██╔══██╗
#  ╚██████╗╚██████╔╝██████╔╝███████╗██║░░██║
#  ░╚═════╝░╚═════╝░╚═════╝░╚══════╝╚═╝░░╚═╝
#
#                         ✨ MADE BY UNRATED CODER ✨
#                  Join Updates Channel: https://t.me/UNRATED_CODER
#=====================================================================================##

import logging
import asyncio
import random
from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.types import Message, LinkPreviewOptions, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto
from database.methods import delete_all_accounts
from database.connection import db
from config import OWNER_ID

logger = logging.getLogger("TGStorageBot.plugins.start")

router = Router()

IMAGES = [
    'https://graph.org/file/e8af951d867b0aaff8cb0-3205689663c5c662ba.jpg', 'https://graph.org/file/9ce76c7db28dc4daa5f27-b969a50f5a53345633.jpg',
    'https://graph.org/file/3207c5504dc9d45f5d9cf-a8e081cb548479752f.jpg', 'https://graph.org/file/c31949e692d280663d58b-175b7206869b9a2c82.jpg',
    'https://graph.org/file/800c9a3ee9ebc2097d38f-7609d3cf5ae42e41d5.jpg', 'https://graph.org/file/6e6502b5c2d6a68cac1c4-45a1ffc966477471c7.jpg',
    'https://graph.org/file/826a285bb1b76717d6a0e-0a8d4d501cf45fc2db.jpg', 'https://graph.org/file/0a315ee59fbc73bc44326-a766d350855ca79eca.jpg',
    'https://graph.org/file/ac509cacdbc03efbc2e8d-a8ac806b49a71e872d.jpg', 'https://graph.org/file/dd250b63501917843e481-3675d23c4799f97624.jpg',
    'https://graph.org/file/161d918adb1682dd7e301-32d10ea7256daacfa4.jpg', 'https://graph.org/file/7626817e26de338d2e5a1-478b1b721ca9bc63d3.jpg',
    'https://graph.org/file/dd250b63501917843e481-3675d23c4799f97624.jpg', 'https://graph.org/file/9c52583fba67124b6a183-586e58ffeeb840bc5e.jpg',
    'https://graph.org/file/91621631e7dc800ea4562-4b0a9c3601a270556d.jpg', 'https://graph.org/file/91621631e7dc800ea4562-4b0a9c3601a270556d.jpg',
    'https://graph.org/file/4abf7c572c4949e7f657e-3fbcdfd9fc67de5845.jpg', 'https://graph.org/file/89cddd266235b8a806f0e-6504ecc249b2e58ee7.jpg',
    'https://graph.org/file/eace0fc6fa82c0ca3521a-a089e3306f6386977d.jpg', 'https://graph.org/file/a50cde78b6d61ebb76ccd-9d02a956a89fddadd8.jpg',
    'https://graph.org/file/c77152bc70b96db0f079f-0cca0a31c983f97478.jpg', 'https://graph.org/file/019f4539cbecec208972c-c65454256e966a830c.jpg',
    'https://graph.org/file/d7f8b0cf7cf78723b3aee-a5b041281c203e2449.jpg', 'https://graph.org/file/8a012335580d322e7438f-353fbd48e95b00f0f7.jpg',
    'https://graph.org/file/c698be54a12027fb82e69-e9feef426481186208.jpg', 'https://graph.org/file/e3c28bdeb0c2af1b3bbb9-0c5a132aca7f768332.jpg',
    'https://graph.org/file/d8b92bfb4b8932e2ae553-ff9264f5b40c710698.jpg', 'https://graph.org/file/deff1d9b2af3c0740b525-9032f27f051633a627.jpg',
    'https://graph.org/file/a668600b4a516645369fa-465839cfd9e31ecf85.jpg', 'https://graph.org/file/f11e43b3ba09ff1af2eeb-a7d7c86298644597f3.jpg',
    'https://graph.org/file/13b0eaf75f4ffd28cd445-6e5b90592458fc05f1.jpg'
]

STICKERS = [
    "CAACAgUAAxkBAAIm72p5uhDyd5y4kTBgAAFXOJk32R8rAwAC2RQAAmcFaVZ86P4g9HBS6D0E",
    "CAACAgUAAxkBAAIm5Wp4nLY-xArcRez6HkUN0g80IAmIAAIeGgACx9AwVgmOMWuZKMGNPQQ"
]

def get_main_keyboard() -> InlineKeyboardMarkup:
    """
    generates next-level dashboard keyboard filled with beautiful inline buttons arranged vertically.
    """
    keyboard = [
        [
            InlineKeyboardButton(text="ᴀᴅᴅ ᴀᴄᴄᴏᴜɴᴛ", callback_data="menu:add_account"),
            InlineKeyboardButton(text="ʟɪsᴛ ᴀᴄᴄᴏᴜɴᴛs", callback_data="menu:list_accounts")
        ],
        [
            InlineKeyboardButton(text="ʜᴇʟᴘ & ɪɴғᴏ", callback_data="menu:help")
        ],
        [
            InlineKeyboardButton(text="ʀᴇᴍᴏᴠᴇ ᴀʟʟ sᴇssɪᴏɴs", callback_data="menu:remove_all_confirm")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_back_keyboard() -> InlineKeyboardMarkup:
    """
    returns standard back to menu inline keyboard.
    """
    keyboard = [[InlineKeyboardButton(text="ʙᴀᴄᴋ ᴛᴏ ᴍᴀɪɴ ᴍᴇɴᴜ", callback_data="menu:main")]]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_welcome_text() -> str:
    """
    returns beautifully designed welcome text in lowercase small caps.
    """
    welcome_text = (
        "👋 <b>ᴡᴇʟᴄᴏᴍᴇ ᴛᴏ ᴀᴅᴠᴀɴᴄᴇᴅ ᴛᴇʟᴇɢʀᴀᴍ ɪᴅ sᴛᴏʀᴀɢᴇ ʙᴏᴛ!</b>\n\n"
        "⚡ ᴛʜɪs ɴᴇxᴛ-ʟᴇᴠᴇʟ ᴅᴀsʜʙᴏᴀʀᴅ ʟᴇᴛs ʏᴏᴜ ᴇᴀsɪʟʏ ᴍᴀɴᴀɢᴇ ʏᴏᴜʀ ᴀᴄᴄᴏᴜɴᴛs ᴇɴᴛɪʀᴇʟʏ ᴠɪᴀ ɪɴʟɪɴᴇ ʙᴜᴛᴛᴏɴs. ɴᴏ ᴄᴏᴍᴍᴀɴᴅs ɴᴇᴇᴅᴇᴅ!\n\n"
        "🛡️ ᴀʟʟ sᴛʀɪɴɢ sᴇssɪᴏɴs ᴀʀᴇ ꜰᴜʟʟʏ ᴇɴᴄʀʏᴘᴛᴇᴅ ᴜsɪɴɢ ᴀᴇs-256 ʜʏʙʀɪᴅ sᴇᴄᴜʀɪᴛʏ.\n\n"
        "👤 <b>ᴅᴇᴠᴇʟᴏᴘᴇʀ ᴄʀᴇᴅɪᴛ:</b> ᴅᴇᴠᴇʟᴏᴘᴇᴅ ᴡɪᴛʜ ❤️ ʙʏ <a href=\"https://t.me/Unrated_Coder\">Unrated Coder</a>"
    )
    return welcome_text

def get_help_text() -> str:
    """
    returns assistance instructions text in lowercase small caps.
    """
    help_text = (
        "ℹ️ <b>ɪɴᴛᴇʀᴀᴄᴛɪᴠᴇ ʜᴇʟᴘ &amp; ᴅᴏᴄᴜᴍᴇɴᴛᴀᴛɪᴏɴ</b>\n\n"
        "➕ <b>ᴀᴅᴅ ᴀᴄᴄᴏᴜɴᴛ:</b>\n"
        "👉 ɢᴜɪᴅᴇs ʏᴏᴜ ᴛᴏ sᴇᴄᴜʀᴇʟʏ ᴄᴏɴɴᴇᴄᴛ ᴀɴʏ ᴛᴇʟᴇɢʀᴀᴍ ᴀᴄᴄᴏᴜɴᴛ sᴇssɪᴏɴ.\n\n"
        "📋 <b>ʟɪsᴛ ᴀᴄᴄᴏᴜɴᴛs:</b>\n"
        "👉 ᴅɪsᴘʟᴀʏs ᴀ ᴘᴀɢɪɴᴀᴛᴇᴅ ᴠɪᴇᴡ (6 ᴘᴇʀ ᴘᴀɢᴇ) ᴏꜰ ʏᴏᴜʀ sᴇssɪᴏɴs, sᴜᴘᴘᴏʀᴛɪɴɢ:\n"
        "  • 📁 <b>ᴅᴇᴛᴀɪʟs:</b> ᴇsᴛɪᴍᴀᴛᴇs ᴄʀᴇᴀᴛɪᴏɴ ᴀɢᴇ ᴀɴᴅ views ᴘʀᴇᴍɪᴜᴍ/ʀᴇsᴛʀɪᴄᴛᴇᴅ/ᴛʀᴜsᴛ.\n"
        "  • ✔️ <b>ᴠᴇʀɪꜰʏ:</b> ᴄʜᴇᴄᴋs ɪꜰ sᴇssɪᴏɴ ɪs ᴀʟɪᴠᴇ ᴏɴ ᴛᴇʟᴇɢʀᴀᴍ sᴇʀᴠᴇʀs.\n"
        "  • ✉️ <b>sᴇɴᴅ:</b> sᴇɴᴅs ᴄᴜsᴛᴏᴍ ᴍᴇssᴀɢᴇs ᴛᴏ ɪᴅs, ᴜsᴇʀɴᴀᴍᴇs, ᴏʀ ʟɪɴᴋs.\n"
        "  • 📩 <b>ᴏᴛᴘ ᴄᴏᴅᴇs:</b> sᴄᴀɴs ɪɴʙᴏx ᴀɴᴅ shows ᴄᴏᴅᴇ ɪɴsᴛᴀɴᴛʟʏ ɪɴ ᴀɴ ᴀʟᴇʀᴛ ᴘᴏᴘᴜᴘ!\n"
        "  • 🔑 <b>ᴇxᴛʀᴀᴄᴛ:</b> ᴏᴜᴛᴘᴜᴛs ᴀ ᴄᴏᴘʏ-ꜰʀɪᴇɴᴅʟʏ ʀᴀᴡ sᴛʀɪɴɢ sᴇssɪᴏɴ.\n"
        "  • 💾 <b>ᴇxᴘᴏʀᴛ sǫʟɪᴛᴇ:</b> sᴇɴᴅs ʏᴏᴜ ᴀ ᴘʜʏsɪᴄᴀʟ <code>.session</code> sǫʟɪᴛᴇ ꜰɪʟᴇ.\n"
        "  • 🔐 <b>sᴇᴄᴜʀɪᴛʏ:</b> ᴍᴀɴᴀɢᴇs 2ꜰᴀ, renames ᴘʀᴏꜰɪʟᴇs, views &amp; revokes active sessions.\n"
        "  • 🗑️ <b>ᴅᴇʟᴇᴛᴇ:</b> ᴡɪᴘᴇs ᴛʜᴇ sᴇssɪᴏɴ ꜰʀᴏᴍ ᴛʜᴇ ʙᴏᴛ ᴅᴀᴛᴀʙᴀsᴇ.\n\n"
        "👤 <b>ᴅᴇᴠᴇʟᴏᴘᴇʀ ᴄʀᴇᴅɪᴛ:</b> ᴅᴇᴠᴇʟᴏᴘᴇᴅ ᴡɪᴛʜ ❤️ ʙʏ <a href=\"https://t.me/Unrated_Coder\">Unrated Coder</a>"
    )
    return help_text

async def check_auth(user_id: int) -> bool:
    if user_id == OWNER_ID:
        return True
    admin = await db["admins"].find_one({"user_id": user_id})
    return bool(admin)

@router.message(Command("start"))
async def send_welcome_cmd(message: Message):
    try:
        await message.delete()
    except Exception:
        pass

    sticker_msg = await message.answer_sticker(random.choice(STICKERS))
    await asyncio.sleep(1.5)

    try:
        await sticker_msg.delete()
    except Exception:
        pass

    if not await check_auth(message.from_user.id):
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="• ᴍʏ ᴏᴡɴᴇʀ •", url="https://t.me/Unrated_Coder")]
        ])
        await message.answer("You're not a authorised user", reply_markup=keyboard)
        return

    random_url = random.choice(IMAGES)
    await message.answer(
        text=get_welcome_text(),
        parse_mode="HTML",
        reply_markup=get_main_keyboard(),
        link_preview_options=LinkPreviewOptions(url=random_url, prefer_large_media=True)
    )

@router.message(Command("help"))
async def send_help(message: Message):
    if getattr(message, "photo", None):
        # We don't strictly need this but it's safe
        pass
    # The requirement is just for start.py but the prompt specifically says "When ANY user sends /start"
    # For /help we just follow the old behavior but with an image because all bots send images for help too, maybe?
    # Or just keep edit_text behavior. The memory says: "Every single image sent by the bot across the repo must have a spoiler applied (has_spoiler=True)."
    # If it sends text only, it's fine.
    await message.answer(
        get_help_text(),
        parse_mode="HTML",
        disable_web_page_preview=True,
        reply_markup=get_back_keyboard()
    )

@router.callback_query(F.data == "menu:remove_all_confirm")
async def remove_all_confirm_callback(callback_query: CallbackQuery):
    await callback_query.answer()
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="ʏᴇs, ᴅᴇʟᴇᴛᴇ ᴀʟʟ", callback_data="menu:remove_all_yes")],
        [InlineKeyboardButton(text="ᴄᴀɴᴄᴇʟ", callback_data="menu:main")]
    ])

    # Since previous message could be photo or text, edit text / caption accordingly
    try:
        await callback_query.message.edit_text(
            "⚠️ <b>Are you sure you want to delete ALL saved sessions? This cannot be undone.</b>",
            parse_mode="HTML",
            reply_markup=keyboard,
            link_preview_options=LinkPreviewOptions(url=random.choice(IMAGES), prefer_large_media=True)
        )
    except Exception:
        # Fallback if it's currently a photo message
        await callback_query.message.delete()
        await callback_query.message.answer(
            "⚠️ <b>Are you sure you want to delete ALL saved sessions? This cannot be undone.</b>",
            parse_mode="HTML",
            reply_markup=keyboard,
            link_preview_options=LinkPreviewOptions(url=random.choice(IMAGES), prefer_large_media=True)
        )

@router.callback_query(F.data == "menu:remove_all_yes")
async def remove_all_yes_callback(callback_query: CallbackQuery):
    await callback_query.answer()
    deleted_count = await delete_all_accounts(callback_query.from_user.id)
    text = f"✅ <b>All sessions have been successfully removed.</b> (Deleted {deleted_count} accounts)"

    try:
        await callback_query.message.edit_text(
            text,
            parse_mode="HTML",
            reply_markup=get_back_keyboard(),
            link_preview_options=LinkPreviewOptions(url=random.choice(IMAGES), prefer_large_media=True)
        )
    except Exception:
        await callback_query.message.delete()
        await callback_query.message.answer(
            text,
            parse_mode="HTML",
            reply_markup=get_back_keyboard(),
            link_preview_options=LinkPreviewOptions(url=random.choice(IMAGES), prefer_large_media=True)
        )

@router.callback_query(F.data == "menu:main")
async def back_to_main_callback(callback_query: CallbackQuery):
    await callback_query.answer()

    try:
        await callback_query.message.edit_text(
            text=get_welcome_text(),
            parse_mode="HTML",
            reply_markup=get_main_keyboard(),
            link_preview_options=LinkPreviewOptions(url=random.choice(IMAGES), prefer_large_media=True)
        )
    except Exception:
        await callback_query.message.delete()
        await callback_query.message.answer(
            text=get_welcome_text(),
            parse_mode="HTML",
            reply_markup=get_main_keyboard(),
            link_preview_options=LinkPreviewOptions(url=random.choice(IMAGES), prefer_large_media=True)
        )

@router.callback_query(F.data == "menu:help")
async def help_callback(callback_query: CallbackQuery):
    await callback_query.answer()

    try:
        await callback_query.message.edit_text(
            get_help_text(),
            parse_mode="HTML",
            reply_markup=get_back_keyboard(),
            link_preview_options=LinkPreviewOptions(url=random.choice(IMAGES), prefer_large_media=True)
        )
    except Exception:
        await callback_query.message.delete()
        await callback_query.message.answer(
            get_help_text(),
            parse_mode="HTML",
            reply_markup=get_back_keyboard(),
            link_preview_options=LinkPreviewOptions(url=random.choice(IMAGES), prefer_large_media=True)
        )
