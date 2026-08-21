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
import re
import logging
import html
import random
import emoji
from pyrogram.errors import RPCError, FloodWait, ChatAdminRequired, UserDeactivated, UsernameOccupied, UsernameInvalid, FreshResetAuthorisationForbidden
from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, LinkPreviewOptions
from config import API_ID, API_HASH
from database import save_account
from helpers import get_random_proxy, create_pyrogram_client, encrypt_data, normalize_session_string

# Pyrogram exceptions
from pyrogram.errors import (
    SessionPasswordNeeded,
    PhoneCodeInvalid,
    PhoneCodeExpired,
    PasswordHashInvalid,
    AuthKeyInvalid,
    Unauthorized,
    AuthKeyUnregistered
)

logger = logging.getLogger("TGStorageBot.plugins.add_account")
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

def get_preview():
    return LinkPreviewOptions(url=random.choice(IMAGES), prefer_large_media=True, show_above_text=True)

class AddAccountStates(StatesGroup):
    waiting_for_phone = State()
    waiting_for_otp = State()
    waiting_for_2fa = State()
    waiting_for_string_or_file = State()
    waiting_for_telethon_string_or_file = State()

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
    text = emoji.replace_emoji(text, replace="")
    text = text.replace("[", "").replace("]", "").strip()
    return "".join(mapping.get(c, c) for c in text)

def get_back_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=make_small_caps("back to menu"), callback_data="menu:cancel_add")]
    ])

