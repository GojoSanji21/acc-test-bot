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
import os
import base64
import struct
import html
import re
from pathlib import Path
from datetime import datetime
import datetime as dt
from aiogram import Router, F, Bot, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery, FSInputFile

from database import delete_account, get_all_accounts, get_account, save_account
from helpers import decrypt_data, create_pyrogram_client, encrypt_data, pyrogram_to_telethon, generate_telethon_sqlite

from pyrogram import raw
from pyrogram.storage.file_storage import FileStorage
from pyrogram.storage.memory_storage import MemoryStorage

# Pyrogram exceptions
from pyrogram.errors import (
    AuthKeyInvalid,
    RPCError
)

logger = logging.getLogger("TGStorageBot.plugins.list_accounts")

router = Router()

class SecurityStates(StatesGroup):
    waiting_for_new_2fa = State()
    waiting_for_remove_2fa = State()
    waiting_for_new_name = State()

class SendStates(StatesGroup):
    waiting_for_target = State()
    waiting_for_message = State()

def make_small_caps(text: str) -> str:
    mapping = {
        'a': 'ᴀ', 'b': 'ʙ', 'c': 'ᴄ', 'd': 'ᴅ', 'e': 'ᴇ', 'f': 'ꜰ', 'g': 'ɢ', 'h': 'ʜ',
        'i': 'ɪ', 'j': 'ᴊ', 'k': 'ᴋ', 'l': 'ʟ', 'm': 'ᴍ', 'n': 'ɴ', 'o': 'ᴏ', 'p': 'ᴘ',
        'q': 'ǫ', 'r': 'ʀ', 's': 's', 't': 'ᴛ', 'u': 'ᴜ', 'v': 'ᴠ', 'w': 'ᴡ', 'x': 'x',
        'y': 'ʏ', 'z': 'ᴢ',
        'A': 'ᴀ', 'B': 'ʙ', 'C': 'ᴄ', 'D': 'ᴅ', 'E': 'ᴇ', 'F': 'ꜰ', 'G': 'ɢ', 'H': 'ʜ',
        'I': 'ɪ', 'J': 'ᴊ', 'K': 'ᴋ', 'L': 'ʟ', 'M': 'ᴍ', 'N': 'ɴ', 'O': 'ᴏ', 'P': 'ᴘ',
        'Q': 'ǫ', 'R': 'ʀ', 'S': 's', 'T': 'ᴛ', 'U': 'ᴜ', 'V': 'ᴠ', 'W': 'ᴡ', 'X': 'x',
        'Y': 'ʏ', 'Z': 'ᴢ'
    }
    return "".join(mapping.get(c, c) for c in text)

def estimate_account_age(user_id: int) -> tuple[str, str]:
    """
    Estimates the creation date and human-readable age of a Telegram account from user ID.
    """
    landmarks = [
        (10000000, datetime(2013, 12, 31)),
        (95000000, datetime(2014, 12, 31)),
        (185000000, datetime(2015, 12, 31)),
        (315000000, datetime(2016, 12, 31)),
        (490000000, datetime(2017, 12, 31)),
        (730000000, datetime(2018, 12, 31)),
        (1000000000, datetime(2019, 12, 31)),
        (1500000000, datetime(2020, 12, 31)),
        (2200000000, datetime(2021, 12, 31)),
        (5000000000, datetime(2022, 12, 31)),
        (6400000000, datetime(2023, 12, 31)),
        (7300000000, datetime(2024, 12, 31)),
        (8500000000, datetime(2025, 12, 31)),
    ]

    start_id = 100000
    start_date = datetime(2013, 8, 14)

    lower_id, lower_date = start_id, start_date
    upper_id, upper_date = None, None

    for lid, ldate in landmarks:
        if user_id <= lid:
            upper_id, upper_date = lid, ldate
            break
        lower_id, lower_date = lid, ldate

    if upper_id is None:
        upper_id = 10000000000
        upper_date = datetime(2026, 12, 31)

    id_diff = upper_id - lower_id
    if id_diff == 0:
         id_diff = 1
    fraction = (user_id - lower_id) / id_diff

    seconds_diff = (upper_date - lower_date).total_seconds()
    est_seconds = seconds_diff * fraction
    est_date = lower_date + dt.timedelta(seconds=est_seconds)

    now = datetime.now()
    age_delta = now - est_date

    years = age_delta.days // 365
    remaining_days = age_delta.days % 365
    months = remaining_days // 30
    days = remaining_days % 30

    creation_date_str = est_date.strftime("%B %Y")
    creation_date_sc = make_small_caps(creation_date_str)

    if years > 0:
        age_sc = make_small_caps(f"{years} ʏᴇᴀʀs, {months} ᴍᴏɴᴛʜs")
    elif months > 0:
        age_sc = make_small_caps(f"{months} ᴍᴏɴᴛʜs, {days} ᴅᴀʏs")
    else:
        age_sc = make_small_caps(f"{days} ᴅᴀʏs")

    return creation_date_sc, age_sc

def get_back_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 ʙᴀᴄᴋ ᴛᴏ ᴍᴀɪɴ ᴍᴇɴᴜ", callback_data="menu:main")]
    ])

def get_back_to_panel_keyboard(phone: str, page: int = 0) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 ʙᴀᴄᴋ ᴛᴏ ᴘᴀɴᴇʟ", callback_data=f"view_acc:{phone}:{page}")]
    ])

