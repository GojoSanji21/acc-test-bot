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
from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from database.methods import delete_all_accounts
logger = logging.getLogger("TGStorageBot.plugins.start")

router = Router()

def get_main_keyboard() -> InlineKeyboardMarkup:
    """
    generates next-level dashboard keyboard filled with beautiful inline buttons arranged vertically.
    """
    keyboard = [
        [
            InlineKeyboardButton(text="➕ ᴀᴅᴅ ᴀᴄᴄᴏᴜɴᴛ", callback_data="menu:add_account")
        ],
        [
            InlineKeyboardButton(text="📋 ʟɪsᴛ ᴀᴄᴄᴏᴜɴᴛs", callback_data="menu:list_accounts")
        ],
        [
            InlineKeyboardButton(text="ℹ️ ʜᴇʟᴘ & ɪɴꜰᴏ", callback_data="menu:help")
        ],
        [
            InlineKeyboardButton(text="🗑️ ʀᴇᴍᴏᴠᴇ ᴀʟʟ sᴇssɪᴏɴs", callback_data="menu:remove_all_confirm")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_back_keyboard() -> InlineKeyboardMarkup:
    """
    returns standard back to menu inline keyboard.
    """
    keyboard = [[InlineKeyboardButton(text="🔙 ʙᴀᴄᴋ ᴛᴏ ᴍᴀɪɴ ᴍᴇɴᴜ", callback_data="menu:main")]]
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

@router.message(Command("start"))
async def send_welcome(message: Message):
    await message.answer(
        get_welcome_text(),
        parse_mode="HTML",
        disable_web_page_preview=True,
        reply_markup=get_main_keyboard()
    )

@router.message(Command("help"))
async def send_help(message: Message):
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
        [InlineKeyboardButton(text="✅ Yes, Delete All", callback_data="menu:remove_all_yes")],
        [InlineKeyboardButton(text="❌ Cancel", callback_data="menu:main")]
    ])
    await callback_query.message.edit_text(
        "⚠️ <b>Are you sure you want to delete ALL saved sessions? This cannot be undone.</b>",
        parse_mode="HTML",
        reply_markup=keyboard
    )

@router.callback_query(F.data == "menu:remove_all_yes")
async def remove_all_yes_callback(callback_query: CallbackQuery):
    await callback_query.answer()
    deleted_count = await delete_all_accounts(callback_query.from_user.id)
    await callback_query.message.edit_text(
        f"✅ <b>All sessions have been successfully removed.</b> (Deleted {deleted_count} accounts)",
        parse_mode="HTML",
        reply_markup=get_back_keyboard()
    )

@router.callback_query(F.data == "menu:main")
async def back_to_main_callback(callback_query: CallbackQuery):
    await callback_query.answer()
    await callback_query.message.edit_text(
        get_welcome_text(),
        parse_mode="HTML",
        disable_web_page_preview=True,
        reply_markup=get_main_keyboard()
    )

@router.callback_query(F.data == "menu:help")
async def help_callback(callback_query: CallbackQuery):
    await callback_query.answer()
    await callback_query.message.edit_text(
        get_help_text(),
        parse_mode="HTML",
        disable_web_page_preview=True,
        reply_markup=get_back_keyboard()
    )