def get_add_account_choice_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton(text=make_small_caps("phone (otp)"), callback_data="add_acc:phone")],
        [InlineKeyboardButton(text=make_small_caps("upload string / file"), callback_data="add_acc:upload")],
        [InlineKeyboardButton(text=make_small_caps("cancel"), callback_data="menu:cancel_add")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


# ----------------- TELETHON TO PYROGRAM CONVERTER -----------------
def convert_telethon_string_to_pyrogram(telethon_string: str, fallback_api_id: int) -> str:
    import struct
    import base64

    fallback_api_id = int(fallback_api_id) if fallback_api_id else 6
    telethon_string = telethon_string.strip()

    if not telethon_string.startswith("1"):
        raise ValueError("Not a valid Telethon string (does not start with '1')")

    import binascii
    base64_str = telethon_string[1:]
    base64_str += "=" * (-len(base64_str) % 4)

    try:
        decoded = base64.urlsafe_b64decode(base64_str)
    except (Exception, binascii.Error) as e:
        raise ValueError(f"Failed to decode base64: {e}")

    if len(decoded) != 263:
        raise ValueError(f"Invalid Telethon string length (expected 263, got {len(decoded)})")

    dc_id, ip_bytes, port, auth_key = struct.unpack(">B4sH256s", decoded)

    user_id = 9999
    pyro_packed = struct.pack('>BI?256sQ?', dc_id, fallback_api_id, False, auth_key, user_id, False)
    return base64.urlsafe_b64encode(pyro_packed).decode().rstrip("=")

def parse_sqlite_to_pyrogram_string(db_path: str, fallback_api_id: int) -> str:
    import sqlite3
    import struct
    import base64
    
    fallback_api_id = int(fallback_api_id) if fallback_api_id else 6
    
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='entities'")
        is_telethon = cursor.fetchone() is not None
        
        if is_telethon:
            cursor.execute("SELECT dc_id, auth_key FROM sessions")
            row = cursor.fetchone()
            if not row:
                raise ValueError("Telethon sessions table is empty.")
            dc_id, auth_key = row
            
            user_id = 9999 
                
            pyro_packed = struct.pack('>BI?256sQ?', dc_id, fallback_api_id, False, auth_key, user_id, False)
            return base64.urlsafe_b64encode(pyro_packed).decode().rstrip("=")
        else:
            cursor.execute("SELECT dc_id, api_id, test_mode, auth_key, user_id, is_bot FROM sessions")
            row = cursor.fetchone()
            if not row:
                raise ValueError("Pyrogram sessions table is empty.")
            dc_id, api_id, test_mode, auth_key, user_id, is_bot = row
            
            user_id = abs(int(user_id)) if user_id else 9999
            
            pyro_packed = struct.pack('>BI?256sQ?', dc_id, int(api_id) if api_id else fallback_api_id, bool(test_mode), auth_key, user_id, bool(is_bot))
            return base64.urlsafe_b64encode(pyro_packed).decode().rstrip("=")
# ------------------------------------------------------------------


@router.callback_query(F.data == "menu:add_account")
async def start_add_account_callback(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.answer()
    await state.clear()
    await callback_query.message.edit_text(
        "<b>➕ ᴀᴅᴅ ᴀᴄᴄᴏᴜɴᴛ</b>\n\n"
        "ᴄʜᴏᴏsᴇ ʜᴏᴡ ᴛᴏ ᴀᴅᴅ:",
        parse_mode="HTML",
        link_preview_options=get_preview(),
        reply_markup=get_add_account_choice_keyboard()
    )

@router.message(Command("add_account"))
async def start_add_account(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "<b>➕ ᴀᴅᴅ ᴀᴄᴄᴏᴜɴᴛ</b>\n\n"
        "ᴄʜᴏᴏsᴇ ʜᴏᴡ ᴛᴏ ᴀᴅᴅ:",
        parse_mode="HTML",
        link_preview_options=get_preview(),
        reply_markup=get_add_account_choice_keyboard()
    )

@router.message(Command("telethon"))
async def start_telethon_import(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "<b>📁 ᴛᴇʟᴇᴛʜᴏɴ ɪᴍᴘᴏʀᴛ</b>\n\n"
        "👉 <b>ᴘʟᴇᴀsᴇ sᴇɴᴅ ʏᴏᴜʀ Telethon sᴇssɪᴏɴ sᴛʀɪɴɢ</b> (starts with <code>1</code>) as a text message or a <code>.txt</code> file.\n\n"
        "👉 Alternatively, you can <b>upload a <code>.zip</code> archive</b> containing multiple text files with Telethon strings.",
        parse_mode="HTML",
        link_preview_options=get_preview(),
        reply_markup=get_back_keyboard()
    )
    await state.set_state(AddAccountStates.waiting_for_telethon_string_or_file)

@router.callback_query(F.data == "add_acc:phone")
async def add_account_phone_callback(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.answer()
    await callback_query.message.edit_text(
        "<b>📱 ᴘʟᴇᴀsᴇ ᴇɴᴛᴇʀ ᴛʜᴇ ᴛᴇʟᴇɢʀᴀᴍ ᴘʜᴏɴᴇ ɴᴜᴍʙᴇʀ</b> ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ᴀᴅᴅ.\n"
        "ɪɴᴄʟᴜᴅᴇ ᴛʜᴇ ᴄᴏᴜɴᴛʀʏ ᴄᴏᴅᴇ (ᴇ.ɢ., <code>+1234567890</code> ᴏʀ <code>+919876543210</code>):\n\n"
        "ᴘʀᴇss ᴛʜᴇ ʙᴜᴛᴛᴏɴ ʙᴇʟᴏᴡ ᴀᴛ ᴀɴʏ ᴛɪᴍᴇ ᴛᴏ ᴄᴀɴᴄᴇʟ.",
        parse_mode="HTML",
        link_preview_options=get_preview(),
        reply_markup=get_back_keyboard()
    )
    await state.set_state(AddAccountStates.waiting_for_phone)

@router.callback_query(F.data == "add_acc:upload")
async def add_account_upload_callback(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.answer()
    await callback_query.message.edit_text(
        "<b>📁 ᴜᴘʟᴏᴀᴅ sᴛʀɪɴɢ / ꜰɪʟᴇ</b>\n\n"
        "👉 <b>ᴘʟᴇᴀsᴇ sᴇɴᴅ ʏᴏᴜʀ Pyrogram sᴇssɪᴏɴ sᴛʀɪɴɢ</b> as a text message or a <code>.txt</code> file.\n\n"
        "👉 Alternatively, you can <b>upload a physical <code>.session</code> SQLite file</b>.",
        parse_mode="HTML",
        link_preview_options=get_preview(),
        reply_markup=get_back_keyboard()
    )
    await state.set_state(AddAccountStates.waiting_for_string_or_file)

@router.message(Command("cancel"))
@router.message(F.text.casefold() == "cancel")
async def cancel_handler(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    data = await state.get_data()
    client = data.get("client")
    if client:
        try:
            if client.is_connected:
                await client.disconnect()
        except Exception as e:
            logger.error(f"Error disconnecting client on cancel: {e}")
    await state.clear()
    await message.answer(
        "❌ <b>ᴀᴄᴛɪᴏɴ ᴄᴀɴᴄᴇʟʟᴇᴅ sᴜᴄᴄᴇssꜰᴜʟʟʏ.</b>",
        parse_mode="HTML",
        link_preview_options=get_preview(),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=make_small_caps("back to main menu"), callback_data="menu:main")]
        ])
    )

@router.callback_query(F.data == "menu:cancel_add")
async def cancel_add_callback(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.answer()
    data = await state.get_data()
    client = data.get("client")
    if client:
        try:
            if client.is_connected:
                await client.disconnect()
        except Exception as e:
            logger.error(f"Error disconnecting client on cancel: {e}")
    await state.clear()
    await callback_query.message.edit_text(
        "❌ <b>ᴀᴄᴛɪᴏɴ ᴄᴀɴᴄᴇʟʟᴇᴅ sᴜᴄᴄᴇssꜰᴜʟʟʏ.</b>",
        parse_mode="HTML",
        link_preview_options=get_preview(),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=make_small_caps("back to main menu"), callback_data="menu:main")]
        ])
    )