def get_accounts_keyboard(accounts: list, page: int = 0) -> InlineKeyboardMarkup:
    keyboard = []

    start_idx = page * 6
    end_idx = start_idx + 6
    page_accounts = accounts[start_idx:end_idx]

    for acc in page_accounts:
        phone = acc.get("phone")
        p_name = acc.get("profile_name") or "ᴜɴᴋɴᴏᴡɴ"
        btn_text = f"📱 {phone} | ⚙️ {p_name}"
        keyboard.append([InlineKeyboardButton(text=btn_text, callback_data=f"view_acc:{phone}:{page}")])

    # Navigation row (only if total accounts > 6)
    nav_row = []
    if page > 0:
        nav_row.append(InlineKeyboardButton(text="◀️ ᴘʀᴇᴠ", callback_data=f"list_page:{page - 1}"))
    if end_idx < len(accounts):
        nav_row.append(InlineKeyboardButton(text="ɴᴇxᴛ ▶️", callback_data=f"list_page:{page + 1}"))

    if nav_row:
        keyboard.append(nav_row)

    # Add Bulk Export button inside accounts list, above back to main menu
    keyboard.append([InlineKeyboardButton(text="📦 ʙᴜʟᴋ ᴇxᴘᴏʀᴛ / ɢᴇɴᴇʀᴀᴛᴇ", callback_data=f"bulk_export:menu:{page}")])

    keyboard.append([InlineKeyboardButton(text="🔙 ʙᴀᴄᴋ ᴛᴏ ᴍᴀɪɴ ᴍᴇɴᴜ", callback_data="menu:main")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

async def save_session_string_to_file(session_string: str, name: str, workdir: Path) -> Path:
    storage = FileStorage(name, workdir)
    await storage.open()

    mem_storage = MemoryStorage(name, session_string)
    await mem_storage.open()

    await storage.dc_id(await mem_storage.dc_id())
    await storage.api_id(await mem_storage.api_id())
    await storage.test_mode(await mem_storage.test_mode())
    await storage.auth_key(await mem_storage.auth_key())
    await storage.user_id(await mem_storage.user_id())
    await storage.is_bot(await mem_storage.is_bot())
    await storage.date(await mem_storage.date())

    await mem_storage.close()
    await storage.save()
    await storage.close()

    return workdir / f"{name}.session"

async def check_otp_logic(callback_query: CallbackQuery, phone: str, page: int):
    """
    Directly scans the inbox history of official Telegram service (777000)
    to fetch any active OTP verification code instantly.
    """
    # 1. Instantly trigger the toast popup header!
    try:
        await callback_query.answer("🔍 ᴄʜᴇᴄᴋɪɴɢ ꜰᴏʀ ᴛʜᴇ ʟᴀᴛᴇsᴛ ᴏᴛᴘ ᴏɴ ᴀᴄᴄᴏᴜɴᴛ...", show_alert=False)
    except Exception as e:
        logger.warning(f"Could not answer callback query at check_otp_logic start: {e}")

    # 2. Show loading message
    await callback_query.message.edit_text(
        f"⏳ <b>sᴄᴀɴɴɪɴɢ ʏᴏᴜʀ ɪɴʙᴏx ꜰᴏʀ ᴛʜᴇ ʟᴀᴛᴇsᴛ ᴏᴛᴘ ᴄᴏᴅᴇ ᴏɴ</b> <code>{html.escape(phone)}</code>... <b>ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ.</b>",
        parse_mode="HTML"
    )

    acc = await get_account(phone, user_id=callback_query.from_user.id)
    if not acc:
        await callback_query.message.edit_text("❌ <b>sᴇʟᴇᴄᴛᴇᴅ ᴀᴄᴄᴏᴜɴᴛ ɴᴏ ʟᴏɴɢᴇʀ ᴇxɪsᴛs.</b>", reply_markup=get_back_keyboard(), parse_mode="HTML")
        return

    session_str = decrypt_data(acc["encrypted_session"])
    proxy = acc.get("proxy")
    custom_api = acc.get("custom_api")

    client = create_pyrogram_client(f"otp_{phone.replace('+', '')}", session_str, proxy, custom_api)
    try:
        await client.connect()

        found = False
        async for msg in client.get_chat_history(777000, limit=5):
            text = msg.text or msg.caption or ""
            if "login code" in text.lower() or "verification code" in text.lower():
                otp_match = re.search(r"\b(\d{5,6})\b", text)
                if otp_match:
                    otp_code = otp_match.group(1)
                    escaped_text = html.escape(text)

                    # Native Telegram Alert Dialog containing the code!
                    try:
                        await callback_query.bot.answer_callback_query(
                            callback_query_id=callback_query.id,
                            text=f"🔑 ʏᴏᴜʀ ᴏᴛᴘ ᴄᴏᴅᴇ: {otp_code}",
                            show_alert=True
                        )
                    except Exception as answer_err:
                        logger.warning(f"Failed to send OTP alert popup: {answer_err}")

                    success_text = (
                        "━━━━━━━━━━━━━━━━━━━━━\n"
                        "🔑 <b>ᴛᴇʟᴇɢʀᴀᴍ ʟᴏɢɪɴ ᴏᴛᴘ ʀᴇᴄᴇɪᴠᴇᴅ!</b>\n"
                        "━━━━━━━━━━━━━━━━━━━━━\n"
                        f"📱 <b>ᴀᴄᴄᴏᴜɴᴛ:</b> <code>{html.escape(phone)}</code>\n"
                        f"🔑 <b>ʟᴏɢɪɴ ᴄᴏᴅᴇ:</b> <code>{otp_code}</code>\n\n"
                        f"📝 <b>ᴍᴇssᴀɢᴇ ᴅᴇᴛᴀɪʟs:</b>\n<code>{escaped_text}</code>"
                    )

                    refresh_kbd = [
                        [
                            InlineKeyboardButton(text="🔄 ᴄʜᴇᴄᴋ ᴀɢᴀɪɴ / ʀᴇꜰʀᴇsʜ", callback_data=f"check_otp:{phone}:{page}"),
                            InlineKeyboardButton(text="🔙 ʙᴀᴄᴋ ᴛᴏ ᴘᴀɴᴇʟ", callback_data=f"view_acc:{phone}:{page}")
                        ]
                    ]

                    await callback_query.message.edit_text(
                        success_text,
                        reply_markup=InlineKeyboardMarkup(inline_keyboard=refresh_kbd),
                        parse_mode="HTML"
                    )
                    found = True
                    break

        if not found:
            # Native Telegram Alert Dialog showing no OTP
            try:
                await callback_query.bot.answer_callback_query(
                    callback_query_id=callback_query.id,
                    text="❌ ɴᴏ ʀᴇᴄᴇɴᴛ ᴏᴛᴘ ᴄᴏᴅᴇ ꜰᴏᴜɴᴅ ɪɴ ʏᴏᴜʀ ɪɴʙᴏx.",
                    show_alert=True
                )
            except Exception as answer_err:
                logger.warning(f"Failed to send no-OTP alert popup: {answer_err}")

            fail_text = (
                "━━━━━━━━━━━━━━━━━━━━━\n"
                "⚠️ <b><b>ɴᴏ ʀᴇᴄᴇɴᴛ ᴏᴛᴘ ᴄᴏᴅᴇ ꜰᴏᴜɴᴅ!</b></b>\n"
                "━━━━━━━━━━━━━━━━━━━━━\n"
                f"📱 <b>ᴀᴄᴄᴏᴜɴᴛ:</b> <code>{html.escape(phone)}</code>\n\n"
                "👉 ᴘʟᴇᴀsᴇ ᴍᴀᴋᴇ sᴜʀᴇ ʏᴏᴜ ᴛʀɪɢɢᴇʀᴇᴅ ᴛʜᴇ ʟᴏɢɪɴ ᴄᴏᴅᴇ ʀᴇǫᴜᴇsᴛ on your official Telegram App or device first, then click the refresh button below to scan again!"
            )

            refresh_kbd = [
                [
                    InlineKeyboardButton(text="🔄 ᴄʜᴇᴄᴋ ᴀɢᴀɪɴ / ʀᴇꜰʀᴇsʜ", callback_data=f"check_otp:{phone}:{page}"),
                    InlineKeyboardButton(text="🔙 ʙᴀᴄᴋ ᴛᴏ ᴘᴀɴᴇʟ", callback_data=f"view_acc:{phone}:{page}")
                ]
            ]

            await callback_query.message.edit_text(
                fail_text,
                reply_markup=InlineKeyboardMarkup(inline_keyboard=refresh_kbd),
                parse_mode="HTML"
            )

    except Exception as e:
        await callback_query.message.edit_text(
            f"❌ <b>ꜰᴀɪʟᴇᴅ ᴛᴏ sᴄᴀɴ ɪɴʙᴏx:</b> <code>{html.escape(str(e))}</code>",
            reply_markup=get_back_to_panel_keyboard(phone, page),
            parse_mode="HTML"
        )
    finally:
        try:
            if client.is_connected:
                await client.disconnect()
        except Exception:
            pass

@router.callback_query(F.data == "menu:list_accounts")
async def list_accounts_callback(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.answer()
    await state.clear()
    accounts = await get_all_accounts(user_id=callback_query.from_user.id)
    if not accounts:
        await callback_query.message.edit_text(
            "📭 <b><b>ɴᴏ sᴀᴠᴇᴅ ᴛᴇʟᴇɢʀᴀᴍ ᴀᴄᴄᴏᴜɴᴛs ꜰᴏᴜɴᴅ ɪɴ ᴛʜᴇ ᴅᴀᴛᴀʙᴀsᴇ.</b></b>",
            reply_markup=get_back_keyboard(),
            parse_mode="HTML"
        )
        return

    await callback_query.message.edit_text(
        "📋 <b>sᴇʟᴇᴄᴛ ᴀɴ ᴀᴄᴄᴏᴜɴᴛ ꜰʀᴏᴍ ᴛʜᴇ ʟɪsᴛ:</b>",
        reply_markup=get_accounts_keyboard(accounts, page=0),
        parse_mode="HTML"
    )

@router.callback_query(F.data.startswith("list_page:"))
async def process_list_pagination(callback_query: CallbackQuery):
    await callback_query.answer()
    page = int(callback_query.data.split(":")[1])

    accounts = await get_all_accounts(user_id=callback_query.from_user.id)
    if not accounts:
        await callback_query.message.edit_text(
            "📭 <b><b>ɴᴏ sᴀᴠᴇᴅ ᴛᴇʟᴇɢʀᴀᴍ ᴀᴄᴄᴏᴜɴᴛs ꜰᴏᴜɴᴅ ɪɴ ᴛʜᴇ ᴅᴀᴛᴀʙᴀsᴇ.</b></b>",
            reply_markup=get_back_keyboard(),
            parse_mode="HTML"
        )
        return

    await callback_query.message.edit_text(
        "📋 <b>sᴇʟᴇᴄᴛ ᴀɴ ᴀᴄᴄᴏᴜɴᴛ ꜰʀᴏᴍ ᴛʜᴇ ʟɪsᴛ:</b>",
        reply_markup=get_accounts_keyboard(accounts, page=page),
        parse_mode="HTML"
    )

@router.callback_query(F.data.startswith("back_to_list:"))
async def process_back_to_list(callback_query: CallbackQuery):
    await callback_query.answer()
    page = int(callback_query.data.split(":")[1])

    accounts = await get_all_accounts(user_id=callback_query.from_user.id)
    if not accounts:
        await callback_query.message.edit_text(
            "📭 <b><b>ɴᴏ sᴀᴠᴇᴅ ᴛᴇʟᴇɢʀᴀᴍ ᴀᴄᴄᴏᴜɴᴛs ꜰᴏᴜɴᴅ ɪɴ ᴛʜᴇ ᴅᴀᴛᴀʙᴀsᴇ.</b></b>",
            reply_markup=get_back_keyboard(),
            parse_mode="HTML"
        )
        return

    await callback_query.message.edit_text(
        "📋 <b>sᴇʟᴇᴄᴛ ᴀɴ ᴀᴄᴄᴏᴜɴᴛ ꜰʀᴏᴍ ᴛʜᴇ ʟɪsᴛ:</b>",
        reply_markup=get_accounts_keyboard(accounts, page=page),
        parse_mode="HTML"
    )

@router.callback_query(F.data.startswith("check_otp:"))
async def process_check_otp_callback(callback_query: CallbackQuery):
    parts = callback_query.data.split(":")
    phone = parts[1]
    page = int(parts[2]) if len(parts) > 2 else 0
    await check_otp_logic(callback_query, phone, page)

@router.message(Command("list_accounts"))
async def list_accounts_handler(message: Message, state: FSMContext):
    await state.clear()
    accounts = await get_all_accounts(user_id=message.from_user.id)
    if not accounts:
        await message.answer("📭 <b>ɴᴏ sᴀᴠᴇᴅ ᴛᴇʟᴇɢʀᴀᴍ ᴀᴄᴄᴏᴜɴᴛs ꜰᴏᴜɴᴅ ɪɴ ᴛʜᴇ ᴅᴀᴛᴀʙᴀsᴇ.</b>", reply_markup=get_back_keyboard(), parse_mode="HTML")
        return

    await message.answer(
        "📋 <b>sᴇʟᴇᴄᴛ ᴀɴ ᴀᴄᴄᴏᴜɴᴛ ꜰʀᴏᴍ ᴛʜᴇ ʟɪsᴛ:</b>",
        reply_markup=get_accounts_keyboard(accounts, page=0),
        parse_mode="HTML"
    )

@router.callback_query(F.data.startswith("view_acc:"))
async def view_account_panel(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.answer()
    await state.clear()

    parts = callback_query.data.split(":")
    phone = parts[1]
    page = int(parts[2]) if len(parts) > 2 else 0

    acc = await get_account(phone, user_id=callback_query.from_user.id)
    if not acc:
        await callback_query.message.edit_text("❌ <b>sᴇʟᴇᴄᴛᴇᴅ ᴀᴄᴄᴏᴜɴᴛ ɴᴏ ʟᴏɴɢᴇʀ ᴇxɪsᴛs.</b>", reply_markup=get_back_keyboard(), parse_mode="HTML")
        return

    p_name = acc.get("profile_name") or "ᴜɴᴋɴᴏᴡɴ"

    panel_keyboard = [
        [
            InlineKeyboardButton(text="📁 ᴅᴇᴛᴀɪʟs", callback_data=f"acc_opt:details:{phone}:{page}"),
            InlineKeyboardButton(text="✔️ ᴠᴇʀɪꜰʏ", callback_data=f"acc_opt:verify:{phone}:{page}")
        ],
        [
            InlineKeyboardButton(text="✉️ sᴇɴᴅ", callback_data=f"acc_opt:send:{phone}:{page}"),
            InlineKeyboardButton(text="📩 ᴏᴛᴘ ᴄᴏᴅᴇs", callback_data=f"acc_opt:otp:{phone}:{page}")
        ],
        [
            InlineKeyboardButton(text="🔑 ᴇxᴛʀᴀᴄᴛ", callback_data=f"acc_opt:extract:{phone}:{page}"),
            InlineKeyboardButton(text="💾 ᴇxᴘᴏʀᴛ sǫʟɪᴛᴇ", callback_data=f"acc_opt:export:{phone}:{page}")
        ],
        [
            InlineKeyboardButton(text="🔐 sᴇᴄᴜʀɪᴛʏ", callback_data=f"acc_opt:security:{phone}:{page}")
        ],
        [
            InlineKeyboardButton(text="🗑️ ᴅᴇʟᴇᴛᴇ", callback_data=f"acc_opt:delete:{phone}:{page}")
        ],
        [
            InlineKeyboardButton(text="ᴘᴜʙʟɪᴄ ᴄʜᴀɴɴᴇʟs", callback_data=f"acc_opt:pub_chan:{phone}:{page}"),
            InlineKeyboardButton(text="ᴘʀɪᴠᴀᴛᴇ ᴄʜᴀɴɴᴇʟs", callback_data=f"acc_opt:priv_chan:{phone}:{page}")
        ],
        [
            InlineKeyboardButton(text="ɢʀᴏᴜᴘs", callback_data=f"acc_opt:groups:{phone}:{page}"),
            InlineKeyboardButton(text="ᴄʜᴀᴛ sᴛᴀᴛs", callback_data=f"acc_opt:chat_stats:{phone}:{page}")
        ],
        [
            InlineKeyboardButton(text="ᴀᴄᴛɪᴠᴇ ᴅᴇᴠɪᴄᴇs", callback_data=f"acc_opt:devices:{phone}:{page}")
        ],
        [
            InlineKeyboardButton(text="🔙 ʙᴀᴄᴋ ᴛᴏ ʟɪsᴛ", callback_data=f"back_to_list:{page}")
        ]
    ]

    panel_text = (
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "📱 <b>ᴀᴄᴄᴏᴜɴᴛ ᴘᴀɴᴇʟ</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        f"📞 <code>{html.escape(phone)}</code> | ⚙️ <code>{html.escape(p_name)}</code>\n\n"
        "✨ <b>ᴍᴀɴᴀɢᴇ ᴛʜɪs sᴇssɪᴏɴ ᴜsɪɴɢ ᴛʜᴇ ᴄᴏɴᴛʀᴏʟs ʙᴇʟᴏᴡ:</b>"
    )

    await callback_query.message.edit_text(
        panel_text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=panel_keyboard),
        parse_mode="HTML"
    )


@router.callback_query(F.data.startswith("format_sel:"))
async def process_format_selection(callback_query: CallbackQuery):
    await callback_query.answer()

    parts = callback_query.data.split(":")
    format_choice = parts[1]
    action = parts[2]
    phone = parts[3]
    page = int(parts[4]) if len(parts) > 4 else 0

    bot = callback_query.bot

    acc = await get_account(phone, user_id=callback_query.from_user.id)
    if not acc:
        await callback_query.message.edit_text("❌ <b>ᴀᴄᴄᴏᴜɴᴛ ɴᴏ ʟᴏɴɢᴇʀ ᴇxɪsᴛs.</b>", reply_markup=get_back_keyboard(), parse_mode="HTML")
        return

    session_str = decrypt_data(acc["encrypted_session"])
    p_name = acc.get("profile_name") or "ᴜɴᴋɴᴏᴡɴ"

    if action == "extract":
        if format_choice == "telethon":
            out_str = pyrogram_to_telethon(session_str)
            if not out_str:
                out_str = "Error converting to Telethon format."
            title = "Telethon sᴇssɪᴏɴ sᴛʀɪɴɢ:"
        else:
            out_str = session_str
            title = "Pyrogram sᴇssɪᴏɴ sᴛʀɪɴɢ (V2):"

        extract_text = (
            "━━━━━━━━━━━━━━━━━━━━━\n"
            "🔑 <b>sᴇssɪᴏɴ ᴇxᴛʀᴀᴄᴛɪᴏɴ</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━\n"
            f"📱 <b>ᴘʜᴏɴᴇ:</b> <code>{html.escape(phone)}</code>\n"
            f"👤 <b>ᴀᴄᴄᴏᴜɴᴛ:</b> <code>{html.escape(p_name)}</code>\n\n"
            f"👇 <b><b>{title}</b></b>\n"
            f"<code>{html.escape(out_str)}</code>"
        )
        await callback_query.message.edit_text(
            extract_text,
            reply_markup=get_back_to_panel_keyboard(phone, page),
            parse_mode="HTML"
        )
        return

    if action == "export":
        await callback_query.message.edit_text(
            f"⏳ <b>ɢᴇɴᴇʀᴀᴛɪɴɢ sᴇssɪᴏɴ ꜰɪʟᴇ ꜰᴏʀ</b> <code>{html.escape(phone)}</code>... <b>ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ.</b>",
            parse_mode="HTML"
        )

        temp_dir = Path("temp_sessions")
        temp_dir.mkdir(exist_ok=True)
        name_clean = phone.replace("+", "")
        file_path = None

        try:
            if format_choice == "telethon":
                out_path_str = generate_telethon_sqlite(session_str, name_clean, temp_dir)
                if not out_path_str:
                    raise ValueError("Failed to generate Telethon sqlite file.")
                file_path = Path(out_path_str)
            else:
                file_path = await save_session_string_to_file(session_str, name_clean, temp_dir)

            if file_path and file_path.exists():
                await bot.send_document(
                    chat_id=callback_query.message.chat.id,
                    document=FSInputFile(str(file_path)),
                    caption=f"✅ <b>sᴇssɪᴏɴ ᴇxᴘᴏʀᴛᴇᴅ sᴜᴄᴄᴇssꜰᴜʟʟʏ!</b>\n\n📱 <b>ᴘʜᴏɴᴇ:</b> <code>{html.escape(phone)}</code>",
                    parse_mode="HTML"
                )
                await callback_query.message.edit_text(
                    f"✅ <b>sᴇssɪᴏɴ ꜰɪʟᴇ sᴇɴᴛ sᴜᴄᴄᴇssꜰᴜʟʟʏ!</b>\n\n📱 <b>ᴘʜᴏɴᴇ:</b> <code>{html.escape(phone)}</code>",
                    reply_markup=get_back_to_panel_keyboard(phone, page),
                    parse_mode="HTML"
                )
            else:
                await callback_query.message.edit_text(
                    f"❌ <b>ꜰᴀɪʟᴇᴅ ᴛᴏ ᴇxᴘᴏʀᴛ sᴇssɪᴏɴ:</b> file was not created.",
                    reply_markup=get_back_to_panel_keyboard(phone, page),
                    parse_mode="HTML"
                )
        except Exception as e:
            await callback_query.message.edit_text(
                f"❌ <b>ꜰᴀɪʟᴇᴅ ᴛᴏ ᴇxᴘᴏʀᴛ sᴇssɪᴏɴ:</b> <code>{html.escape(str(e))}</code>",
                reply_markup=get_back_to_panel_keyboard(phone, page),
                parse_mode="HTML"
            )
        finally:
            if file_path and file_path.exists():
                try:
                    os.remove(file_path)
                except Exception:
                    pass
        return

@router.callback_query(F.data.startswith("acc_opt:"))
async def process_account_options(callback_query: CallbackQuery, state: FSMContext):
    # Instantly answer the callback query to stop the button loader spinning circle immediately!
    await callback_query.answer()

    bot = callback_query.bot
    parts = callback_query.data.split(":")
    action = parts[1]
    phone = parts[2]
    page = int(parts[3]) if len(parts) > 3 else 0

    acc = await get_account(phone, user_id=callback_query.from_user.id)
    if not acc:
        await callback_query.message.edit_text("❌ <b>ᴀᴄᴄᴏᴜɴᴛ ɴᴏ ʟᴏɴɢᴇʀ ᴇxɪsᴛs.</b>", reply_markup=get_back_keyboard(), parse_mode="HTML")
        return

    # Handle delete option
    if action == "delete":
        confirm_kbd = [
            [
                InlineKeyboardButton(text="✅ ʏᴇs, ᴅᴇʟᴇᴛᴇ", callback_data=f"confirm_del:{phone}:{page}"),
                InlineKeyboardButton(text="❌ ɴᴏ, ᴄᴀɴᴄᴇʟ", callback_data=f"view_acc:{phone}:{page}")
            ]
        ]
        await callback_query.message.edit_text(
            f"⚠️ <b>ᴀʀᴇ ʏᴏᴜ sᴜʀᴇ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ᴅᴇʟᴇᴛᴇ <code>{html.escape(phone)}</code>?</b>\n\n"
            "ᴛʜɪs ᴀᴄᴛɪᴏɴ ɪs ɪʀʀᴇᴠᴇʀsɪʙʟᴇ ᴀɴᴅ ᴛʜᴇ sᴇssɪᴏɴ sᴛʀɪɴɢ ᴡɪʟʟ ʙᴇ ᴘᴇʀᴍᴀɴᴇɴᴛʟʏ ᴡɪᴘᴇᴅ.",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=confirm_kbd),
            parse_mode="HTML"
        )
        return

    # Handle OTP Codes option
    if action == "otp":
        await check_otp_logic(callback_query, phone, page)
        return

    # Handle Send option
    if action == "send":
        await state.update_data(phone=phone, page=page)
        await callback_query.message.edit_text(
            "✉️ <b>[sᴇɴᴅ ᴍᴇssᴀɢᴇ] sᴛᴇᴘ 1/2</b>\n\n"
            "👉 ᴘʟᴇᴀsᴇ sᴇɴᴅ ᴛʜᴇ <b>ᴜsᴇʀ ɪᴅ, ᴜsᴇʀɴᴀᴍᴇ, ᴏʀ ᴛ.ᴍᴇ ʟɪɴᴋ</b> of the target recipient:\n\n"
            "👉 ᴘʀᴇss ᴄᴀɴᴄᴇʟ ʙᴜᴛᴛᴏɴ ʙᴇʟᴏᴡ ᴛᴏ ᴀʙᴏʀᴛ.",
            reply_markup=get_back_to_panel_keyboard(phone, page),
            parse_mode="HTML"
        )
        await state.set_state(SendStates.waiting_for_target)
        return

    # Handle Details option
    if action == "details":
        await callback_query.message.edit_text(
            f"⏳ <b>ꜰᴇᴛᴄʜɪɴɢ ᴀᴄᴄᴏᴜɴᴛ ᴅᴇᴛᴀɪʟs ꜰᴏʀ</b> <code>{html.escape(phone)}</code>... <b>ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ.</b>",
            parse_mode="HTML"
        )

        session_str = decrypt_data(acc["encrypted_session"])
        proxy = acc.get("proxy")
        custom_api = acc.get("custom_api")

        client = create_pyrogram_client(f"det_{phone.replace('+', '')}", session_str, proxy, custom_api)
        try:
            await client.connect()
            me = await client.get_me()

            # Estimate Account Creation Date and Age
            creation_date, account_age = estimate_account_age(me.id)

            # Fetch 2FA Status / Hint
            two_fa_status = "ᴅɪsᴀʙʟᴇᴅ ❌"
            hint_str = "ɴᴏɴᴇ"
            try:
                hint = await client.get_password_hint()
                if hint is not None:
                    two_fa_status = "ᴇɴᴀʙʟᴇᴅ 🔐"
                    hint_str = f"<code>{html.escape(hint)}</code>" if hint else "ᴇᴍᴘᴛʏ"
            except Exception:
                pass

            p_name = " ".join([p for p in [me.first_name or "", me.last_name or ""] if p.strip()]) or "ᴜɴᴋɴᴏᴡɴ"
            username = f"@{me.username}" if me.username else "ɴᴏɴᴇ"
            proxy_info = f"<code>{html.escape(proxy['hostname'])}:{proxy['port']}</code>" if proxy else "ᴅɪʀᴇᴄᴛ ᴄᴏɴɴᴇᴄᴛɪᴏɴ"

            # Map Trust/Verification Fields
            premium_status = "✅" if getattr(me, "is_premium", False) else "✖️"
            restricted_status = "✅" if getattr(me, "is_restricted", False) else "✖️"
            bot_status = "Yes" if getattr(me, "is_bot", False) else "No"

            if getattr(me, "is_scam", False):
                trust_status = "❌ Scam"
            elif getattr(me, "is_fake", False):
                trust_status = "⚠️ Fake"
            else:
                trust_status = "✅ Clean"

            premium_status = make_small_caps(premium_status)
            restricted_status = make_small_caps(restricted_status)
            bot_status = make_small_caps(bot_status)
            trust_status = make_small_caps(trust_status)

            details_text = (
                "━━━━━━━━━━━━━━━━━━━━━\n"
                "📋 <b>ᴀᴄᴄᴏᴜɴᴛ ᴅᴇᴛᴀɪʟs</b>\n"
                "━━━━━━━━━━━━━━━━━━━━━\n"
                f"👤 <b>ɴᴀᴍᴇ:</b> <code>{html.escape(p_name)}</code>\n"
                f"📞 <b>ᴘʜᴏɴᴇ:</b> <code>{html.escape(phone)}</code>\n"
                f"🆔 <b>ᴜsᴇʀ ɪᴅ:</b> <code>{me.id}</code>\n"
                f"📅 <b><b>ᴄʀᴇᴀᴛɪᴏɴ ᴅᴀᴛᴇ:</b></b> {creation_date}\n"
                f"⏳ <b><b>ᴀᴄᴄᴏᴜɴᴛ ᴀɢᴇ:</b></b> {account_age}\n"
                f"💠 <b><b>ᴘʀᴇᴍɪᴜᴍ:</b></b> {premium_status}\n"
                f"🚫 <b><b>ʀᴇsᴛʀɪᴄᴛᴇᴅ:</b></b> {restricted_status}\n"
                f"🤖 <b><b>ʙᴏᴛ:</b></b> {bot_status}\n"
                f"🛡️ <b><b>ᴛʀᴜsᴛ:</b></b> {trust_status}\n"
                f"🏷️ <b><b>ᴜsᴇʀɴᴀᴍᴇ:</b></b> <code>{html.escape(username)}</code>\n"
                f"🌐 <b><b>ᴅᴄ ɪᴅ:</b></b> <code>{me.dc_id}</code>\n"
                f"🔐 <b>2ꜰᴀ sᴛᴀᴛᴜs:</b> {two_fa_status}\n"
                f"📝 <b>2ꜰᴀ ʜɪɴᴛ:</b> {hint_str}\n"
                f"🌐 <b>ᴘʀᴏxʏ:</b> {proxy_info}\n\n"
                "✨ <b>ᴍᴀɴᴀɢᴇ ᴛʜɪs sᴇssɪᴏɴ ᴜsɪɴɢ ᴛʜᴇ ᴄᴏɴᴛʀᴏʟs ʙᴇʟᴏᴡ:</b>"
            )

            await callback_query.message.edit_text(
                details_text,
                reply_markup=get_back_to_panel_keyboard(phone, page),
                parse_mode="HTML"
            )
        except AuthKeyInvalid:
            await callback_query.message.edit_text(
                f"❌ <b>sᴇssɪᴏɴ ɪs ɪɴᴠᴀʟɪᴅ / ᴇxᴘɪʀᴇᴅ</b> ꜰᴏʀ <code>{html.escape(phone)}</code>.",
                reply_markup=get_back_to_panel_keyboard(phone, page),
                parse_mode="HTML"
            )
        except Exception as e:
            await callback_query.message.edit_text(
                f"❌ <b>ꜰᴀɪʟᴇᴅ ᴛᴏ ꜰᴇᴛᴄʜ ᴅᴇᴛᴀɪʟs:</b> <code>{html.escape(str(e))}</code>",
                reply_markup=get_back_to_panel_keyboard(phone, page),
                parse_mode="HTML"
            )
        finally:
            try:
                if client.is_connected:
                    await client.disconnect()
            except Exception:
                pass
        return

    # Handle Verify option
    if action == "verify":
        await callback_query.message.edit_text(
            f"⏳ <b><b>ᴠᴇʀɪꜰʏɪɴɢ sᴇssɪᴏɴ status ꜰᴏʀ</b></b> <code>{html.escape(phone)}</code>... <b>ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ.</b>",
            parse_mode="HTML"
        )

        session_str = decrypt_data(acc["encrypted_session"])
        proxy = acc.get("proxy")
        custom_api = acc.get("custom_api")

        client = create_pyrogram_client(f"ver_{phone.replace('+', '')}", session_str, proxy, custom_api)
        try:
            await client.connect()
            me = await client.get_me()
            p_name = " ".join([p for p in [me.first_name or "", me.last_name or ""] if p.strip()]) or "ᴜɴᴋɴᴏᴡɴ"

            # Save the latest profile name to database
            await save_account(
                phone=phone,
                encrypted_session=acc["encrypted_session"],
                user_id=callback_query.from_user.id,
                proxy=proxy,
                custom_api=custom_api,
                profile_name=p_name
            )

            await callback_query.message.edit_text(
                f"✅ <b>sᴇssɪᴏɴ ᴠᴇʀɪꜰɪᴇᴅ!</b>\n\n"
                f"📱 <b>ᴘʜᴏɴᴇ:</b> <code>{html.escape(phone)}</code>\n"
                f"👤 <b>ɴᴀᴍᴇ:</b> <code>{html.escape(p_name)}</code>\n"
                f"🟢 <b>sᴛᴀᴛᴜs:</b> <b>ᴀᴄᴛɪᴠᴇ &amp; ᴠᴇʀɪꜰɪᴇᴅ</b> on ᴛᴇʟᴇɢʀᴀᴍ sᴇʀᴠᴇʀs.",
                reply_markup=get_back_to_panel_keyboard(phone, page),
                parse_mode="HTML"
            )
        except AuthKeyInvalid:
            await callback_query.message.edit_text(
                f"❌ <b>sᴇssɪᴏɴ ᴇxᴘɪʀᴇᴅ / ɪɴᴠᴀʟɪᴅ!</b>\n\n"
                f"📱 <b>ᴘʜᴏɴᴇ:</b> <code>{html.escape(phone)}</code>\n"
                f"🔴 <b>sᴛᴀᴛᴜs:</b> <b>ᴇxᴘɪʀᴇᴅ ᴏʀ ᴛᴇʀᴍɪɴᴀᴛᴇᴅ</b> by ᴜsᴇʀ.",
                reply_markup=get_back_to_panel_keyboard(phone, page),
                parse_mode="HTML"
            )
        except Exception as e:
            await callback_query.message.edit_text(
                f"❌ <b>ᴠᴇʀɪꜰɪᴄᴀᴛɪᴏɴ ꜰᴀɪʟᴇᴅ:</b> <code>{html.escape(str(e))}</code>",
                reply_markup=get_back_to_panel_keyboard(phone, page),
                parse_mode="HTML"
            )
        finally:
            try:
                if client.is_connected:
                    await client.disconnect()
            except Exception:
                pass
        return

    # Handle Extract option
    if action == "extract":
        format_kbd = [
            [InlineKeyboardButton(text="[ ᴘʏʀᴏɢʀᴀᴍ ]", callback_data=f"format_sel:pyrogram:extract:{phone}:{page}")],
            [InlineKeyboardButton(text="[ ᴛᴇʟᴇᴛʜᴏɴ ]", callback_data=f"format_sel:telethon:extract:{phone}:{page}")],
            [InlineKeyboardButton(text="🔙 ʙᴀᴄᴋ", callback_data=f"view_acc:{phone}:{page}")]
        ]
        await callback_query.message.edit_text(
            "🗂 <b>Choose the session format for export:</b>",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=format_kbd),
            parse_mode="HTML"
        )
        return

    # Handle Export SQLite option
    if action == "export":
        format_kbd = [
            [InlineKeyboardButton(text="[ ᴘʏʀᴏɢʀᴀᴍ ]", callback_data=f"format_sel:pyrogram:export:{phone}:{page}")],
            [InlineKeyboardButton(text="[ ᴛᴇʟᴇᴛʜᴏɴ ]", callback_data=f"format_sel:telethon:export:{phone}:{page}")],
            [InlineKeyboardButton(text="🔙 ʙᴀᴄᴋ", callback_data=f"view_acc:{phone}:{page}")]
        ]
        await callback_query.message.edit_text(
            "🗂 <b>Choose the session format for export:</b>",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=format_kbd),
            parse_mode="HTML"
        )
        return

    # Handle Security option
    if action == "security":
        p_name = acc.get("profile_name") or "ᴜɴᴋɴᴏᴡɴ"

        sec_kbd = [
            [
                InlineKeyboardButton(text="🆕 sᴇᴛ / ᴄʜᴀɴɢᴇ 2ꜰᴀ", callback_data=f"sec_opt:set_2fa:{phone}:{page}"),
                InlineKeyboardButton(text="❌ ʀᴇᴍᴏᴠᴇ 2ꜰᴀ", callback_data=f"sec_opt:remove_2fa:{phone}:{page}")
            ],
            [
                InlineKeyboardButton(text="💻 ᴠɪᴇᴡ sᴇssɪᴏɴs", callback_data=f"sec_opt:view_sessions:{phone}:{page}"),
                InlineKeyboardButton(text="✏️ ʀᴇɴᴀᴍᴇ ᴘʀᴏꜰɪʟᴇ", callback_data=f"sec_opt:rename_profile:{phone}:{page}")
            ],
            [
                InlineKeyboardButton(text="🔙 ʙᴀᴄᴋ ᴛᴏ ᴘᴀɴᴇʟ", callback_data=f"view_acc:{phone}:{page}")
            ]
        ]

        await callback_query.message.edit_text(
            "━━━━━━━━━━━━━━━━━━━━━\n"
            "🔐 <b>sᴇᴄᴜʀɪᴛʏ sᴇᴛᴛɪɴɢs</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━\n"
            f"📱 <b>ᴀᴄᴄᴏᴜɴᴛ:</b> <code>{html.escape(phone)}</code> | <code>{html.escape(p_name)}</code>\n\n"
            "👉 <b><b>ᴄʜᴏᴏsᴇ ᴀɴ ᴀᴄᴛɪᴏɴ ʙᴇʟᴏᴡ:</b></b>",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=sec_kbd),
            parse_mode="HTML"
        )
        return

