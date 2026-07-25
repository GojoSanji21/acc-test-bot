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
import os
import io
import zipfile
import shutil
import sqlite3
import struct
import base64
import logging
import html
from pathlib import Path
from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from config import API_ID, API_HASH
from database import save_account
from helpers import get_random_proxy, create_pyrogram_client, encrypt_data, normalize_session_string
from pyrogram import Client

# Pyrogram exceptions
from pyrogram.errors import (
    SessionPasswordNeeded,
    PhoneCodeInvalid,
    PhoneCodeExpired,
    PasswordHashInvalid,
    AuthKeyInvalid
)

logger = logging.getLogger("TGStorageBot.plugins.add_account")
router = Router()

class AddAccountStates(StatesGroup):
    waiting_for_phone = State()
    waiting_for_otp = State()
    waiting_for_2fa = State()
    waiting_for_string_or_file = State()

def get_back_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 ʙᴀᴄᴋ ᴛᴏ ᴍᴇɴᴜ", callback_data="menu:cancel_add")]
    ])

def get_add_account_choice_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton(text="📱 ᴘʜᴏɴᴇ (ᴏᴛᴘ)", callback_data="add_acc:phone")],
        [InlineKeyboardButton(text="📁 ᴜᴘʟᴏᴀᴅ sᴛʀɪɴɢ / ꜰɪʟᴇ", callback_data="add_acc:upload")],
        [InlineKeyboardButton(text="🔙 ᴄᴀɴᴄᴇʟ", callback_data="menu:cancel_add")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

# ----------------- TELETHON TO PYROGRAM CONVERTER -----------------
def parse_sqlite_to_pyrogram_string(db_path: str, fallback_api_id: int) -> str:
    """Safely extracts SQLite session data and converts it into a Pyrogram String."""
    fallback_api_id = int(fallback_api_id) if fallback_api_id else 6
    
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        
        # Check if the DB is Telethon (has 'entities' table) or Pyrogram
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='entities'")
        is_telethon = cursor.fetchone() is not None
        
        if is_telethon:
            # Telethon Extraction Logic
            cursor.execute("SELECT dc_id, auth_key FROM sessions")
            row = cursor.fetchone()
            if not row:
                raise ValueError("Telethon sessions table is empty.")
            dc_id, auth_key = row
            
            user_id = 9999
            try:
                cursor.execute("SELECT id FROM entities")
                ent_row = cursor.fetchone()
                if ent_row:
                    user_id = ent_row[0]
            except Exception:
                pass
                
            pyro_packed = struct.pack('>BI?256sQ?', dc_id, fallback_api_id, False, auth_key, user_id, False)
            return base64.urlsafe_b64encode(pyro_packed).decode().rstrip("=")
        else:
            # Pyrogram Extraction Logic
            cursor.execute("SELECT dc_id, api_id, test_mode, auth_key, user_id, is_bot FROM sessions")
            row = cursor.fetchone()
            if not row:
                raise ValueError("Pyrogram sessions table is empty.")
            dc_id, api_id, test_mode, auth_key, user_id, is_bot = row
            
            pyro_packed = struct.pack('>BI?256sQ?', dc_id, int(api_id) if api_id else fallback_api_id, bool(test_mode), auth_key, user_id, bool(is_bot))
            return base64.urlsafe_b64encode(pyro_packed).decode().rstrip("=")
# ------------------------------------------------------------------

@router.callback_query(F.data == "menu:add_account")
async def start_add_account_callback(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.answer()
    await state.clear()
    await callback_query.message.edit_text(
        "➕ <b>ᴀᴅᴅ ᴀᴄᴄᴏᴜɴᴛ</b>\n\n"
        "ᴄʜᴏᴏsᴇ ʜᴏᴡ ᴛᴏ ᴀᴅᴅ:",
        parse_mode="HTML",
        reply_markup=get_add_account_choice_keyboard()
    )

@router.message(Command("add_account"))
async def start_add_account(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "➕ <b>ᴀᴅᴅ ᴀᴄᴄᴏᴜɴᴛ</b>\n\n"
        "ᴄʜᴏᴏsᴇ ʜᴏᴡ ᴛᴏ ᴀᴅᴅ:",
        parse_mode="HTML",
        reply_markup=get_add_account_choice_keyboard()
    )

@router.callback_query(F.data == "add_acc:phone")
async def add_account_phone_callback(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.answer()
    await callback_query.message.edit_text(
        "📱 <b>ᴘʟᴇᴀsᴇ ᴇɴᴛᴇʀ ᴛʜᴇ ᴛᴇʟᴇɢʀᴀᴍ ᴘʜᴏɴᴇ ɴᴜᴍʙᴇʀ</b> ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ᴀᴅᴅ.\n"
        "ɪɴᴄʟᴜᴅᴇ ᴛʜᴇ ᴄᴏᴜɴᴛʀʏ ᴄᴏᴅᴇ (ᴇ.ɢ., <code>+1234567890</code> ᴏʀ <code>+919876543210</code>):\n\n"
        "ᴘʀᴇss ᴛʜᴇ ʙᴜᴛᴛᴏɴ ʙᴇʟᴏᴡ ᴀᴛ ᴀɴʏ ᴛɪᴍᴇ ᴛᴏ ᴄᴀɴᴄᴇʟ.",
        parse_mode="HTML",
        reply_markup=get_back_keyboard()
    )
    await state.set_state(AddAccountStates.waiting_for_phone)

@router.callback_query(F.data == "add_acc:upload")
async def add_account_upload_callback(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.answer()
    await callback_query.message.edit_text(
        "📁 <b>ᴜᴘʟᴏᴀᴅ sᴛʀɪɴɢ / ꜰɪʟᴇ</b>\n\n"
        "👉 <b>ᴘʟᴇᴀsᴇ sᴇɴᴅ ʏᴏᴜʀ Pyrogram sᴇssɪᴏɴ sᴛʀɪɴɢ</b> as a text message or a <code>.txt</code> file.\n\n"
        "👉 Alternatively, you can <b>upload a physical <code>.session</code> SQLite file</b> or a <code>.zip</code> archive.",
        parse_mode="HTML",
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
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 ʙᴀᴄᴋ ᴛᴏ ᴍᴀɪɴ ᴍᴇɴᴜ", callback_data="menu:main")]
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
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 ʙᴀᴄᴋ ᴛᴏ ᴍᴀɪɴ ᴍᴇɴᴜ", callback_data="menu:main")]
        ])
    )

@router.message(AddAccountStates.waiting_for_string_or_file)
async def process_string_or_file_upload(message: Message, state: FSMContext):
    session_str = None
    file_path_to_clean = None

    try:
        if message.document:
            file_id = message.document.file_id
            file_name = message.document.file_name or ""
            temp_dir = Path("temp_uploads")
            temp_dir.mkdir(exist_ok=True)
            dest_path = temp_dir / f"uploaded_{message.from_user.id}_{file_name}"
            file_path_to_clean = dest_path
            
            bot_obj = message.bot
            await bot_obj.download(file_id, destination=str(dest_path))
            
            if file_name.lower().endswith(".zip"):
                status_msg = await message.answer("⚙️ ᴇxᴛʀᴀᴄᴛɪɴɢ ᴀɴᴅ ᴘᴀʀsɪɴɢ <code>.zip</code> ᴀʀᴄʜɪᴠᴇ...", parse_mode="HTML")
                zip_extract_dir = temp_dir / f"extracted_{message.from_user.id}_{os.urandom(4).hex()}"
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
                                        content = f.read()
                                    found_strings = re.findall(r"[a-zA-Z0-9+\-_=/]{100,}", content)
                                    if found_strings:
                                        for s in found_strings:
                                            sessions_to_import.append(("string", s, p.name, None))
                                    else:
                                        parsing_errors.append(f"{p.name} (no string found)")
                                except Exception as txt_err:
                                    parsing_errors.append(f"{p.name} (read err: {str(txt_err)[:40]})")
                    
                    if not sessions_to_import:
                        await status_msg.edit_text(
                            "❌ <b>ɴᴏ ᴠᴀʟɪᴅ sᴇssɪᴏɴs ꜰᴏᴜɴᴅ ɪɴ ᴛʜᴇ ᴢɪᴘ ᴀʀᴄʜɪᴠᴇ.</b>",
                            parse_mode="HTML", reply_markup=get_back_keyboard()
                        )
                        return

                    unique_sessions = []
                    seen_strings = set()
                    for s_type, s_data, s_name, s_workdir in sessions_to_import:
                        dedup_key = f"{s_workdir}/{s_data}" if s_type == "file" else s_data
                        if dedup_key not in seen_strings:
                            seen_strings.add(dedup_key)
                            unique_sessions.append((s_type, s_data, s_name, s_workdir))

                    success_count = 0
                    expired_sessions = [] 
                    other_failed_sessions = [] 
                    import time
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
                                f"⏳ <b>ʙᴜʟᴋ ɪᴍᴘᴏʀᴛ ɪɴ ᴘʀᴏɢʀᴇss...</b>\n\n"
                                f"📈 <b>ᴘʀᴏɢʀᴇss:</b> {make_progress_bar(i - 1, total_sessions)} (<code>{i - 1} / {total_sessions}</code>)\n"
                                f"━━━━━━━━━━━━━━━━━━━━━\n"
                                f"✅ <b>sᴜᴄᴄᴇss:</b> <code>{success_count}</code>\n"
                                f"🔴 <b>ᴇxᴘɪʀᴇᴅ:</b> <code>{len(expired_sessions)}</code>\n"
                                f"⚠️ <b>ꜰᴀɪʟᴇᴅ:</b> <code>{len(other_failed_sessions)}</code>\n"
                                f"⏳ <b>ᴘᴇɴᴅɪɴɢ:</b> <code>{total_sessions - (i - 1)}</code>\n\n"
                                f"⚡ <i>Processing: {html.escape(source_name)}...</i>"
                            )
                            try:
                                await status_msg.edit_text(progress_text, parse_mode="HTML")
                                last_edit_time = now_time
                            except Exception:
                                pass
                                
                        proxy, proxy_error = get_random_proxy()
                        temp_name = f"uploaded_sess_zip_{message.from_user.id}_{i}"

                        if s_type == "file":
                            # 🚀 THE FIX: Use our converter instead of Pyrogram file init!
                            session_file_path = os.path.join(s_workdir, f"{s_data}.session")
                            try:
                                converted_str = parse_sqlite_to_pyrogram_string(session_file_path, API_ID)
                                client = create_pyrogram_client(session_name=temp_name, session_string=converted_str, proxy=proxy)
                            except Exception as e:
                                logger.error(f"Failed to convert session {source_name}: {e}")
                                other_failed_sessions.append((source_name, f"DB Error: {e}"))
                                continue
                        else:
                            s_data = normalize_session_string(s_data)
                            client = create_pyrogram_client(session_name=temp_name, session_string=s_data, proxy=proxy)

                        try:
                            await client.connect()
                            me = await client.get_me()
                            if not me:
                                raise ValueError("Could not retrieve account identity from get_me()")
                            phone = getattr(me, "phone_number", None)
                            if not phone:
                                phone_match = re.search(r'\d+', source_name)
                                phone = f"+{phone_match.group(0)}" if phone_match else f"+{me.id}"
                            else:
                                phone = f"+{phone}" if not phone.startswith("+") else phone
                                
                            first, last = me.first_name or "", me.last_name or ""
                            profile_name = " ".join([p for p in [first, last] if p.strip()]) or me.username or "ᴜɴᴋɴᴏᴡɴ"
                            
                            exported_session_str = await client.export_session_string()
                            encrypted_session = encrypt_data(exported_session_str)
                            await client.disconnect()
                            
                            saved = await save_account(
                                phone=phone, encrypted_session=encrypted_session,
                                user_id=message.from_user.id, proxy=proxy, profile_name=profile_name
                            )
                            if saved: success_count += 1
                            else: other_failed_sessions.append((source_name, "Failed to save to MongoDB"))
                        except AuthKeyInvalid:
                            expired_sessions.append((source_name, "Session Expired / Revoked"))
                        except Exception as conn_err:
                            err_str = str(conn_err)
                            if "deactivated" in err_str.lower() or "deactive" in err_str.lower():
                                expired_sessions.append((source_name, "Account Deactivated"))
                            else:
                                other_failed_sessions.append((source_name, err_str))
                        finally:
                            try: await client.disconnect()
                            except: pass

                    summary_text = (
                        "📦 <b>ʙᴜʟᴋ ɪᴍᴘᴏʀᴛ sᴜᴍᴍᴀʀʏ</b>\n"
                        "━━━━━━━━━━━━━━━━━━━━━\n"
                        f"✅ <b>sᴜᴄᴄᴇssꜰᴜʟʟʏ ɪᴍᴘᴏʀᴛᴇᴅ:</b> <code>{success_count} / {len(unique_sessions)}</code> accounts\n"
                    )
                    if expired_sessions:
                        summary_text += f"\n🔴 <b>ᴇxᴘɪʀᴇᴅ / ɪɴᴠᴀʟɪᴅ:</b> <code>{len(expired_sessions)}</code>\n"
                    if other_failed_sessions:
                        summary_text += f"\n⚠️ <b>ᴏᴛʜᴇʀ ꜰᴀɪʟᴜʀᴇs:</b> <code>{len(other_failed_sessions)}</code>\n"
                    if not expired_sessions and not other_failed_sessions:
                        summary_text += "\n🟢 <b>All sessions imported successfully!</b>"
                        
                    await status_msg.delete()
                    await message.answer(
                        summary_text, parse_mode="HTML",
                        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                            [InlineKeyboardButton(text="🔙 ʙᴀᴄᴋ ᴛᴏ ᴍᴀɪɴ ᴍᴇɴᴜ", callback_data="menu:main")]
                        ])
                    )
                    await state.clear()
                    return
                except Exception as zip_err:
                    await status_msg.edit_text(f"❌ <b><b>ꜰᴀɪʟᴇᴅ ᴛᴏ ᴘʀᴏᴄᴇss ᴢɪᴘ:</b></b> <code>{html.escape(str(zip_err))}</code>", parse_mode="HTML", reply_markup=get_back_keyboard())
                    return
                finally:
                    if zip_extract_dir.exists():
                        try: shutil.rmtree(zip_extract_dir)
                        except: pass

            elif file_name.lower().endswith(".session"):
                status_msg = await message.answer("⚙️ ᴘᴀʀsɪɴɢ sǫʟɪᴛᴇ <code>.session</code> ꜰɪʟᴇ...", parse_mode="HTML")
                try:
                    proxy, proxy_error = get_random_proxy()
                    
                    # 🚀 THE FIX: Convert physical file to String Session first!
                    session_str = parse_sqlite_to_pyrogram_string(str(dest_path), API_ID)
                    
                    temp_name = f"sess_uploaded_{message.from_user.id}"
                    client = create_pyrogram_client(session_name=temp_name, session_string=session_str, proxy=proxy)
                    await client.connect()
                    
                    me = await client.get_me()
                    if not me:
                        raise ValueError("Could not retrieve account identity from get_me()")
                        
                    phone = getattr(me, "phone_number", None)
                    if not phone:
                        phone_match = re.search(r'\d+', dest_path.stem)
                        phone = f"+{phone_match.group(0)}" if phone_match else f"+{me.id}"
                    else:
                        phone = f"+{phone}" if not phone.startswith("+") else phone
                        
                    first, last = me.first_name or "", me.last_name or ""
                    profile_name = " ".join([p for p in [first, last] if p.strip()]) or me.username or "ᴜɴᴋɴᴏᴡɴ"
                    
                    session_str_final = await client.export_session_string()
                    encrypted_session = encrypt_data(session_str_final)
                    await client.disconnect()
                    
                    success = await save_account(
                        phone=phone, encrypted_session=encrypted_session,
                        user_id=message.from_user.id, proxy=proxy, profile_name=profile_name
                    )
                    await status_msg.delete()
                    
                    if success:
                        await message.answer(
                            f"✅ <b>ᴀᴄᴄᴏᴜɴᴛ ᴀᴅᴅᴇᴅ sᴜᴄᴄᴇssꜰᴜʟʟʏ!</b>\n\n"
                            f"👤 <b>ɴᴀᴍᴇ:</b> <code>{html.escape(profile_name)}</code>\n"
                            f"📱 <b>ᴘʜᴏɴᴇ:</b> <code>{html.escape(phone)}</code>\n"
                            f"ʏᴏᴜ ᴄᴀɴ ɴᴏᴡ ᴍᴀɴᴀɢᴇ ᴛʜɪs sᴇssɪᴏɴ inside the account panel.",
                            parse_mode="HTML",
                            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                [InlineKeyboardButton(text="🔙 ʙᴀᴄᴋ ᴛᴏ ᴍᴀɪɴ ᴍᴇɴᴜ", callback_data="menu:main")]
                            ])
                        )
                        await state.clear()
                    else:
                        await message.answer("❌ <b>ᴇʀʀᴏʀ ᴏᴄᴄᴜʀʀᴇᴅ ᴡʜɪʟᴇ sᴀᴠɪɴɢ.</b>", parse_mode="HTML", reply_markup=get_back_keyboard())
                    return
                except Exception as db_err:
                    await status_msg.delete()
                    await message.answer(f"❌ <b>ꜰᴀɪʟᴇᴅ ᴛᴏ ᴘᴀʀsᴇ sǫʟɪᴛᴇ sᴇssɪᴏɴ:</b> <code>{html.escape(str(db_err))}</code>", parse_mode="HTML", reply_markup=get_back_keyboard())
                    return
            else:
                try:
                    with open(dest_path, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read().strip()
                    found_strings = re.findall(r"[a-zA-Z0-9+\-_=/]{100,}", content)
                    session_str = found_strings[0] if found_strings else content
                except Exception as text_err:
                    await message.answer(f"❌ <b>ꜰᴀɪʟᴇᴅ:</b> <code>{html.escape(str(text_err))}</code>", parse_mode="HTML", reply_markup=get_back_keyboard())
                    return
        elif message.text:
            content = message.text.strip()
            found_strings = re.findall(r"[a-zA-Z0-9+\-_=/]{100,}", content)
            session_str = found_strings[0] if found_strings else content
        else:
            await message.answer("⚠️ <b>ᴘʟᴇᴀsᴇ sᴇɴᴅ ᴀ ᴠᴀʟɪᴅ sᴇssɪᴏɴ.</b>", parse_mode="HTML", reply_markup=get_back_keyboard())
            return
            
        if not session_str:
            await message.answer("⚠️ <b>ᴛʜᴇ sᴇssɪᴏɴ sᴛʀɪɴɢ ᴄᴏᴜʟᴅ ɴᴏᴛ ʙᴇ ᴇxᴛʀᴀᴄᴛᴇᴅ.</b>", parse_mode="HTML", reply_markup=get_back_keyboard())
            return
            
        session_str = normalize_session_string(session_str)
        status_msg = await message.answer("⏳ <b>ᴄᴏɴɴᴇᴄᴛɪɴɢ...</b>", parse_mode="HTML")
        proxy, proxy_error = get_random_proxy()
        
        temp_name = f"uploaded_sess_{message.from_user.id}"
        client = create_pyrogram_client(session_name=temp_name, session_string=session_str, proxy=proxy)
        try:
            await client.connect()
            me = await client.get_me()
            phone = getattr(me, "phone_number", None)
            phone = f"+{phone}" if phone and not phone.startswith("+") else f"+{me.id}" if not phone else phone
            
            first, last = me.first_name or "", me.last_name or ""
            profile_name = " ".join([p for p in [first, last] if p.strip()]) or me.username or "ᴜɴᴋɴᴏᴡɴ"
            
            encrypted_session = encrypt_data(session_str)
            await client.disconnect()
            
            success = await save_account(phone=phone, encrypted_session=encrypted_session, user_id=message.from_user.id, proxy=proxy, profile_name=profile_name)
            await status_msg.delete()
            if success:
                await message.answer(
                    f"✅ <b>ᴀᴄᴄᴏᴜɴᴛ ᴀᴅᴅᴇᴅ sᴜᴄssꜰᴜʟʟʏ!</b>\n\n"
                    f"👤 <b>ɴᴀᴍᴇ:</b> <code>{html.escape(profile_name)}</code>\n"
                    f"📱 <b>ᴘʜᴏɴᴇ:</b> <code>{html.escape(phone)}</code>",
                    parse_mode="HTML", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔙 ʙᴀᴄᴋ", callback_data="menu:main")]])
                )
                await state.clear()
        except Exception as conn_err:
            await status_msg.delete()
            await message.answer(f"❌ <b>ꜰᴀɪʟᴇᴅ:</b> <code>{html.escape(str(conn_err))}</code>", parse_mode="HTML", reply_markup=get_back_keyboard())
    finally:
        if file_path_to_clean and os.path.exists(file_path_to_clean):
            try: os.remove(file_path_to_clean)
            except: pass

@router.message(AddAccountStates.waiting_for_phone)
async def process_phone(message: Message, state: FSMContext):
    if not message.text:
        await message.answer("⚠️ ᴘʟᴇᴀsᴇ sᴇɴᴅ ᴀ ᴠᴀʟɪᴅ ᴘʜᴏɴᴇ ɴᴜᴍʙᴇʀ.", reply_markup=get_back_keyboard())
        return
    phone = message.text.strip().replace(" ", "")
    if not re.match(r"^\+\d{8,15}$", phone):
        await message.answer("⚠️ <b>ɪɴᴠᴀʟɪᴅ ᴘʜᴏɴᴇ ꜰᴏʀᴍᴀᴛ.</b>", parse_mode="HTML", reply_markup=get_back_keyboard())
        return
    proxy, proxy_error = get_random_proxy()
    if not proxy: await message.answer("⚠️ ɴᴏ ᴘʀᴏxɪᴇs ᴄᴏɴꜰɪɢᴜʀᴇᴅ. ᴘʀᴏᴄᴇᴇᴅɪɴɢ ᴡɪᴛʜ ᴅɪʀᴇᴄᴛ ᴄᴏɴɴᴇᴄᴛɪᴏɴ.", parse_mode="HTML")
    else: await message.answer(f"🌐 <b>ᴘʀᴏxʏ sᴇʟᴇᴄᴛᴇᴅ:</b> <code>{html.escape(proxy['hostname'])}:{proxy['port']}</code>", parse_mode="HTML")
    
    status_msg = await message.answer("⏳ <b><b>ᴄᴏɴɴᴇᴄᴛɪɴɢ... ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ.</b></b>", parse_mode="HTML", reply_markup=get_back_keyboard())
    try:
        session_name = f"sess_{phone.replace('+', '')}"
        client = create_pyrogram_client(session_name=session_name, proxy=proxy)
        await client.connect()
        code_info = await client.send_code(phone)
        await state.update_data(phone=phone, client=client, phone_code_hash=code_info.phone_code_hash, proxy=proxy)
        await message.answer("📨 <b>ᴏᴛᴘ sᴇɴᴛ!</b> ᴘʟᴇᴀsᴇ ᴇɴᴛᴇʀ ᴛʜᴇ ᴄᴏᴅᴇ:", parse_mode="HTML", reply_markup=get_back_keyboard())
        await state.set_state(AddAccountStates.waiting_for_otp)
    except Exception as e:
        await message.answer(f"❌ <b>ꜰᴀɪʟᴇᴅ:</b> <code>{html.escape(str(e))}</code>", parse_mode="HTML", reply_markup=get_back_keyboard())
        await state.clear()

@router.message(AddAccountStates.waiting_for_otp)
async def process_otp(message: Message, state: FSMContext):
    if not message.text: return
    otp = message.text.strip().replace(" ", "")
    data = await state.get_data()
    client = data.get("client")
    if not client:
        await message.answer("❌ <b>sᴇssɪᴏɴ ᴇxᴘɪʀᴇᴅ.</b>", parse_mode="HTML", reply_markup=get_back_keyboard())
        await state.clear()
        return
    await message.answer("⏳ <b>ᴠᴇʀɪꜰʏɪɴɢ...</b>", parse_mode="HTML")
    try:
        await client.sign_in(data.get("phone"), data.get("phone_code_hash"), otp)
        await finalize_account_registration(message, state, client, data.get("phone"), data.get("proxy"))
    except SessionPasswordNeeded:
        await message.answer("🔐 <b>2ꜰᴀ ɪs ᴇɴᴀʙʟᴇᴅ</b>. ᴘʟᴇᴀsᴇ ᴇɴᴛᴇʀ ᴘᴀssᴡᴏʀᴅ:", parse_mode="HTML", reply_markup=get_back_keyboard())
        await state.set_state(AddAccountStates.waiting_for_2fa)
    except PhoneCodeInvalid: await message.answer("❌ <b>ɪɴᴠᴀʟɪᴅ ᴄᴏᴅᴇ.</b>", parse_mode="HTML", reply_markup=get_back_keyboard())
    except PhoneCodeExpired:
        await message.answer("❌ <b>ᴄᴏᴅᴇ ᴇxᴘɪʀᴇᴅ.</b>", parse_mode="HTML", reply_markup=get_back_keyboard())
        await client.disconnect()
        await state.clear()

@router.message(AddAccountStates.waiting_for_2fa)
async def process_2fa(message: Message, state: FSMContext):
    if not message.text: return
    data = await state.get_data()
    client = data.get("client")
    if not client:
        await message.answer("❌ <b>sᴇssɪᴏɴ ᴇxᴘɪʀᴇᴅ.</b>", parse_mode="HTML", reply_markup=get_back_keyboard())
        await state.clear()
        return
    await message.answer("⏳ <b><b>ᴄʜᴇᴄᴋɪɴɢ...</b></b>", parse_mode="HTML")
    try:
        await client.check_password(message.text.strip())
        await finalize_account_registration(message, state, client, data.get("phone"), data.get("proxy"))
    except Exception:
        await message.answer("❌ <b>ɪɴᴠᴀʟɪᴅ ᴘᴀssᴡᴏʀᴅ.</b>", parse_mode="HTML", reply_markup=get_back_keyboard())

async def finalize_account_registration(message: Message, state: FSMContext, client, phone, proxy):
    try:
        me = await client.get_me()
        first, last = me.first_name or "", me.last_name or ""
        profile_name = " ".join([p for p in [first, last] if p.strip()]) or me.username or "ᴜɴᴋɴᴏᴡɴ"
        
        session_str = await client.export_session_string()
        encrypted_session = encrypt_data(session_str)
        await client.disconnect()
        
        if await save_account(phone=phone, encrypted_session=encrypted_session, user_id=message.from_user.id, proxy=proxy, profile_name=profile_name):
            await message.answer(
                f"✅ <b>ᴀᴄᴄᴏᴜɴᴛ ᴀᴅᴅᴇᴅ sᴜᴄᴄᴇssꜰᴜʟʟʏ!</b>\n\n📱 <b><b>ᴘʜᴏɴᴇ:</b></b> <code>{html.escape(phone)}</code>",
                parse_mode="HTML", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔙 ʙᴀᴄᴋ", callback_data="menu:main")]])
            )
        else: await message.answer("❌ <b>ᴇʀʀᴏʀ ᴏᴄᴄᴜʀʀᴇᴅ ᴡʜɪʟᴇ sᴀᴠɪɴɢ.</b>", parse_mode="HTML", reply_markup=get_back_keyboard())
    except Exception as e:
        await message.answer(f"❌ <b>ꜰᴀɪʟᴇᴅ:</b> <code>{html.escape(str(e))}</code>", parse_mode="HTML", reply_markup=get_back_keyboard())
    finally:
        await state.clear()