@router.message(AddAccountStates.waiting_for_telethon_string_or_file)
async def process_telethon_string_or_file_upload(message: Message, state: FSMContext):
    import os
    import zipfile
    import shutil
    from pathlib import Path

    session_str = None
    file_path_to_clean = None

    try:
        if message.document:
            file_id = message.document.file_id
            file_name = message.document.file_name or ""

            temp_dir = Path("temp_uploads")
            temp_dir.mkdir(exist_ok=True)
            dest_path = temp_dir / f"uploaded_tel_{message.from_user.id}_{file_name}"
            file_path_to_clean = dest_path

            bot_obj = message.bot
            await bot_obj.download(file_id, destination=str(dest_path))

            if file_name.lower().endswith(".zip"):
                status_msg = await message.answer(
                    "⚙️ <b>ᴇxᴛʀᴀᴄᴛɪɴɢ ᴀɴᴅ ᴘᴀʀsɪɴɢ</b> <code>.zip</code> <b>ᴀʀᴄʜɪᴠᴇ ꜰᴏʀ ᴛᴇʟᴇᴛʜᴏɴ...</b>", 
                    parse_mode="HTML",
                    link_preview_options=get_preview()
                )
                zip_extract_dir = temp_dir / f"extracted_tel_{message.from_user.id}_{os.urandom(4).hex()}"
                try:
                    zip_extract_dir.mkdir(exist_ok=True, parents=True)

                    with zipfile.ZipFile(dest_path, 'r') as zip_ref:
                        safe_members = []
                        for member in zip_ref.infolist():
                            filename = member.filename
                            normalized = filename.replace("\\", "/")
                            if normalized.startswith("/") or ".." in normalized.split("/"):
                                continue
                            safe_members.append(member)
                        zip_ref.extractall(zip_extract_dir, members=safe_members)

                    sessions_to_import = []
                    all_found_files = []
                    parsing_errors = []

                    for root, dirs, files in os.walk(zip_extract_dir):
                        for file in files:
                            p = Path(root) / file
                            file_size = p.stat().st_size if p.exists() else 0
                            all_found_files.append((p.name, file_size))

                            if p.suffix.lower() == ".session":
                                sessions_to_import.append(("file", p.stem, p.name, str(p.parent)))
                            else:
                                try:
                                    with open(p, "r", encoding="utf-8", errors="ignore") as f:
                                        content_f = f.read()
                                    found_strings = re.findall(r"1[a-zA-Z0-9+\-_=/]{300,}", content_f)
                                    if found_strings:
                                        for s in found_strings:
                                            sessions_to_import.append(("string", s, p.name, None))
                                    else:
                                        parsing_errors.append(f"{p.name} (no telethon session string found)")
                                except Exception as txt_err:
                                    parsing_errors.append(f"{p.name} (read err: {str(txt_err)[:40]})")

                    if not sessions_to_import:
                        files_list_str = ""
                        for f_name, f_size in all_found_files[:15]:
                            files_list_str += f"• <code>{html.escape(f_name)}</code> ({f_size} bytes)\n"
                        if len(all_found_files) > 15:
                            files_list_str += f"<i>...and {len(all_found_files) - 15} more files</i>\n"
                        error_details = (
                            "❌ <b>ɴᴏ ᴠᴀʟɪᴅ ᴛᴇʟᴇᴛʜᴏɴ sᴇssɪᴏɴs ꜰᴏᴜɴᴅ ɪɴ ᴛʜᴇ ᴢɪᴘ ᴀʀᴄʜɪᴠᴇ.</b>\n\n"
                            f"📁 <b>Files found in ZIP ({len(all_found_files)}):</b>\n"
                            f"{files_list_str or '• None'}"
                        )
                        await status_msg.edit_text(error_details, parse_mode="HTML", reply_markup=get_back_keyboard(), link_preview_options=get_preview())
                        return

                    unique_sessions = []
                    seen_strings = set()
                    for s_type, s_data, s_name, s_workdir in sessions_to_import:
                        dedup_key = f"{s_workdir}/{s_data}" if s_type == "file" else s_data
                        if dedup_key not in seen_strings:
                            seen_strings.add(dedup_key)
                            unique_sessions.append((s_type, s_data, s_name, s_workdir))

                    await process_telethon_bulk_import(message, state, unique_sessions, status_msg)
                    return
                except Exception as zip_err:
                    await status_msg.edit_text(
                        f"❌ <b>ꜰᴀɪʟᴇᴅ ᴛᴏ ᴘʀᴏᴄᴇss ᴢɪᴘ:</b> <code>{html.escape(str(zip_err))}</code>",
                        parse_mode="HTML",
                        reply_markup=get_back_keyboard(),
                        link_preview_options=get_preview()
                    )
                    return
                finally:
                    if zip_extract_dir.exists():
                        try: shutil.rmtree(zip_extract_dir)
                        except Exception: pass
            else:
                try:
                    with open(dest_path, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read().strip()
                    found_strings = re.findall(r"1[a-zA-Z0-9+\-_=/]{300,}", content)
                    if found_strings:
                        session_str = found_strings[0]
                    else:
                        session_str = content
                except Exception as text_err:
                    await message.answer(f"❌ <b>ꜰᴀɪʟᴇᴅ ᴛᴏ ʀᴇᴀᴅ ꜰɪʟᴇ:</b> <code>{html.escape(str(text_err))}</code>", parse_mode="HTML", reply_markup=get_back_keyboard(), link_preview_options=get_preview())
                    return
        elif message.text:
            content = message.text.strip()
            found_strings = re.findall(r"1[a-zA-Z0-9+\-_=/]{300,}", content)
            if found_strings:
                session_str = found_strings[0]
            else:
                session_str = content
        else:
            await message.answer("⚠️ <b>ᴘʟᴇᴀsᴇ sᴇɴᴅ ᴀ ᴠᴀʟɪᴅ ᴛᴇʟᴇᴛʜᴏɴ sᴇssɪᴏɴ sᴛʀɪɴɢ ᴏʀ ᴜᴘʟᴏᴀᴅ ᴀ ꜰɪʟᴇ.</b>", parse_mode="HTML", reply_markup=get_back_keyboard(), link_preview_options=get_preview())
            return

        if not session_str or not session_str.startswith("1"):
            await message.answer("⚠️ <b>ᴛʜᴇ sᴛʀɪɴɢ ᴅᴏᴇs ɴᴏᴛ ᴀᴘᴘᴇᴀʀ ᴛᴏ ʙᴇ ᴀ ᴠᴀʟɪᴅ ᴛᴇʟᴇᴛʜᴏɴ sᴇssɪᴏɴ (ᴍᴜsᴛ sᴛᴀʀᴛ ᴡɪᴛʜ '1').</b>", parse_mode="HTML", reply_markup=get_back_keyboard(), link_preview_options=get_preview())
            return

        await process_telethon_bulk_import(message, state, [("string", session_str, "uploaded_string", None)], await message.answer("⏳ <b>ᴄᴏɴɴᴇᴄᴛɪɴɢ...</b>", parse_mode="HTML", link_preview_options=get_preview()))

    finally:
        if file_path_to_clean and os.path.exists(file_path_to_clean):
            try: os.remove(file_path_to_clean)
            except: pass

async def process_telethon_bulk_import(message: Message, state: FSMContext, unique_sessions: list, status_msg: Message):
    import time
    success_count = 0
    expired_sessions = []
    other_failed_sessions = []

    total_sessions = len(unique_sessions)
    last_edit_time = time.time()

    def make_progress_bar(current: int, total: int) -> str:
        if total <= 0: return "░" * 10
        filled = int(10 * current // total)
        bar = "■" * filled + "□" * (10 - filled)
        pct = int((current / total) * 100)
        return f"<code>[{bar}]</code> <b>{pct}%</b>"

    for i, (s_type, s_data, source_name, s_workdir) in enumerate(unique_sessions, 1):
        now_time = time.time()
        if i == 1 or i == total_sessions or (now_time - last_edit_time >= 1.5):
            progress_text = (
                f"⏳ <b>ᴛᴇʟᴇᴛʜᴏɴ ʙᴜʟᴋ ɪᴍᴘᴏʀᴛ ɪɴ ᴘʀᴏɢʀᴇss...</b>\n\n"
                f"📈 <b>ᴘʀᴏɢʀᴇss:</b> {make_progress_bar(i - 1, total_sessions)} (<code>{i - 1} / {total_sessions}</code>)\n"
                f"━━━━━━━━━━━━━━━━━━━━━\n"
                f"✅ <b>sᴜᴄᴄᴇss:</b> <code>{success_count}</code>\n"
                f"🔴 <b>ᴇxᴘɪʀᴇᴅ:</b> <code>{len(expired_sessions)}</code>\n"
                f"⚠️ <b>ꜰᴀɪʟᴇᴅ:</b> <code>{len(other_failed_sessions)}</code>\n"
                f"⏳ <b>ᴘᴇɴᴅɪɴɢ:</b> <code>{total_sessions - (i - 1)}</code>\n\n"
                f"⚡ <i>Processing: {html.escape(source_name)}...</i>"
            )
            try:
                await status_msg.edit_text(progress_text, parse_mode="HTML", link_preview_options=get_preview())
                last_edit_time = now_time
            except:
                pass

        proxy, proxy_error = get_random_proxy()
        temp_name = f"uploaded_tel_sess_{message.from_user.id}_{i}"

        try:
            if s_type == "file":
                session_file_path = os.path.join(s_workdir, f"{s_data}.session")
                pyro_str = parse_sqlite_to_pyrogram_string(session_file_path, API_ID)
            else:
                pyro_str = convert_telethon_string_to_pyrogram(s_data, API_ID)

            client = create_pyrogram_client(session_name=temp_name, session_string=pyro_str, proxy=proxy)

            await client.connect()
            try:
                me = await client.get_me()
            except (AuthKeyInvalid, Unauthorized, AuthKeyUnregistered):
                raise AuthKeyInvalid("Session is dead")

            if not me:
                raise ValueError("Could not retrieve account identity from get_me()")

            phone = getattr(me, "phone_number", None)
            if not phone:
                phone = f"+{me.id}"
            else:
                if not phone.startswith("+"): phone = f"+{phone}"

            first = me.first_name or ""
            last = me.last_name or ""
            profile_name = " ".join([p for p in [first, last] if p.strip()]) or me.username or "ᴜɴᴋɴᴏᴡɴ"

            exported_session_str = await client.export_session_string()
            encrypted_session = encrypt_data(exported_session_str)
            await client.disconnect()

            saved = await save_account(phone=phone, encrypted_session=encrypted_session, user_id=message.from_user.id, proxy=proxy, profile_name=profile_name)
            if saved: success_count += 1
            else: other_failed_sessions.append((source_name, "Failed to save to MongoDB"))

        except (AuthKeyInvalid, Unauthorized, AuthKeyUnregistered):
            expired_sessions.append((source_name, "Session Expired / Revoked"))
            try: await client.disconnect()
            except: pass
        except Exception as err:
            err_str = str(err)
            if "deactivated" in err_str.lower() or "deactive" in err_str.lower():
                expired_sessions.append((source_name, "Account Deactivated by Telegram"))
            else:
                other_failed_sessions.append((source_name, err_str))
            try: await client.disconnect()
            except: pass

    summary_text = (
        "📦 <b>ᴛᴇʟᴇᴛʜᴏɴ ʙᴜʟᴋ ɪᴍᴘᴏʀᴛ sᴜᴍᴍᴀʀʏ</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        f"✅ <b>sᴜᴄᴄᴇssꜰᴜʟʟʏ ɪᴍᴘᴏʀᴛᴇᴅ:</b> <code>{success_count} / {len(unique_sessions)}</code> accounts\n"
    )
    if expired_sessions:
        summary_text += f"\n🔴 <b>ᴇxᴘɪʀᴇᴅ / ɪɴᴠᴀʟɪᴅ sᴇssɪᴏɴs:</b> <code>{len(expired_sessions)}</code>\n"
    if other_failed_sessions:
        summary_text += f"\n⚠️ <b>ᴏᴛʜᴇʀ ꜰᴀɪʟᴜʀᴇs:</b> <code>{len(other_failed_sessions)}</code>\n"
    if not expired_sessions and not other_failed_sessions:
        summary_text += "\n🟢 <b>All sessions imported successfully!</b>"

    await status_msg.delete()
    await message.answer(
        summary_text,
        parse_mode="HTML",
        link_preview_options=get_preview(),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=make_small_caps("back to main menu"), callback_data="menu:main")]
        ])
    )
    await state.clear()