@router.message(SendStates.waiting_for_target)
async def process_send_target(message: Message, state: FSMContext):
    if not message.text:
        await message.answer("⚠️ <b>ᴘʟᴇᴀsᴇ sᴇɴᴅ ᴀ ᴠᴀʟɪᴅ ᴛᴀʀɢᴇᴛ ɪᴅ ᴏʀ ᴜsᴇʀɴᴀᴍᴇ.</b>", parse_mode="HTML")
        return

    target_raw = message.text.strip()
    target = target_raw
    if "/" in target:
        target = target.split("/")[-1]
    if not target.startswith("@") and not target.isdigit() and not target.startswith("+"):
        target = f"@{target}"

    await state.update_data(target=target)
    data = await state.get_data()
    phone = data.get("phone")
    page = data.get("page", 0)

    await message.answer(
        "✉️ <b>[sᴇɴᴅ ᴍᴇssᴀɢᴇ] sᴛᴇᴘ 2/2</b>\n\n"
        f"👤 <b>ᴛᴀʀɢᴇᴛ:</b> <code>{html.escape(target)}</code>\n\n"
        "👉 <b><b>ᴘʟᴇᴀsᴇ sᴇɴᴅ ᴛʜᴇ ᴍᴇssᴀɢᴇ ᴛᴇxᴛ</b> you want to send below:</b>\n\n"
        "👉 ᴘʀᴇss ᴄᴀɴᴄᴇʟ ʙᴜᴛᴛᴏɴ ʙᴇʟᴏᴡ ᴛᴏ ᴀʙᴏʀᴛ.",
        reply_markup=get_back_to_panel_keyboard(phone, page),
        parse_mode="HTML"
    )
    await state.set_state(SendStates.waiting_for_message)

@router.message(SendStates.waiting_for_message)
async def process_send_message(message: Message, state: FSMContext):
    if not message.text:
        await message.answer("⚠️ <b>ᴘʟᴇᴀsᴇ sᴇɴᴅ ᴀ ᴠᴀʟɪᴅ ᴛᴇxᴛ ᴍᴇssᴀɢᴇ.</b>", parse_mode="HTML")
        return

    msg_text = message.text.strip()
    data = await state.get_data()
    phone = data.get("phone")
    target = data.get("target")
    page = data.get("page", 0)

    await state.clear()

    acc = await get_account(phone, user_id=message.from_user.id)
    if not acc:
        await message.answer("❌ <b>ᴀᴄᴄᴏᴜɴᴛ ɴᴏ ʟᴏɴɢᴇʀ ᴇxɪsᴛs.</b>", reply_markup=get_back_keyboard(), parse_mode="HTML")
        return

    session_str = decrypt_data(acc["encrypted_session"])
    proxy = acc.get("proxy")
    custom_api = acc.get("custom_api")

    status_msg = await message.answer("⏳ <b><b>ᴄᴏɴɴᴇᴄᴛɪɴɢ ᴛᴏ ᴛᴇʟᴇɢʀᴀᴍ sᴇʀᴠᴇʀs &amp; sᴇɴᴅɪɴɢ...</b></b>", parse_mode="HTML")
    client = create_pyrogram_client(f"snd_{phone.replace('+', '')}", session_str, proxy, custom_api)

    try:
        await client.connect()
        resolved_target = int(target) if target.isdigit() else target

        await client.send_message(chat_id=resolved_target, text=msg_text)
        await status_msg.edit_text(
            f"✅ <b><b>ᴍᴇssᴀɢᴇ sᴇɴᴛ sᴜᴄᴄᴇssꜰᴜʟʟʏ!</b></b>\n\n"
            f"📱 <b>sᴇɴᴅᴇʀ:</b> <code>{html.escape(phone)}</code>\n"
            f"👤 <b>ʀᴇᴄɪᴘɪᴇɴᴛ:</b> <code>{html.escape(str(target))}</code>\n"
            f"📝 <b>ᴍᴇssᴀɢᴇ:</b> <code>{html.escape(msg_text)}</code>",
            reply_markup=get_back_to_panel_keyboard(phone, page),
            parse_mode="HTML"
        )
    except Exception as e:
        await status_msg.edit_text(
            f"❌ <b>ꜰᴀɪʟᴇᴅ ᴛᴏ sᴇᴛ ᴍᴇssᴀɢᴇ:</b> <code>{html.escape(str(e))}</code>",
            reply_markup=get_back_to_panel_keyboard(phone, page),
            parse_mode="HTML"
        )
    finally:
        try:
            if client.is_connected:
                await client.disconnect()
        except Exception:
            pass