@router.callback_query(F.data == "add_acc:phone")
async def add_account_phone_callback(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.answer()
    await callback_query.message.edit_text(
        "<b>📱 ᴘʟᴇᴀsᴇ ᴇɴᴛᴇʀ ᴛʜᴇ ᴛᴇʟᴇɢʀᴀᴍ ᴘʜᴏɴᴇ ɴᴜᴍʙᴇʀ</b> ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ᴀᴅᴅ.\n"
        "ɪɴᴄʟᴜᴅᴇ ᴛʜᴇ ᴄᴏᴜɴᴛʀʏ ᴄᴏᴅᴇ (ᴇ.ɢ., <code>+1234567890</code> ᴏʀ <code>+919876543210</code>):\n\n"
        "ᴘʀᴇss ᴛʜᴇ ʙᴜᴛᴛᴏɴ ʙᴇʟᴏᴡ ᴀᴛ ᴀɴʏ ᴛɪᴍᴇ ᴛᴏ ᴄᴀɴᴄᴇʟ.",
        parse_mode="HTML",
        link_preview_options=get_preview(),
        reply_markup=get_back_keyboard()
    )
    await state.set_state(AddAccountStates.waiting_for_phone)


@router.message(AddAccountStates.waiting_for_phone)
async def process_phone(message: Message, state: FSMContext):
    if not message.text:
        await message.answer("⚠️ <b>ᴘʟᴇᴀsᴇ sᴇɴᴅ ᴀ ᴠᴀʟɪᴅ ᴘʜᴏɴᴇ ɴᴜᴍʙᴇʀ.</b>", parse_mode="HTML", reply_markup=get_back_keyboard(), link_preview_options=get_preview())
        return
    phone = message.text.strip().replace(" ", "")
    if not re.match(r"^\+\d{8,15}$", phone):
        await message.answer(
            "⚠️ <b>ɪɴᴠᴀʟɪᴅ ᴘʜᴏɴᴇ ꜰᴏʀᴍᴀᴛ.</b> ᴘʟᴇᴀsᴇ ᴇɴᴛᴇʀ ᴡɪᴛʜ ᴄᴏᴜɴᴛʀʏ ᴄᴏᴅᴇ (ᴇ.ɢ. <code>+1234567890</code>):",
            parse_mode="HTML",
            link_preview_options=get_preview(),
            reply_markup=get_back_keyboard()
        )
        return
    proxy, proxy_error = get_random_proxy()
    if not proxy:
        warning_msg = "⚠️ <b>ɴᴏ sᴏᴄᴋs5 ᴘʀᴏxɪᴇs ᴄᴏɴꜰɪɢᴜʀᴇᴅ. ᴘʀᴏᴄᴇᴇᴅɪɴɢ ᴡɪᴛʜ ᴅɪʀᴇᴄᴛ ᴄᴏɴɴᴇᴄᴛɪᴏɴ.</b>"
        await message.answer(warning_msg, parse_mode="HTML", link_preview_options=get_preview())
    else:
        success_msg = f"🌐 <b>ᴘʀᴏxʏ sᴇʟᴇᴄᴛᴇᴅ:</b> <code>{html.escape(proxy['hostname'])}:{proxy['port']}</code>. ᴄᴏɴɴᴇᴄᴛɪɴɢ..."
        await message.answer(success_msg, parse_mode="HTML", link_preview_options=get_preview())
        
    status_msg = await message.answer(
        "⏳ <b>ᴄᴏɴɴᴇᴄᴛɪɴɢ ᴛᴏ ᴛᴇʟᴇɢʀᴀᴍ sᴇʀᴠᴇʀs &amp; ɢᴇɴᴇʀᴀᴛɪɴɢ ᴏᴛᴘ... ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ.</b>",
        parse_mode="HTML",
        link_preview_options=get_preview(),
        reply_markup=get_back_keyboard()
    )
    try:
        session_name = f"sess_{phone.replace('+', '')}"
        client = create_pyrogram_client(session_name=session_name, proxy=proxy)
        await client.connect() # FIX: Bypass console prompt
        code_info = await client.send_code(phone)
        phone_code_hash = code_info.phone_code_hash
        await state.update_data(
            phone=phone,
            client=client,
            phone_code_hash=phone_code_hash,
            proxy=proxy
        )
        await message.answer(
            f"📨 <b>ᴛᴇʟᴇɢʀᴀᴍ sᴇɴᴛ ᴀ ʟᴏɢɪɴ ᴏᴛᴘ/ᴄᴏᴅᴇ</b> ᴛᴏ <code>{html.escape(phone)}</code>.\n"
            "ᴘʟᴇᴀsᴇ ᴄʜᴇᴄᴋ ʏᴏᴜʀ ᴏꜰꜰɪᴄɪᴀʟ ᴛᴇʟᴇɢʀᴀᴍ ᴀᴘᴘ ᴏʀ sᴍs ᴀɴᴅ ᴇɴᴛᴇʀ ᴛʜᴇ ᴄᴏᴅᴇ ʜᴇʀᴇ:",
            parse_mode="HTML",
            link_preview_options=get_preview(),
            reply_markup=get_back_keyboard()
        )
        await state.set_state(AddAccountStates.waiting_for_otp)
    except Exception as e:
        await message.answer(
            f"❌ <b>ꜰᴀɪʟᴇᴅ ᴛᴏ ɪɴɪᴛɪᴀᴛᴇ ʟᴏɢɪɴ sᴇssɪᴏɴ:</b> <code>{html.escape(str(e))}</code>",
            parse_mode="HTML",
            link_preview_options=get_preview(),
            reply_markup=get_back_keyboard()
        )
        await state.clear()

@router.message(AddAccountStates.waiting_for_otp)
async def process_otp(message: Message, state: FSMContext):
    if not message.text:
        await message.answer("⚠️ <b>ᴘʟᴇᴀsᴇ sᴇɴᴅ ᴀ ᴠᴀʟɪᴅ ᴏᴛᴘ.</b>", parse_mode="HTML", reply_markup=get_back_keyboard(), link_preview_options=get_preview())
        return
    otp = message.text.strip().replace(" ", "")
    data = await state.get_data()
    phone = data.get("phone")
    client = data.get("client")
    phone_code_hash = data.get("phone_code_hash")
    proxy = data.get("proxy")
    if not client:
        await message.answer(
            "❌ <b>sᴇssɪᴏɴ ᴇxᴘɪʀᴇᴅ. ᴘʟᴇᴀsᴇ sᴛᴀʀᴛ ᴏᴠᴇʀ.</b>",
            parse_mode="HTML",
            link_preview_options=get_preview(),
            reply_markup=get_back_keyboard()
        )
        await state.clear()
        return
        
    await message.answer("⏳ <b>ᴠᴇʀɪꜰʏɪɴɢ ᴏᴛᴘ...</b>", parse_mode="HTML", link_preview_options=get_preview())
    try:
        await client.sign_in(phone, phone_code_hash, otp)
        await finalize_account_registration(message, state, client, phone, proxy)
    except SessionPasswordNeeded:
        await message.answer(
            "🔐 <b>ᴛᴡᴏ-ꜰᴀᴄᴛᴏʀ ᴀᴜᴛʜᴇɴᴛɪᴄᴀᴛɪᴏɴ (2ꜰᴀ) ɪs ᴇɴᴀʙʟᴇᴅ</b> ᴏɴ ᴛʜɪs ᴀᴄᴄᴏᴜɴᴛ.\n"
            "ᴘʟᴇᴀsᴇ ᴇɴᴛᴇʀ ʏᴏᴜʀ ᴄʟᴏᴜᴅ ᴘᴀssᴡᴏʀᴅ ʙᴇʟᴏᴡ:",
            parse_mode="HTML",
            link_preview_options=get_preview(),
            reply_markup=get_back_keyboard()
        )
        await state.set_state(AddAccountStates.waiting_for_2fa)
    except PhoneCodeInvalid:
        await message.answer(
            "❌ <b>ɪɴᴠᴀʟɪᴅ ʟᴏɢɪɴ ᴄᴏᴅᴇ.</b> ᴘʟᴇᴀsᴇ ᴇɴᴛᴇʀ ᴛʜᴇ ᴄᴏʀʀᴇᴄᴛ ᴄᴏᴅᴇ:",
            parse_mode="HTML",
            link_preview_options=get_preview(),
            reply_markup=get_back_keyboard()
        )
    except PhoneCodeExpired:
        await message.answer(
            "❌ <b>ʟᴏɢɪɴ ᴄᴏᴅᴇ ʜᴀs ᴇxᴘɪʀᴇᴅ. ᴘʟᴇᴀsᴇ ʀᴇsᴛᴀʀᴛ ᴛʜᴇ ᴘʀᴏᴄᴇss.</b>",
            parse_mode="HTML",
            link_preview_options=get_preview(),
            reply_markup=get_back_keyboard()
        )
        await client.disconnect()
        await state.clear()
    except Exception as e:
        await message.answer(
            f"❌ <b>ᴀɴ ᴇʀʀᴏʀ ᴏᴄᴄᴜʀʀᴇᴅ:</b> <code>{html.escape(str(e))}</code>",
            parse_mode="HTML",
            link_preview_options=get_preview(),
            reply_markup=get_back_keyboard()
        )
        await client.disconnect()
        await state.clear()

@router.message(AddAccountStates.waiting_for_2fa)
async def process_2fa(message: Message, state: FSMContext):
    if not message.text:
        await message.answer("⚠️ <b>ᴘʟᴇᴀsᴇ sᴇɴᴅ ᴀ ᴠᴀʟɪᴅ 2ꜰᴀ ᴄʟᴏᴜᴅ ᴘᴀssᴡᴏʀᴅ.</b>", parse_mode="HTML", reply_markup=get_back_keyboard(), link_preview_options=get_preview())
        return
    password = message.text.strip()
    data = await state.get_data()
    phone = data.get("phone")
    client = data.get("client")
    proxy = data.get("proxy")
    if not client:
        await message.answer(
            "❌ <b>sᴇssɪᴏɴ ᴇxᴘɪʀᴇᴅ. ᴘʟᴇᴀsᴇ sᴛᴀʀᴛ ᴏᴠᴇʀ.</b>",
            parse_mode="HTML",
            link_preview_options=get_preview(),
            reply_markup=get_back_keyboard()
        )
        await state.clear()
        return
        
    await message.answer("⏳ <b>ᴄʜᴇᴄᴋɪɴɢ 2ꜰᴀ ᴄʟᴏᴜᴅ ᴘᴀssᴡᴏʀᴅ...</b>", parse_mode="HTML", link_preview_options=get_preview())
    try:
        await client.check_password(password)
        await finalize_account_registration(message, state, client, phone, proxy)
    except (PasswordHashInvalid, Exception) as e:
        await message.answer(
            "❌ <b>ɪɴᴠᴀʟɪᴅ 2ꜰᴀ ᴄʟᴏᴜᴅ ᴘᴀssᴡᴏʀᴅ.</b> ᴘʟᴇᴀsᴇ ᴛʀʏ ᴀɢᴀɪɴ:",
            parse_mode="HTML",
            link_preview_options=get_preview(),
            reply_markup=get_back_keyboard()
        )

async def finalize_account_registration(message: Message, state: FSMContext, client, phone, proxy):
    try:
        profile_name = "ᴜɴᴋɴᴏᴡɴ"
        try:
            me = await client.get_me()
            if me:
                first = me.first_name or ""
                last = me.last_name or ""
                profile_name = " ".join([p for p in [first, last] if p.strip()]) or me.username or "ᴜɴᴋɴᴏᴡɴ"
        except Exception:
            pass
            
        session_str = await client.export_session_string()
        encrypted_session = encrypt_data(session_str)
        await client.disconnect()
        
        success = await save_account(
            phone=phone,
            encrypted_session=encrypted_session,
            user_id=message.from_user.id,
            proxy=proxy,
            profile_name=profile_name
        )
        
        if success:
            proxy_info = f"<code>{html.escape(proxy['hostname'])}:{proxy['port']}</code>" if proxy else "ɴᴏɴᴇ (ᴅɪʀᴇᴄᴛ)"
            await message.answer(
                f"✅ <b>ᴀᴄᴄᴏᴜɴᴛ ᴀᴅᴅᴇᴅ sᴜᴄᴄᴇssꜰᴜʟʟʏ!</b>\n\n"
                f"📱 <b>ᴘʜᴏɴᴇ:</b> <code>{html.escape(phone)}</code>\n"
                f"🔒 <b>sᴇssɪᴏɴ sᴛʀɪɴɢ:</b> ᴇɴᴄʀʏᴘᴛᴇᴅ &amp; sᴀᴠᴇᴅ sᴇᴄᴜʀᴇʟʏ.\n"
                f"🌐 <b>ʙᴏᴜɴᴅ ᴘʀᴏxʏ:</b> {proxy_info}\n\n"
                f"ʏᴏᴜ ᴄᴀɴ ɴᴏᴡ ʀᴇᴛʀɪᴇᴠᴇ ᴏᴛᴘ ꜰᴏʀ ʟᴏɢɪɴ ᴜsɪɴɢ ᴛʜᴇ ɪɴʟɪɴᴇ ᴘᴀɴᴇʟ.",
                parse_mode="HTML",
                link_preview_options=get_preview(),
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text=make_small_caps("back to main menu"), callback_data="menu:main")]
                ])
            )
        else:
            await message.answer(
                "❌ <b>ᴇʀʀᴏʀ ᴏᴄᴄᴜʀʀᴇᴅ ᴡʜɪʟᴇ sᴀᴠɪɴɢ ᴛᴏ ᴍᴏɴɢᴏᴅʙ. ᴘʟᴇᴀsᴇ ᴄʜᴇᴄᴋ ʟᴏɢs.</b>",
                parse_mode="HTML",
                link_preview_options=get_preview(),
                reply_markup=get_back_keyboard()
            )
    except Exception as e:
        await message.answer(
            f"❌ <b>ꜰᴀɪʟᴇᴅ ᴛᴏ ꜰɪɴᴀʟɪᴢᴇ ᴀᴄᴄᴏᴜɴᴛ:</b> <code>{html.escape(str(e))}</code>",
            parse_mode="HTML",
            link_preview_options=get_preview(),
            reply_markup=get_back_keyboard()
        )
        try: await client.disconnect()
        except: pass
    finally:
        await state.clear()