@router.callback_query(F.data.startswith("sec_opt:"))
async def process_security_options(callback_query: CallbackQuery, state: FSMContext):
    # Instantly answer callback query to stop the button spinning circle immediately!
    await callback_query.answer()

    parts = callback_query.data.split(":")
    sec_action = parts[1]
    phone = parts[2]
    page = int(parts[3]) if len(parts) > 3 else 0

    if sec_action == "set_2fa":
        await state.update_data(phone=phone, page=page)
        await callback_query.message.edit_text(
            "🆕 <b>[sᴇᴄᴜʀɪᴛʏ] sᴇᴛ / ᴄʜᴀɴɢᴇ 2ꜰᴀ ᴘᴀssᴡᴏʀᴅ</b>\n\n"
            "👉 <b>ᴘʟᴇᴀsᴇ sᴇɴᴅ ʏᴏᴜʀ ɴᴇᴡ ᴄʟᴏᴜᴅ ᴘᴀssᴡᴏʀᴅ ʙᴇʟᴏᴡ.</b>\n\n"
            "⚠️ <b>ɪꜰ 2ꜰᴀ ɪs ᴀʟʀᴇᴀᴅʏ ᴇɴᴀʙʟᴇᴅ</b>, sᴇɴᴅ ʙᴏᴛʜ ᴛʜᴇ ᴄᴜʀʀᴇɴᴛ ᴀɴᴅ ɴᴇᴡ ᴘᴀssᴡᴏʀᴅ ɪɴ ᴛʜɪs ꜰᴏʀᴍᴀᴛ:\n"
            "<code>ᴄᴜʀʀᴇɴᴛ_ᴘᴀssᴡᴏʀᴅ:ɴᴇᴡ_ᴘᴀssᴡᴏʀᴅ</code>\n\n"
            "<i>ᴇxᴀᴍᴘʟᴇ:</i> <code>ᴍʏᴏʟᴅᴘᴀss123:ᴍʏɴᴇᴡᴘᴀss456</code>\n\n"
            "👉 ᴘʀᴇss ᴄᴀɴᴄᴇʟ ʙᴜᴛᴛᴏɴ ʙᴇʟᴏᴡ ᴛᴏ ᴀʙᴏʀᴛ.",
            reply_markup=get_back_to_panel_keyboard(phone, page),
            parse_mode="HTML"
        )
        await state.set_state(SecurityStates.waiting_for_new_2fa)
        return

    if sec_action == "remove_2fa":
        await state.update_data(phone=phone, page=page)
        await callback_query.message.edit_text(
            "❌ <b>[sᴇᴄᴜʀɪᴛʏ] ʀᴇᴍᴏᴠᴇ 2ꜰᴀ ᴘᴀssᴡᴏʀᴅ</b>\n\n"
            "👉 <b>ᴘʟᴇᴀsᴇ sᴇɴᴅ ʏᴏᴜʀ ᴄᴜʀʀᴇɴᴛ ᴄʟᴏᴜᴅ ᴘᴀssᴡᴏʀᴅ ʙᴇʟᴏᴡ</b> ᴛᴏ ᴅɪsᴀʙʟᴇ 2ꜰᴀ ᴄᴏᴍᴘʟᴇᴛᴇʟʏ:\n\n"
            "👉 ᴘʀᴇss ᴄᴀɴᴄᴇʟ ʙᴜᴛᴛᴏɴ ʙᴇʟᴏᴡ ᴛᴏ ᴀʙᴏʀᴛ.",
            reply_markup=get_back_to_panel_keyboard(phone, page),
            parse_mode="HTML"
        )
        await state.set_state(SecurityStates.waiting_for_remove_2fa)
        return

    if sec_action == "view_sessions":
        await callback_query.message.edit_text(
            f"⏳ <b>ꜰᴇᴛᴄʜɪɴɢ ᴀᴄᴛɪᴠᴇ sᴇssɪᴏɴs ꜰᴏʀ</b> <code>{html.escape(phone)}</code>... <b>ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ.</b>",
            parse_mode="HTML"
        )

        acc = await get_account(phone, user_id=callback_query.from_user.id)
        session_str = decrypt_data(acc["encrypted_session"])
        proxy = acc.get("proxy")
        custom_api = acc.get("custom_api")

        client = create_pyrogram_client(f"sess_{phone.replace('+', '')}", session_str, proxy, custom_api)
        try:
            await client.connect()
            authorizations_obj = await client.invoke(raw.functions.account.GetAuthorizations())
            authorizations = authorizations_obj.authorizations

            sessions_text = (
                "━━━━━━━━━━━━━━━━━━━━━\n"
                "💻 <b>ᴀᴄᴛɪᴠᴇ sᴇssɪᴏɴs</b>\n"
                "━━━━━━━━━━━━━━━━━━━━━\n"
                f"📱 <b>ᴀᴄᴄᴏᴜɴᴛ:</b> <code>{html.escape(phone)}</code>\n\n"
            )

            sess_buttons = []
            for i, auth in enumerate(authorizations, 1):
                device = auth.device_model or "ᴜɴᴋɴᴏᴡɴ ᴅᴇᴠɪᴄᴇ"
                platform = auth.platform or "ᴜɴᴋɴᴏᴡɴ ᴘʟᴀᴛꜰᴏʀᴍ"
                app_name = auth.app_name or "ᴜɴᴋɴᴏᴡɴ ᴀᴘᴘ"
                ip_addr = auth.ip or "0.0.0.0"
                country = auth.country or "ᴜɴᴋɴᴏᴡɴ"
                created_dt = datetime.fromtimestamp(auth.date_created).strftime("%Y-%m-%d %H:%M")

                status_label = "🟢 CURRENT" if auth.current else "⚪ ACTIVE"

                sessions_text += (
                    f"<b>{i}. {html.escape(device)} ({html.escape(platform)})</b>\n"
                    f"👉 <b>ᴀᴘᴘ:</b> {html.escape(app_name)}\n"
                    f"👉 <b>ɪᴘ:</b> <code>{html.escape(ip_addr)}</code> ({html.escape(country)})\n"
                    f"👉 <b><b>ᴄʀᴇᴀᴛᴇᴅ:</b></b> <code>{created_dt}</code>\n"
                    f"⚡ <b>sᴛᴀᴛᴜs:</b> {status_label}\n\n"
                )

                if not auth.current:
                    sess_buttons.append([
                        InlineKeyboardButton(
                            text=f"🗑️ ʀᴇᴠᴏᴋᴇ: {device} | {country}",
                            callback_data=f"revoke_sess:{phone}:{auth.hash}:{page}"
                        )
                    ])

            sess_buttons.append([InlineKeyboardButton(text="🔙 ʙᴀᴄᴋ ᴛᴏ sᴇᴄᴜʀɪᴛʏ", callback_data=f"acc_opt:security:{phone}:{page}")])

            await callback_query.message.edit_text(
                sessions_text,
                reply_markup=InlineKeyboardMarkup(inline_keyboard=sess_buttons),
                parse_mode="HTML"
            )
        except Exception as e:
            await callback_query.message.edit_text(
                f"❌ <b><b>ꜰᴀɪʟᴇᴅ ᴛᴏ ꜰᴇᴛᴄʜ sᴇssɪᴏɴs:</b></b> <code>{html.escape(str(e))}</code>",
                reply_markup=get_back_to_panel_keyboard(phone, page),
                parse_mode="HTML"
            )
        finally:
            try:
                if client.is_connected:
                    await client.disconnect()
            except Exception:
                pass
        return

    if sec_action == "rename_profile":
        await state.update_data(phone=phone, page=page)
        await callback_query.message.edit_text(
            "✏️ <b>[sᴇᴄᴜʀɪᴛʏ] ʀᴇɴᴀᴍᴇ ᴘʀᴏꜰɪʟᴇ</b>\n\n"
            "👉 <b><b>ᴘʟᴇᴀsᴇ sᴇɴᴅ ᴛʜᴇ ɴᴇᴡ ᴘʀᴏꜰɪʟᴇ ɴᴀᴍᴇ below:</b></b>\n\n"
            "👉 ᴘʀᴇss ᴄᴀɴᴄᴇʟ ʙᴜᴛᴛᴏɴ ʙᴇʟᴏᴡ ᴛᴏ ᴀʙᴏʀᴛ.",
            reply_markup=get_back_to_panel_keyboard(phone, page),
            parse_mode="HTML"
        )
        await state.set_state(SecurityStates.waiting_for_new_name)
        return

@router.callback_query(F.data.startswith("revoke_sess:"))
async def process_revoke_session_prompt(callback_query: CallbackQuery):
    await callback_query.answer()

    parts = callback_query.data.split(":")
    phone = parts[1]
    sess_hash = parts[2]
    page = int(parts[3]) if len(parts) > 3 else 0

    confirm_kbd = [
        [
            InlineKeyboardButton(text="✅ ʏᴇs, ʀᴇᴠᴏᴋᴇ", callback_data=f"confirm_rev:{phone}:{sess_hash}:{page}"),
            InlineKeyboardButton(text="❌ ɴᴏ, ᴄᴀɴᴄᴇʟ", callback_data=f"sec_opt:view_sessions:{phone}:{page}")
        ]
    ]

    await callback_query.message.edit_text(
        f"⚠️ <b>ᴀʀᴇ ʏᴏᴜ sᴜʀᴇ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ʀᴇᴠᴏᴋᴇ ᴛʜɪs sᴇssɪᴏɴ?</b>\n\n"
        "ᴛʜɪs ᴀᴄᴛɪᴏɴ ᴡɪʟʟ ɪɴsᴛᴀɴᴛʟʏ terminate and log out the selected device.",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=confirm_kbd),
        parse_mode="HTML"
    )

@router.callback_query(F.data.startswith("confirm_rev:"))
async def process_confirm_revoke_session(callback_query: CallbackQuery):
    await callback_query.answer()

    parts = callback_query.data.split(":")
    phone = parts[1]
    sess_hash = int(parts[2])
    page = int(parts[3]) if len(parts) > 3 else 0

    await callback_query.message.edit_text(
        f"⏳ <b>ʀᴇᴠᴏᴋɪɴɢ sᴇssɪᴏɴ... ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ.</b>",
        parse_mode="HTML"
    )

    acc = await get_account(phone, user_id=callback_query.from_user.id)
    session_str = decrypt_data(acc["encrypted_session"])
    proxy = acc.get("proxy")
    custom_api = acc.get("custom_api")

    client = create_pyrogram_client(f"rev_{phone.replace('+', '')}", session_str, proxy, custom_api)
    try:
        await client.connect()
        await client.invoke(raw.functions.account.ResetAuthorization(hash=sess_hash))

        await callback_query.message.edit_text(
            f"✅ <b>sᴇssɪᴏɴ ʀᴇᴠᴏᴋᴇᴅ sᴜᴄᴄᴇssꜰᴜʟʟʏ!</b>",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔙 ʙᴀᴄᴋ ᴛᴏ sᴇssɪᴏɴs ʟɪsᴛ", callback_data=f"sec_opt:view_sessions:{phone}:{page}")]
            ]),
            parse_mode="HTML"
        )
    except Exception as e:
        await callback_query.message.edit_text(
            f"❌ <b><b>ꜰᴀɪʟᴇᴅ ᴛᴏ ʀᴇᴠᴏᴋᴇ sᴇssɪᴏɴ:</b></b> <code>{html.escape(str(e))}</code>",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔙 ʙᴀᴄᴋ ᴛᴏ sᴇssɪᴏɴs ʟɪsᴛ", callback_data=f"sec_opt:view_sessions:{phone}:{page}")]
            ]),
            parse_mode="HTML"
        )
    finally:
        try:
            if client.is_connected:
                await client.disconnect()
        except Exception:
            pass

@router.message(SecurityStates.waiting_for_new_name)
async def process_new_profile_name(message: Message, state: FSMContext):
    if not message.text:
        await message.answer("⚠️ <b>ᴘʟᴇᴀsᴇ sᴇɴᴅ ᴀ ᴠᴀʟɪᴅ ɴᴀᴍᴇ.</b>", parse_mode="HTML")
        return

    new_name = message.text.strip()
    data = await state.get_data()
    phone = data.get("phone")
    page = data.get("page", 0)

    await state.clear()

    acc = await get_account(phone, user_id=message.from_user.id)
    if not acc:
        await message.answer("❌ <b>ᴀᴄᴄᴏᴜɴᴛ ɴᴏ ʟᴏɴɢᴇʀ ᴇxɪsᴛs.</b>", reply_markup=get_back_keyboard(), parse_mode="HTML")
        return

    session_str = decrypt_data(acc["encrypted_session"])
    proxy = acc.get("proxy")
    custom_api = acc.get("custom_api")

    status_msg = await message.answer("⏳ <b><b><b><b>ᴄᴏɴɴᴇᴄᴛɪɴɢ ᴛᴏ ᴛᴇʟᴇɢʀᴀᴍ sᴇʀᴠᴇʀs &amp; ᴜᴘᴅᴀᴛɪɴɢ...</b></b></b></b>", parse_mode="HTML")
    client = create_pyrogram_client(f"ren_{phone.replace('+', '')}", session_str, proxy, custom_api)

    try:
        await client.connect()
        name_parts = new_name.split(" ", 1)
        first_n = name_parts[0]
        last_n = name_parts[1] if len(name_parts) > 1 else ""

        await client.update_profile(first_name=first_n, last_name=last_n)

        # Save to database
        await save_account(
            phone=phone,
            encrypted_session=acc["encrypted_session"],
            user_id=message.from_user.id,
            proxy=proxy,
            custom_api=custom_api,
            profile_name=new_name
        )

        await status_msg.edit_text(
            f"✅ <b>ᴘʀᴏꜰɪʟᴇ ʀᴇɴᴀᴍᴇᴅ sᴜᴄᴄᴇssꜰᴜʟʟʏ!</b>\n\n"
            f"📱 <b>ᴘʜᴏɴᴇ:</b> <code>{html.escape(phone)}</code>\n"
            f"👤 <b>ɴᴇᴡ ɴᴀᴍᴇ:</b> <code>{html.escape(new_name)}</code>",
            reply_markup=get_back_to_panel_keyboard(phone, page),
            parse_mode="HTML"
        )
    except Exception as e:
        await status_msg.edit_text(
            f"❌ <b><b><b>ꜰᴀɪʟᴇᴅ ᴛᴏ ʀᴇɴᴀᴍᴇ ᴘʀᴏꜰɪʟᴇ:</b></b></b> <code>{html.escape(str(e))}</code>",
            reply_markup=get_back_to_panel_keyboard(phone, page),
            parse_mode="HTML"
        )
    finally:
        try:
            if client.is_connected:
                await client.disconnect()
        except Exception:
            pass

@router.message(SecurityStates.waiting_for_new_2fa)
async def process_set_2fa_text(message: Message, state: FSMContext):
    if not message.text:
        await message.answer("⚠️ <b>ᴘʟᴇᴀsᴇ sᴇɴᴅ ᴀ ᴠᴀʟɪᴅ ᴛᴇxᴛ ᴘᴀssᴡᴏʀᴅ.</b>", parse_mode="HTML")
        return
    data = await state.get_data()
    phone = data.get("phone")
    page = data.get("page", 0)
    text = message.text.strip()

    await state.clear()

    acc = await get_account(phone, user_id=message.from_user.id)
    if not acc:
        await message.answer("❌ <b>ᴀᴄᴄᴏᴜɴᴛ ɴᴏ ʟᴏɴɢᴇʀ ᴇxɪsᴛs.</b>", reply_markup=get_back_keyboard(), parse_mode="HTML")
        return

    session_str = decrypt_data(acc["encrypted_session"])
    proxy = acc.get("proxy")
    custom_api = acc.get("custom_api")

    status_msg = await message.answer("⏳ <b><b>ᴄᴏɴɴᴇᴄᴛɪɴɢ ᴛᴏ ᴛᴇʟᴇɢʀᴀᴍ sᴇʀᴠᴇʀs...</b></b>", parse_mode="HTML")
    client = create_pyrogram_client(f"sec_{phone.replace('+', '')}", session_str, proxy, custom_api)

    try:
        await client.connect()

        if ":" in text:
            parts = text.split(":", 1)
            current_pwd = parts[0].strip()
            new_pwd = parts[1].strip()

            await client.change_cloud_password(current_password=current_pwd, new_password=new_pwd)
            await status_msg.edit_text(
                f"✅ <b>2ꜰᴀ ᴄʟᴏᴜᴅ ᴘᴀssᴡᴏʀᴅ ᴄʜᴀɴɢᴇᴅ sᴜᴄᴄᴇssꜰᴜʟʟʏ!</b>\n\n"
                f"📱 <b>ᴘʜᴏɴᴇ:</b> <code>{html.escape(phone)}</code>\n"
                f"🔒 <b><b>ɴᴇᴡ ᴘᴀssᴡᴏʀᴅ:</b></b> <code>{html.escape(new_pwd)}</code>",
                reply_markup=get_back_to_panel_keyboard(phone, page),
                parse_mode="HTML"
            )
        else:
            new_pwd = text
            try:
                await client.enable_cloud_password(password=new_pwd)
                await status_msg.edit_text(
                    f"✅ <b>2<b><b>ꜰᴀ ᴄʟᴏᴜᴅ ᴘᴀssᴡᴏʀᴅ sᴇᴛ sᴜᴄᴄᴇssꜰᴜʟʟʏ!</b></b></b>\n\n"
                    f"📱 <b>ᴘʜᴏɴᴇ:</b> <code>{html.escape(phone)}</code>\n"
                    f"🔒 <b>ᴘᴀssᴡᴏʀᴅ:</b> <code>{html.escape(new_pwd)}</code>",
                    reply_markup=get_back_to_panel_keyboard(phone, page),
                    parse_mode="HTML"
                )
            except ValueError as val_err:
                if "already" in str(val_err).lower() or "active" in str(val_err).lower():
                    await status_msg.edit_text(
                        f"⚠️ <b>2ꜰᴀ ɪs ᴀʟʀᴇᴀᴅʏ ᴇɴᴀʙʟᴇᴅ</b> on <code>{html.escape(phone)}</code>.\n\n"
                        "👉 ᴘʟᴇᴀsᴇ retry by providing both the current and new password in this format:\n"
                        "<code>ᴄᴜʀʀᴇɴᴛ_ᴘᴀssᴡᴏʀᴅ:ɴᴇᴡ_ᴘᴀssᴡᴏʀᴅ</code>",
                        reply_markup=get_back_to_panel_keyboard(phone, page),
                        parse_mode="HTML"
                    )
                else:
                    raise val_err

    except Exception as e:
        await status_msg.edit_text(
            f"❌ <b>ꜰᴀɪʟᴇᴅ ᴛᴏ sᴇᴛ/ᴄʜᴀɴɢᴇ 2ꜰᴀ:</b> <code>{html.escape(str(e))}</code>",
            reply_markup=get_back_to_panel_keyboard(phone, page),
            parse_mode="HTML"
        )
    finally:
        try:
            if client.is_connected:
                await client.disconnect()
        except Exception:
            pass

@router.message(SecurityStates.waiting_for_remove_2fa)
async def process_remove_2fa_text(message: Message, state: FSMContext):
    if not message.text:
        await message.answer("⚠️ <b>ᴘʟᴇᴀsᴇ sᴇɴᴅ ᴀ ᴠᴀʟɪᴅ ᴛᴇxᴛ ᴘᴀssᴡᴏʀᴅ.</b>", parse_mode="HTML")
        return
    data = await state.get_data()
    phone = data.get("phone")
    page = data.get("page", 0)
    pwd = message.text.strip()

    await state.clear()

    acc = await get_account(phone, user_id=message.from_user.id)
    if not acc:
        await message.answer("❌ <b>ᴀᴄᴄᴏᴜɴᴛ ɴᴏ ʟᴏɴɢᴇʀ ᴇxɪsᴛs.</b>", reply_markup=get_back_keyboard(), parse_mode="HTML")
        return

    session_str = decrypt_data(acc["encrypted_session"])
    proxy = acc.get("proxy")
    custom_api = acc.get("custom_api")

    status_msg = await message.answer("⏳ <b><b>ᴄᴏɴɴᴇᴄᴛɪɴɢ ᴛᴏ ᴛᴇʟᴇɢʀᴀᴍ sᴇʀᴠᴇʀs...</b></b>", parse_mode="HTML")
    client = create_pyrogram_client(f"sec_{phone.replace('+', '')}", session_str, proxy, custom_api)

    try:
        await client.connect()
        await client.remove_cloud_password(password=pwd)
        await status_msg.edit_text(
            f"✅ <b>2ꜰᴀ ᴄʟᴏᴜᴅ ᴘᴀssᴡᴏʀᴅ ʀᴇᴍᴏᴠᴇᴅ sᴜᴄᴄᴇssꜰᴜʟʟʏ!</b>\n\n"
            f"📱 <b>ᴘʜᴏɴᴇ:</b> <code>{html.escape(phone)}</code>\n"
            f"🔓 <b>2<b>ꜰᴀ sᴛᴀᴛᴜs:</b></b> ᴅɪsᴀʙʟᴇᴅ ❌",
            reply_markup=get_back_to_panel_keyboard(phone, page),
            parse_mode="HTML"
        )
    except Exception as e:
        await status_msg.edit_text(
            f"❌ <b>ꜰᴀɪʟᴇᴅ ᴛᴏ ʀᴇᴍᴏᴠᴇ 2ꜰᴀ:</b> <code>{html.escape(str(e))}</code>",
            reply_markup=get_back_to_panel_keyboard(phone, page),
            parse_mode="HTML"
        )
    finally:
        try:
            if client.is_connected:
                await client.disconnect()
        except Exception:
            pass


@router.callback_query(F.data.startswith("bulk_export_prompt:"))
async def bulk_export_prompt_handler(callback_query: CallbackQuery):
    await callback_query.answer()

    parts = callback_query.data.split(":")
    action = parts[1]
    page = int(parts[2]) if len(parts) > 2 else 0

    format_kbd = [
        [InlineKeyboardButton(text="[ ᴘʏʀᴏɢʀᴀᴍ ]", callback_data=f"format_sel_bulk:pyrogram:{action}:{page}")],
        [InlineKeyboardButton(text="[ ᴛᴇʟᴇᴛʜᴏɴ ]", callback_data=f"format_sel_bulk:telethon:{action}:{page}")],
        [InlineKeyboardButton(text="🔙 ʙᴀᴄᴋ", callback_data=f"bulk_export:menu:{page}")]
    ]
    await callback_query.message.edit_text(
        "🗂 <b>Choose the session format for export:</b>",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=format_kbd),
        parse_mode="HTML"
    )

@router.callback_query(F.data.startswith("format_sel_bulk:"))
async def process_bulk_format_selection(callback_query: CallbackQuery):
    await callback_query.answer()

    parts = callback_query.data.split(":")
    format_choice = parts[1]
    action = parts[2]
    page = int(parts[3]) if len(parts) > 3 else 0

    user_id = callback_query.from_user.id
    accounts = await get_all_accounts(user_id=user_id)

    if not accounts:
        await callback_query.message.edit_text(
            "📭 <b>ɴᴏ sᴀᴠᴇᴅ ᴛᴇʟᴇɢʀᴀᴍ ᴀᴄᴄᴏᴜɴᴛs ꜰᴏᴜɴᴅ ᴛᴏ ᴇxᴘᴏʀᴛ.</b>",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔙 ʙᴀᴄᴋ ᴛᴏ ʟɪsᴛ", callback_data=f"back_to_list:{page}")]
            ]),
            parse_mode="HTML"
        )
        return

    if action == "text_file":
        await callback_query.message.edit_text(
            f"⏳ <b>ᴄᴏᴍᴘɪʟɪɴɢ {len(accounts)} session strings to a single text file... ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ.</b>",
            parse_mode="HTML"
        )

        txt_path = Path("temp_bulk") / f"all_sessions_{user_id}_{os.urandom(4).hex()}.txt"
        try:
            txt_path.parent.mkdir(parents=True, exist_ok=True)
            consolidated_lines = []
            for acc in accounts:
                phone = acc.get("phone")
                session_str = decrypt_data(acc["encrypted_session"])

                if format_choice == "telethon":
                    out_str = pyrogram_to_telethon(session_str)
                    if not out_str:
                        out_str = "Error converting to Telethon format."
                else:
                    out_str = session_str

                consolidated_lines.append(f"{phone}: {out_str}")

            with open(txt_path, "w", encoding="utf-8") as f:
                f.write("\n".join(consolidated_lines))

            if txt_path.exists() and txt_path.stat().st_size > 0:
                await callback_query.bot.send_document(
                    chat_id=callback_query.message.chat.id,
                    document=FSInputFile(str(txt_path)),
                    caption=f"📄 <b><b>ʙᴜʟᴋ sᴇssɪᴏɴ sᴛʀɪɴɢs (.ᴛxᴛ) ᴇxᴘᴏʀᴛᴇᴅ sᴜᴄᴄᴇssꜰᴜʟʟʏ!</b></b>\n\n📱 <b>ᴛᴏᴛᴀʟ ᴀᴄᴄᴏᴜɴᴛs:</b> <code>{len(accounts)}</code>",
                    parse_mode="HTML"
                )
                await callback_query.message.edit_text(
                    f"✅ <b>session strings text file sent successfully!</b>\n\n📱 <b>ᴛᴏᴛᴀʟ ᴀᴄᴄᴏᴜɴᴛs:</b> <code>{len(accounts)}</code>",
                    reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                        [InlineKeyboardButton(text="🔙 ʙᴀᴄᴋ ᴛᴏ ʟɪsᴛ", callback_data=f"back_to_list:{page}")]
                    ]),
                    parse_mode="HTML"
                )
            else:
                raise FileNotFoundError("Text file was not successfully generated.")

        except Exception as txt_err:
            logger.exception("Error during text file bulk export")
            await callback_query.message.edit_text(
                f"❌ <b>ꜰᴀɪʟᴇᴅ ᴛᴏ ɢᴇɴᴇʀᴀᴛᴇ ᴛᴇxᴛ ꜰɪʟᴇ:</b> <code>{html.escape(str(txt_err))}</code>",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="🔙 ʙᴀᴄᴋ ᴛᴏ ʟɪsᴛ", callback_data=f"back_to_list:{page}")]
                ]),
                parse_mode="HTML"
            )
        finally:
            if txt_path.exists():
                try:
                    os.remove(txt_path)
                except Exception:
                    pass
        return

    import zipfile
    import shutil

    # Secure user partition directory for compilation
    temp_dir = Path("temp_bulk") / f"bulk_{user_id}_{action}"
    temp_dir.mkdir(parents=True, exist_ok=True)

    zip_path = Path("temp_bulk") / f"bulk_{user_id}_{action}.zip"

    if action == "sqlite":
        await callback_query.message.edit_text(
            f"⏳ <b>ᴄᴏɴᴠᴇʀᴛɪɴɢ {len(accounts)} sᴇssɪᴏɴs... ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ.</b>",
            parse_mode="HTML"
        )

        try:
            for acc in accounts:
                phone = acc.get("phone")
                session_str = decrypt_data(acc["encrypted_session"])
                name_clean = phone.replace("+", "")

                if format_choice == "telethon":
                    generate_telethon_sqlite(session_str, name_clean, temp_dir)
                else:
                    await save_session_string_to_file(session_str, name_clean, temp_dir)

            # Create ZIP
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, _, files in os.walk(temp_dir):
                    for file in files:
                        if file.endswith(".session") or file.endswith(".txt"):
                            zipf.write(os.path.join(root, file), file)

            if zip_path.exists() and zip_path.stat().st_size > 0:
                await callback_query.bot.send_document(
                    chat_id=callback_query.message.chat.id,
                    document=FSInputFile(str(zip_path)),
                    caption=f"📦 <b>ʙᴜʟᴋ sᴇssɪᴏɴs (.ᴢɪᴘ) ᴇxᴘᴏʀᴛᴇᴅ sᴜᴄssꜰᴜʟʟʏ!</b>\n\n📱 <b>ᴛᴏᴛᴀʟ ᴀᴄᴄᴏᴜɴᴛs:</b> <code>{len(accounts)}</code>",
                    parse_mode="HTML"
                )
                await callback_query.message.edit_text(
                    f"✅ <b> sᴇssɪᴏɴs ZIP file sent successfully!</b>\n\n📱 <b>ᴛᴏᴛᴀʟ ᴀᴄᴄᴏᴜɴᴛs:</b> <code>{len(accounts)}</code>",
                    reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                        [InlineKeyboardButton(text="🔙 ʙᴀᴄᴋ ᴛᴏ ʟɪsᴛ", callback_data=f"back_to_list:{page}")]
                    ]),
                    parse_mode="HTML"
                )
            else:
                raise FileNotFoundError("ZIP file was not successfully generated.")

        except Exception as zip_err:
            logger.exception("Error during sqlite bulk export")
            await callback_query.message.edit_text(
                f"❌ <b>ꜰᴀɪʟᴇᴅ ᴛᴏ ɢᴇɴᴇʀᴀᴛᴇ sǫʟɪᴛᴇ ᴢɪᴘ:</b> <code>{html.escape(str(zip_err))}</code>",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="🔙 ʙᴀᴄᴋ ᴛᴏ ʟɪsᴛ", callback_data=f"back_to_list:{page}")]
                ]),
                parse_mode="HTML"
            )

    elif action == "strings":
        await callback_query.message.edit_text(
            f"⏳ <b>ᴄᴏᴍᴘɪʟɪɴɢ {len(accounts)} session strings... ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ.</b>",
            parse_mode="HTML"
        )

        try:
            # consolidated format txt file: phone:session_string
            consolidated_lines = []

            for acc in accounts:
                phone = acc.get("phone")
                session_str = decrypt_data(acc["encrypted_session"])
                name_clean = phone.replace("+", "")

                if format_choice == "telethon":
                    generate_telethon_sqlite(session_str, name_clean, temp_dir)
                    # For the consolidated string file, we can optionally keep the string format or skip it.
                    # Since they want native sessions, let's just note it's converted.
                    out_str = pyrogram_to_telethon(session_str) or "Error converting"
                    consolidated_lines.append(f"{phone}: {out_str}")
                else:
                    out_str = session_str
                    # Create individual text file
                    ind_txt_path = temp_dir / f"{name_clean}.txt"
                    with open(ind_txt_path, "w", encoding="utf-8") as ind_f:
                        ind_f.write(out_str)
                    consolidated_lines.append(f"{phone}: {out_str}")

            # Create consolidated text file
            consolidated_path = temp_dir / "sessions.txt"
            with open(consolidated_path, "w", encoding="utf-8") as cons_f:
                cons_f.write("\n".join(consolidated_lines))

            # Create ZIP
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, _, files in os.walk(temp_dir):
                    for file in files:
                        if file.endswith(".txt") or file.endswith(".session"):
                            zipf.write(os.path.join(root, file), file)

            if zip_path.exists() and zip_path.stat().st_size > 0:
                await callback_query.bot.send_document(
                    chat_id=callback_query.message.chat.id,
                    document=FSInputFile(str(zip_path)),
                    caption=f"🌀 <b>ʙᴜʟᴋ sᴇssɪᴏɴ sᴛʀɪɴɢs (.ᴢɪᴘ) ɢᴇɴᴇʀᴀᴛᴇᴅ sᴜᴄᴄᴇssꜰᴜʟʟʏ!</b>\n\n📱 <b>ᴛᴏᴛᴀʟ ᴀᴄᴄᴏᴜɴᴛs:</b> <code>{len(accounts)}</code>",
                    parse_mode="HTML"
                )
                await callback_query.message.edit_text(
                    f"✅ <b>sᴇssɪᴏɴ sᴛʀɪɴɢs ZIP file sent successfully!</b>\n\n📱 <b>ᴛᴏᴛᴀʟ ᴀᴄᴄᴏᴜɴᴛs:</b> <code>{len(accounts)}</code>",
                    reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                        [InlineKeyboardButton(text="🔙 ʙᴀᴄᴋ ᴛᴏ ʟɪsᴛ", callback_data=f"back_to_list:{page}")]
                    ]),
                    parse_mode="HTML"
                )
            else:
                raise FileNotFoundError("ZIP file was not successfully generated.")

        except Exception as zip_err:
            logger.exception("Error during strings bulk export")
            await callback_query.message.edit_text(
                f"❌ <b>ꜰᴀɪʟᴇᴅ ᴛᴏ ɢᴇɴᴇʀᴀᴛᴇ sᴛʀɪɴɢs ᴢɪᴘ:</b> <code>{html.escape(str(zip_err))}</code>",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="🔙 ʙᴀᴄᴋ ᴛᴏ ʟɪsᴛ", callback_data=f"back_to_list:{page}")]
                ]),
                parse_mode="HTML"
            )

    # Clean up temp directories
    if temp_dir.exists():
        try:
            shutil.rmtree(temp_dir)
        except Exception:
            pass
    if zip_path.exists():
        try:
            os.remove(zip_path)
        except Exception:
            pass

@router.callback_query(F.data.startswith("bulk_export:"))
async def bulk_export_handler(callback_query: CallbackQuery):
    await callback_query.answer()

    parts = callback_query.data.split(":")
    action = parts[1]
    page = int(parts[2]) if len(parts) > 2 else 0

    user_id = callback_query.from_user.id
    accounts = await get_all_accounts(user_id=user_id)

    if not accounts:
        await callback_query.message.edit_text(
            "📭 <b>ɴᴏ sᴀᴠᴇᴅ ᴛᴇʟᴇɢʀᴀᴍ ᴀᴄᴄᴏᴜɴᴛs ꜰᴏᴜɴᴅ ᴛᴏ ᴇxᴘᴏʀᴛ.</b>",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔙 ʙᴀᴄᴋ ᴛᴏ ʟɪsᴛ", callback_data=f"back_to_list:{page}")]
            ]),
            parse_mode="HTML"
        )
        return

    if action == "menu":
        export_keyboard = [
            [InlineKeyboardButton(text="📥 ᴇxᴘᴏʀᴛ ᴄᴜʀʀᴇɴᴛ sᴇssɪᴏɴs (.ᴢɪᴘ)", callback_data=f"bulk_export_prompt:sqlite:{page}")],
            [InlineKeyboardButton(text="🌀 ɢᴇɴᴇʀᴀᴛᴇ ᴀʟʟ ɴᴇᴡ sᴇssɪᴏɴs (.ᴢɪᴘ)", callback_data=f"bulk_export_prompt:strings:{page}")],
            [InlineKeyboardButton(text="📄 ᴇxᴘᴏʀᴛ sɪɴɢʟᴇ ᴛᴇxᴛ ꜰɪʟᴇ (.ᴛxᴛ)", callback_data=f"bulk_export_prompt:text_file:{page}")],
            [InlineKeyboardButton(text="🔙 ʙᴀᴄᴋ", callback_data=f"back_to_list:{page}")]
        ]
        await callback_query.message.edit_text(
            "📦 <b>ʙᴜʟᴋ ᴇxᴘᴏʀᴛ / ɢᴇɴᴇʀᴀᴛᴇ</b>\n\n"
            "ᴄʜᴏᴏsᴇ:",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=export_keyboard),
            parse_mode="HTML"
        )
        return

    return

@router.callback_query(F.data.startswith("confirm_del:"))
async def process_confirm_deletion(callback_query: CallbackQuery):
    await callback_query.answer()

    parts = callback_query.data.split(":")
    phone = parts[1]
    page = int(parts[2]) if len(parts) > 2 else 0

    deleted = await delete_account(phone, user_id=callback_query.from_user.id)

    if deleted:
        await callback_query.message.edit_text(
            f"✅ <b>sᴜᴄᴄᴇssꜰᴜʟʟʏ ᴅᴇʟᴇᴛᴇᴅ ᴀᴄᴄᴏᴜɴᴛ:</b> <code>{html.escape(phone)}</code>",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔙 ʙᴀᴄᴋ ᴛᴏ ʟɪsᴛ", callback_data=f"back_to_list:{page}")]
            ])
        )
    else:
        await callback_query.message.edit_text(
            f"❌ <b><b>ꜰᴀɪʟᴇᴅ ᴏʀ ᴀʟʀᴇᴀᴅʏ ᴅᴇʟᴇᴛᴇᴅ ᴀᴄᴄᴏᴜɴᴛ</b></b> <code>{html.escape(phone)}</code>.",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔙 ʙᴀᴄᴋ ᴛᴏ ʟɪsᴛ", callback_data=f"back_to_list:{page}")]
            ])
        )
