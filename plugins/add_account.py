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
from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from config import API_ID, API_HASH
from database import save_account
from helpers import get_random_proxy, create_pyrogram_client, encrypt_data, normalize_session_string

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
    """Safely extracts SQLite session data (Telethon or Pyrogram) and converts it into a Pyrogram String."""
    import sqlite3
    import struct
    import base64
    
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
            
            # FIX: Use a dummy user_id to prevent "int too large" error caused by negative group IDs in Telethon.
            user_id = 9999 
                
            pyro_packed = struct.pack('>BI?256sQ?', dc_id, fallback_api_id, False, auth_key, user_id, False)
            return base64.urlsafe_b64encode(pyro_packed).decode().rstrip("=")
        else:
            # Pyrogram Extraction Logic
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
        "👉 Alternatively, you can <b>upload a physical <code>.session</code> SQLite file</b>.",
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
    # Send cancel message with option to go back to main menu
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
    import os
    import io
    import zipfile
    import shutil
    from pathlib import Path
    from pyrogram import Client
    from pyrogram.storage.file_storage import FileStorage
    from pyrogram.storage.memory_storage import MemoryStorage

    session_str = None
    file_path_to_clean = None

    try:
        # Handle document/file upload
        if message.document:
            file_id = message.document.file_id
            file_name = message.document.file_name or ""
            
            # Create a secure temp directory
            temp_dir = Path("temp_uploads")
            temp_dir.mkdir(exist_ok=True)
            dest_path = temp_dir / f"uploaded_{message.from_user.id}_{file_name}"
            file_path_to_clean = dest_path
            
            # Download file
            bot_obj = message.bot
            await bot_obj.download(file_id, destination=str(dest_path))
            
            if file_name.lower().endswith(".zip"):
                status_msg = await message.answer("⚙️ ᴇxᴛʀᴀᴄᴛɪɴɢ ᴀɴᴅ ᴘᴀʀsɪɴɢ <code>.zip</code> ᴀʀᴄʜɪᴠᴇ...", parse_mode="HTML")
                zip_extract_dir = temp_dir / f"extracted_{message.from_user.id}_{os.urandom(4).hex()}"
                try:
                    # Create a secure temp directory for zip extraction
                    zip_extract_dir.mkdir(exist_ok=True, parents=True)
                    
                    # Extract zip with secure in-memory Zip Slip path traversal protection
                    with zipfile.ZipFile(dest_path, 'r') as zip_ref:
                        safe_members = []
                        for member in zip_ref.infolist():
                            # Prevent directory traversal vulnerability (Zip Slip)
                            filename = member.filename
                            normalized = filename.replace("\\", "/")
                            if normalized.startswith("/") or ".." in normalized.split("/"):
                                logger.warning(f"Path traversal check failed for zip member: {filename}")
                                continue
                            safe_members.append(member)
                        zip_ref.extractall(zip_extract_dir, members=safe_members)
                        
                    # We will collect all potential session strings and their sources
                    sessions_to_import = [] # list of tuples: (session_string, source_name)
                    all_found_files = [] # list of tuples: (file_name, size)
                    parsing_errors = [] # list of strings
                    
                    # Recursively walk through the extracted files using highly reliable os.walk
                    for root, dirs, files in os.walk(zip_extract_dir):
                        for file in files:
                            p = Path(root) / file
                            file_size = p.stat().st_size if p.exists() else 0
                            all_found_files.append((p.name, file_size))
                            if p.suffix.lower() == ".session":
                                # Treat as a physical file, don't try to read it
                                sessions_to_import.append(("file", p.stem, p.name, str(p.parent)))
                            else:
                                # Treat any non-.session file as a text candidate to find potential session strings
                                try:
                                    with open(p, "r", encoding="utf-8", errors="ignore") as f:
                                        content = f.read()
                                    # Use a regex to find all potential base64 strings of length >= 100 including standard and url-safe characters
                                    found_strings = re.findall(r"[a-zA-Z0-9+\-_=/]{100,}", content)
                                    if found_strings:
                                        for s in found_strings:
                                            sessions_to_import.append(("string", s, p.name, None))
                                    else:
                                        parsing_errors.append(f"{p.name} (no session string found)")
                                except Exception as txt_err:
                                    logger.error(f"Failed to read text file {p.name} from ZIP: {txt_err}")
                                    parsing_errors.append(f"{p.name} (read err: {str(txt_err)[:40]})")
                    
                    if not sessions_to_import:
                        files_list_str = ""
                        for f_name, f_size in all_found_files[:15]:
                            files_list_str += f"• <code>{html.escape(f_name)}</code> ({f_size} bytes)\n"
                        if len(all_found_files) > 15:
                            files_list_str += f"<i>...and {len(all_found_files) - 15} more files</i>\n"
                        errors_list_str = ""
                        for err_item in parsing_errors[:15]:
                            errors_list_str += f"• <code>{html.escape(err_item)}</code>\n"
                        if len(parsing_errors) > 15:
                            errors_list_str += f"<i>...and {len(parsing_errors) - 15} more errors</i>\n"
                        error_details = (
                            "❌ <b>ɴᴏ ᴠᴀʟɪᴅ sᴇssɪᴏɴs ꜰᴏᴜɴᴅ ɪɴ ᴛʜᴇ ᴢɪᴘ ᴀʀᴄʜɪᴠᴇ.</b>\n\n"
                            "👉 Please make sure the ZIP contains <code>.session</code> SQLite files or text files with valid session strings.\n\n"
                            f"📁 <b>Files found in ZIP ({len(all_found_files)}):</b>\n"
                            f"{files_list_str or '• None (ZIP may be empty or failed extraction)'}\n"
                            f"⚠️ <b>Parsing logs/errors:</b>\n"
                            f"{errors_list_str or '• None'}"
                        )
                        await status_msg.edit_text(
                            error_details,
                            parse_mode="HTML",
                            reply_markup=get_back_keyboard()
                        )
                        return
                    
                    # Deduplicate sessions_to_import based on session data
                    unique_sessions = []
                    seen_strings = set()
                    for s_type, s_data, s_name, s_workdir in sessions_to_import:
                        # For files, deduplicate by the full path (s_workdir + s_data)
                        # For strings, deduplicate by the string itself
                        dedup_key = f"{s_workdir}/{s_data}" if s_type == "file" else s_data
                        if dedup_key not in seen_strings:
                            seen_strings.add(dedup_key)
                            unique_sessions.append((s_type, s_data, s_name, s_workdir))
                    
                    success_count = 0
                    expired_sessions = []  # list of tuples: (source_name, error_reason)
                    other_failed_sessions = [] # list of tuples: (source_name, error_reason)
                    
                    import time
                    total_sessions = len(unique_sessions)
                    last_edit_time = time.time()
                    
                    # Define an inline progress bar helper
                    def make_progress_bar(current: int, total: int) -> str:
                        if total <= 0:
                            return "░" * 10
                        filled = int(10 * current // total)
                        bar = "■" * filled + "□" * (10 - filled)
                        pct = int((current / total) * 100)
                        return f"<code>[{bar}]</code> <b>{pct}%</b>"
                    
                    for i, (s_type, s_data, source_name, s_workdir) in enumerate(unique_sessions, 1):
                        # Throttle live updates to prevent hitting Telegram API rate limits (flood waits)
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
                            except Exception as edit_err:
                                logger.warning(f"Failed to edit progress status: {edit_err}")
                                
                        proxy, proxy_error = get_random_proxy()
                        temp_name = f"uploaded_sess_zip_{message.from_user.id}_{i}"

                        if s_type == "file":
                            # 🚀 MODIFIED: Use our custom converter instead of passing workdir to Client
                            session_file_path = os.path.join(s_workdir, f"{s_data}.session")
                            try:
                                converted_str = parse_sqlite_to_pyrogram_string(session_file_path, API_ID)
                                client = create_pyrogram_client(session_name=temp_name, session_string=converted_str, proxy=proxy)
                            except Exception as e:
                                logger.error(f"Failed to convert session {source_name}: {e}")
                                other_failed_sessions.append((source_name, f"DB Error: {e}"))
                                continue
                        else:
                            # For strings, normalize and use existing helper
                            s_data = normalize_session_string(s_data)
                            client = create_pyrogram_client(session_name=temp_name, session_string=s_data, proxy=proxy)
                            
                        try:
                            await client.connect()
                            me = await client.get_me()
                            if not me:
                                raise ValueError("Could not retrieve account identity from get_me()")
                            
                            phone = getattr(me, "phone_number", None)
                            if not phone:
                                import re
                                phone_match = re.search(r'\d+', s_data if s_type == "file" else temp_name)
                                if phone_match:
                                    phone = f"+{phone_match.group(0)}"
                                else:
                                    phone = f"+{me.id}"
                            else:
                                if not phone.startswith("+"):
                                    phone = f"+{phone}"
                                    
                            profile_name = "ᴜɴᴋɴᴏᴡɴ"
                            first = me.first_name or ""
                            last = me.last_name or ""
                            name_parts = [first, last]
                            profile_name = " ".join([p for p in name_parts if p.strip()]) or me.username or "ᴜɴᴋɴᴏᴡɴ"
                            
                            # Get session string to store it uniformly in DB
                            exported_session_str = await client.export_session_string()
                            
                            # Encrypt and save securely
                            encrypted_session = encrypt_data(exported_session_str)
                            await client.disconnect()
                            
                            saved = await save_account(
                                phone=phone,
                                encrypted_session=encrypted_session,
                                user_id=message.from_user.id,
                                proxy=proxy,
                                profile_name=profile_name
                            )
                            if saved:
                                success_count += 1
                            else:
                                other_failed_sessions.append((source_name, "Failed to save to MongoDB"))
                        except AuthKeyInvalid:
                            logger.error(f"Session {source_name} is expired/revoked: AuthKeyInvalid")
                            expired_sessions.append((source_name, "Session Expired / Revoked"))
                            try:
                                await client.disconnect()
                            except:
                                pass
                        except Exception as conn_err:
                            err_str = str(conn_err)
                            logger.error(f"Failed to connect session {source_name}: {conn_err}")
                            if "deactivated" in err_str.lower() or "deactive" in err_str.lower():
                                expired_sessions.append((source_name, "Account Deactivated by Telegram"))
                            else:
                                other_failed_sessions.append((source_name, err_str))
                            try:
                                await client.disconnect()
                            except:
                                pass
                                
                    # Prepare final summary message
                    summary_text = (
                        "📦 <b>ʙᴜʟᴋ ɪᴍᴘᴏʀᴛ sᴜᴍᴍᴀʀʏ</b>\n"
                        "━━━━━━━━━━━━━━━━━━━━━\n"
                        f"✅ <b>sᴜᴄᴄᴇssꜰᴜʟʟʏ ɪᴍᴘᴏʀᴛᴇᴅ:</b> <code>{success_count} / {len(unique_sessions)}</code> accounts\n"
                    )
                    if expired_sessions:
                        summary_text += f"\n🔴 <b>ᴇxᴘɪʀᴇᴅ / ɪɴᴠᴀʟɪᴅ sᴇssɪᴏɴs:</b> <code>{len(expired_sessions)}</code>\n"
                        for f_name, f_reason in expired_sessions[:15]:
                            summary_text += f"• <code>{html.escape(f_name)}</code>: <code>{html.escape(f_reason)}</code>\n"
                        if len(expired_sessions) > 15:
                            summary_text += f"<i>...and {len(expired_sessions) - 15} more</i>\n"
                    if other_failed_sessions:
                        summary_text += f"\n⚠️ <b>ᴏᴛʜᴇʀ ꜰᴀɪʟᴜʀᴇs:</b> <code>{len(other_failed_sessions)}</code>\n"
                        for f_name, f_reason in other_failed_sessions[:10]:
                            summary_text += f"• <code>{html.escape(f_name)}</code>: <code>{html.escape(f_reason)}</code>\n"
                        if len(other_failed_sessions) > 10:
                            summary_text += f"<i>...and {len(other_failed_sessions) - 10} more</i>\n"
                    if not expired_sessions and not other_failed_sessions:
                        summary_text += "\n🟢 <b>All sessions imported successfully!</b>"
                        
                    await status_msg.delete()
                    await message.answer(
                        summary_text,
                        parse_mode="HTML",
                        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                            [InlineKeyboardButton(text="🔙 ʙᴀᴄᴋ ᴛᴏ ᴍᴀɪɴ ᴍᴇɴᴜ", callback_data="menu:main")]
                        ])
                    )
                    await state.clear()
                    return
                except Exception as zip_err:
                    logger.exception("Error processing ZIP file")
                    await status_msg.edit_text(
                        f"❌ <b><b>ꜰᴀɪʟᴇᴅ ᴛᴏ ᴘʀᴏᴄᴇss ᴢɪᴘ:</b></b> <code>{html.escape(str(zip_err))}</code>",
                        parse_mode="HTML",
                        reply_markup=get_back_keyboard()
                    )
                    return
                finally:
                    # Always clean up extracted files
                    if zip_extract_dir.exists():
                        try:
                            shutil.rmtree(zip_extract_dir)
                        except Exception as clean_err:
                            logger.error(f"Failed to clean up extracted ZIP dir: {clean_err}")
                            
            elif file_name.lower().endswith(".session"):
                status_msg = await message.answer("⚙️ ᴘᴀʀsɪɴɢ sǫʟɪᴛᴇ <code>.session</code> ꜰɪʟᴇ...", parse_mode="HTML")
                try:
                    session_db_name = dest_path.stem
                    proxy, proxy_error = get_random_proxy()

                    # 🚀 MODIFIED: Replaced huge manual SQLite block with our new clean converter
                    try:
                        session_str = parse_sqlite_to_pyrogram_string(str(dest_path), API_ID)
                        temp_name = f"sess_telethon_{message.from_user.id}"
                        client = create_pyrogram_client(session_name=temp_name, session_string=session_str, proxy=proxy)
                        await client.connect()
                    except Exception as parse_e:
                        raise ValueError(f"Could not find or parse session data: {parse_e}")

                    me = await client.get_me()

                    if not me:
                        raise ValueError("Could not retrieve account identity from get_me()")
                    phone = getattr(me, "phone_number", None)
                    if not phone:
                        # Extract the phone number directly from the uploaded file's name as a fallback
                        import re
                        phone_match = re.search(r'\d+', session_db_name)
                        if phone_match:
                            phone = f"+{phone_match.group(0)}"
                        else:
                            phone = f"+{me.id}"
                    else:
                        if not phone.startswith("+"):
                            phone = f"+{phone}"
                            
                    profile_name = "ᴜɴᴋɴᴏᴡɴ"
                    first = me.first_name or ""
                    last = me.last_name or ""
                    name_parts = [first, last]
                    profile_name = " ".join([p for p in name_parts if p.strip()]) or me.username or "ᴜɴᴋɴᴏᴡɴ"
                    
                    # Get session string to store it uniformly in DB
                    session_str_final = await client.export_session_string()

                    # Encrypt and save securely
                    encrypted_session = encrypt_data(session_str_final)
                    await client.disconnect()
                    
                    success = await save_account(
                        phone=phone,
                        encrypted_session=encrypted_session,
                        user_id=message.from_user.id,
                        proxy=proxy,
                        profile_name=profile_name
                    )
                    await status_msg.delete()
                    if success:
                        proxy_info = f"<code>{html.escape(proxy['hostname'])}:{proxy['port']}</code>" if proxy else "ɴᴏɴᴇ (ᴅɪʀᴇᴄᴛ)"
                        await message.answer(
                            f"✅ <b>ᴀᴄᴄᴏᴜɴᴛ ᴀᴅᴅᴇᴅ sᴜᴄᴄᴇssꜰᴜʟʟʏ ᴠɪᴀ ᴜᴘʟᴏᴀᴅ!</b>\n\n"
                            f"👤 <b>ɴᴀᴍᴇ:</b> <code>{html.escape(profile_name)}</code>\n"
                            f"📱 <b>ᴘʜᴏɴᴇ:</b> <code>{html.escape(phone)}</code>\n"
                            f"🔒 <b>sᴇssɪᴏɴ sᴛʀɪɴɢ:</b> ᴇɴᴄʀʏᴘᴛᴇᴅ &amp; sᴀᴠᴇᴅ sᴇᴄᴜʀᴇʟʏ.\n"
                            f"🌐 <b>ʙᴏᴜɴᴅ ᴘʀᴏxʏ:</b> {proxy_info}\n\n"
                            f"ʏᴏᴜ ᴄᴀɴ ɴᴏᴡ ᴍᴀɴᴀɢᴇ ᴛʜɪs sᴇssɪᴏɴ inside the account panel.",
                            parse_mode="HTML",
                            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                [InlineKeyboardButton(text="🔙 ʙᴀᴄᴋ ᴛᴏ ᴍᴀɪɴ ᴍᴇɴᴜ", callback_data="menu:main")]
                            ])
                        )
                        await state.clear()
                    else:
                        await message.answer(
                            "❌ <b>ᴇʀʀᴏʀ ᴏᴄᴄᴜʀʀᴇᴅ ᴡʜɪʟᴇ sᴀᴠɪɴɢ ᴛᴏ ᴍᴏɴɢᴏᴅʙ. ᴘʟᴇᴀsᴇ ᴄʜᴇᴄᴋ ʟᴏɢs.</b>",
                            parse_mode="HTML",
                            reply_markup=get_back_keyboard()
                        )
                    return
                except Exception as db_err:
                    logger.error(f"Failed to parse SQLite session file {dest_path.name}: {db_err}")
                    await status_msg.delete()
                    await message.answer(
                        f"❌ <b>ꜰᴀɪʟᴇᴅ ᴛᴏ ᴘᴀʀsɪɴɢ sǫʟɪᴛᴇ sᴇssɪᴏɴ:</b> <code>{html.escape(str(db_err))}</code>",
                        parse_mode="HTML",
                        reply_markup=get_back_keyboard()
                    )
                    try:
                        await client.disconnect()
                    except:
                        pass
                    return
            else:
                # Text or txt file containing session string
                try:
                    with open(dest_path, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read().strip()
                    # Extract the first matching valid-looking base64 session string
                    found_strings = re.findall(r"[a-zA-Z0-9+\-_=/]{100,}", content)
                    if found_strings:
                        session_str = found_strings[0]
                    else:
                        session_str = content
                except Exception as text_err:
                    await message.answer(
                        f"❌ <b>ꜰᴀɪʟᴇᴅ ᴛᴏ ʀᴇᴀᴅ ꜰɪʟᴇ:</b> <code>{html.escape(str(text_err))}</code>",
                        parse_mode="HTML",
                        reply_markup=get_back_keyboard()
                    )
                    return
                    
        elif message.text:
            content = message.text.strip()
            # Extract the first matching valid-looking base64 session string
            found_strings = re.findall(r"[a-zA-Z0-9+\-_=/]{100,}", content)
            if found_strings:
                session_str = found_strings[0]
            else:
                session_str = content
        else:
            await message.answer(
                "⚠️ <b>ᴘʟᴇᴀsᴇ sᴇɴᴅ ᴀ ᴠᴀʟɪᴅ sᴇssɪᴏɴ sᴛʀɪɴɢ ᴏʀ ᴜᴘʟᴏᴀᴅ ᴀ ꜰɪʟᴇ.</b>",
                parse_mode="HTML",
                reply_markup=get_back_keyboard()
            )
            return
            
        if not session_str:
            await message.answer(
                "⚠️ <b>ᴛʜᴇ sᴇssɪᴏɴ sᴛʀɪɴɢ ᴄᴏᴜʟᴅ ɴᴏᴛ ʙᴇ ᴇxᴛʀᴀᴄᴛᴇᴅ.</b> ᴘʟᴇᴀsᴇ ᴍᴀᴋᴇ sᴜʀᴇ ʏᴏᴜ sᴇɴᴛ ᴀ ɴᴏɴ-ᴇᴍᴘᴛʏ value.",
                parse_mode="HTML",
                reply_markup=get_back_keyboard()
            )
            return
            
        session_str = normalize_session_string(session_str)
        
        # Attempt to validate and authorize the session string
        status_msg = await message.answer("⏳ <b>ᴄᴏɴɴᴇᴄᴛɪɴɢ ᴛᴏ ᴛᴇʟᴇɢʀᴀᴍ sᴇʀᴠᴇʀs ᴜsɪɴɢ ᴘʀᴏᴠɪᴅᴇᴅ sᴇssɪᴏɴ...</b>", parse_mode="HTML")
        proxy, proxy_error = get_random_proxy()
        
        # Instantiate in-memory client
        temp_name = f"uploaded_sess_{message.from_user.id}"
        client = create_pyrogram_client(session_name=temp_name, session_string=session_str, proxy=proxy)
        
        try:
            await client.connect()
            me = await client.get_me()
            if not me:
                raise ValueError("Could not retrieve account identity from get_me()")
            phone = getattr(me, "phone_number", None)
            if not phone:
                # Fallback format: + followed by digits, or some representation
                phone = f"+{me.id}"
            else:
                # Ensure country code format
                if not phone.startswith("+"):
                    phone = f"+{phone}"
                    
            profile_name = "ᴜɴᴋɴᴏᴡɴ"
            first = me.first_name or ""
            last = me.last_name or ""
            name_parts = [first, last]
            profile_name = " ".join([p for p in name_parts if p.strip()]) or me.username or "ᴜɴᴋɴᴏᴡɴ"
            
            # Encrypt and save securely
            encrypted_session = encrypt_data(session_str)
            await client.disconnect()
            
            success = await save_account(
                phone=phone,
                encrypted_session=encrypted_session,
                user_id=message.from_user.id,
                proxy=proxy,
                profile_name=profile_name
            )
            
            await status_msg.delete()
            
            if success:
                proxy_info = f"<code>{html.escape(proxy['hostname'])}:{proxy['port']}</code>" if proxy else "ɴᴏɴᴇ (ᴅɪʀᴇᴄᴛ)"
                await message.answer(
                    f"✅ <b>ᴀᴄᴄᴏᴜɴᴛ ᴀᴅᴅᴇᴅ sᴜᴄᴄᴇssꜰᴜʟʟʏ ᴠɪᴀ ᴜᴘʟᴏᴀᴅ!</b>\n\n"
                    f"👤 <b>ɴᴀᴍᴇ:</b> <code>{html.escape(profile_name)}</code>\n"
                    f"📱 <b>ᴘʜᴏɴᴇ:</b> <code>{html.escape(phone)}</code>\n"
                    f"🔒 <b>sᴇssɪᴏɴ sᴛʀɪɴɢ:</b> ᴇɴᴄʀʏᴘᴛᴇᴅ &amp; sᴀᴠᴇᴅ sᴇᴄᴜʀᴇʟʏ.\n"
                    f"🌐 <b>ʙᴏᴜɴᴅ ᴘʀᴏxʏ:</b> {proxy_info}\n\n"
                    f"ʏᴏᴜ ᴄᴀɴ ɴᴏᴡ ᴍᴀɴᴀɢᴇ ᴛʜɪs sᴇssɪᴏɴ inside the account panel.",
                    parse_mode="HTML",
                    reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                        [InlineKeyboardButton(text="🔙 ʙᴀᴄᴋ ᴛᴏ ᴍᴀɪɴ ᴍᴇɴᴜ", callback_data="menu:main")]
                    ])
                )
                await state.clear()
            else:
                await message.answer(
                    "❌ <b>ᴇʀʀᴏʀ ᴏᴄᴄᴜʀʀᴇᴅ ᴡʜɪʟᴇ sᴀᴠɪɴɢ ᴛᴏ ᴍᴏɴɢᴏᴅʙ. ᴘʟᴇᴀsᴇ ᴄʜᴇᴄᴋ ʟᴏɢs.</b>",
                    parse_mode="HTML",
                    reply_markup=get_back_keyboard()
                )
        except Exception as conn_err:
            logger.exception("Failed to connect via uploaded session string")
            await status_msg.delete()
            await message.answer(
                f"❌ <b>ꜰᴀɪʟᴇᴅ ᴛᴏ ᴀᴜᴛʜᴏʀɪᴢᴇ sᴇssɪᴏɴ:</b> <code>{html.escape(str(conn_err))}</code>\n\n"
                "👉 Please ensure your session is alive and valid.",
                parse_mode="HTML",
                reply_markup=get_back_keyboard()
            )
            try:
                await client.disconnect()
            except:
                pass
    finally:
        if file_path_to_clean and os.path.exists(file_path_to_clean):
            try:
                os.remove(file_path_to_clean)
            except Exception as clean_err:
                logger.error(f"Could not remove temp uploaded file: {clean_err}")

@router.message(AddAccountStates.waiting_for_phone)
async def process_phone(message: Message, state: FSMContext):
    if not message.text:
        await message.answer("⚠️ ᴘʟᴇᴀsᴇ sᴇɴᴅ ᴀ ᴠᴀʟɪᴅ ᴘʜᴏɴᴇ ɴᴜᴍʙᴇʀ.", reply_markup=get_back_keyboard())
        return
    phone = message.text.strip().replace(" ", "")
    if not re.match(r"^\+\d{8,15}$", phone):
        await message.answer(
            "⚠️ <b>ɪɴᴠᴀʟɪᴅ ᴘʜᴏɴᴇ ꜰᴏʀᴍᴀᴛ.</b> ᴘʟᴇᴀsᴇ ᴇɴᴛᴇʀ ᴡɪᴛʜ ᴄᴏᴜɴᴛʀʏ ᴄᴏᴅᴇ (ᴇ.ɢ. <code>+1234567890</code>):",
            parse_mode="HTML",
            reply_markup=get_back_keyboard()
        )
        return
    proxy, proxy_error = get_random_proxy()
    if not proxy:
        warning_msg = "⚠️ ɴᴏ sᴏᴄᴋs5 ᴘʀᴏxɪᴇs ᴄᴏɴꜰɪɢᴜʀᴇᴅ. ᴘʀᴏᴄᴇᴇᴅɪɴɢ ᴡɪᴛʜ ᴅɪʀᴇᴄᴛ ᴄᴏɴɴᴇᴄᴛɪᴏɴ."
        logger.warning(f"No proxy configured: {proxy_error}")
        await message.answer(warning_msg, parse_mode="HTML")
    else:
        success_msg = f"🌐 <b>ᴘʀᴏxʏ sᴇʟᴇᴄᴛᴇᴅ:</b> <code>{html.escape(proxy['hostname'])}:{proxy['port']}</code>. ᴄᴏɴɴᴇᴄᴛɪɴɢ..."
        await message.answer(success_msg, parse_mode="HTML")
        
    status_msg = await message.answer(
        "⏳ <b><b>ᴄᴏɴɴᴇᴄᴛɪɴɢ ᴛᴏ ᴛᴇʟᴇɢʀᴀᴍ sᴇʀᴠᴇʀs &amp; ɢᴇɴᴇʀᴀᴛɪɴɢ ᴏᴛᴘ... ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ.</b></b>",
        parse_mode="HTML",
        reply_markup=get_back_keyboard()
    )
    try:
        session_name = f"sess_{phone.replace('+', '')}"
        client = create_pyrogram_client(session_name=session_name, proxy=proxy)
        await client.connect()
        code_info = await client.send_code(phone)
        phone_code_hash = code_info.phone_code_hash
        await state.update_data(
            phone=phone,
            client=client,
            phone_code_hash=phone_code_hash,
            proxy=proxy
        )
        await message.answer(
            f"📨 <b>ᴛᴇʟᴇɢʀᴀᴍ sᴇɴᴛ ᴀ ʟᴏɢɪɴ ᴏᴛᴘ/ᴄᴏᴅᴇ</b> ᴛᴏ {html.escape(phone)}.\n"
            "ᴘʟᴇᴀsᴇ ᴄʜᴇᴄᴋ ʏᴏᴜʀ ᴏꜰꜰɪᴄɪᴀʟ ᴛᴇʟᴇɢʀᴀᴍ ᴀᴘᴘ ᴏʀ sᴍs ᴀɴᴅ ᴇɴᴛᴇʀ ᴛʜᴇ ᴄᴏᴅᴇ ʜᴇʀᴇ:",
            parse_mode="HTML",
            reply_markup=get_back_keyboard()
        )
        await state.set_state(AddAccountStates.waiting_for_otp)
    except Exception as e:
        logger.exception("Error during send_code")
        await message.answer(
            f"❌ <b>ꜰᴀɪʟᴇᴅ ᴛᴏ ɪɴɪᴛɪᴀᴛᴇ ʟᴏɢɪɴ sᴇssɪᴏɴ:</b> <code>{html.escape(str(e))}</code>",
            parse_mode="HTML",
            reply_markup=get_back_keyboard()
        )
        await state.clear()

@router.message(AddAccountStates.waiting_for_otp)
async def process_otp(message: Message, state: FSMContext):
    if not message.text:
        await message.answer("⚠️ ᴘʟᴇᴀsᴇ sᴇɴᴅ ᴀ ᴠᴀʟɪᴅ ᴏᴛᴘ.", reply_markup=get_back_keyboard())
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
            reply_markup=get_back_keyboard()
        )
        await state.clear()
        return
        
    await message.answer("⏳ <b>ᴠᴇʀɪꜰʏɪɴɢ ᴏᴛᴘ...</b>", parse_mode="HTML")
    try:
        await client.sign_in(phone, phone_code_hash, otp)
        await finalize_account_registration(message, state, client, phone, proxy)
    except SessionPasswordNeeded:
        await message.answer(
            "🔐 <b>ᴛᴡᴏ-ꜰᴀᴄᴛᴏʀ ᴀᴜᴛʜᴇɴᴛɪᴄᴀᴛɪᴏɴ (2ꜰᴀ) ɪs ᴇɴᴀʙʟᴇᴅ</b> ᴏɴ ᴛʜɪs ᴀᴄᴄᴏᴜɴᴛ.\n"
            "ᴘʟᴇᴀsᴇ ᴇɴᴛᴇʀ ʏᴏᴜʀ ᴄʟᴏᴜᴅ ᴘᴀssᴡᴏʀᴅ ʙᴇʟᴏᴡ:",
            parse_mode="HTML",
            reply_markup=get_back_keyboard()
        )
        await state.set_state(AddAccountStates.waiting_for_2fa)
    except PhoneCodeInvalid:
        await message.answer(
            "❌ <b>ɪɴᴠᴀʟɪᴅ ʟᴏɢɪɴ ᴄᴏᴅᴇ.</b> ᴘʟᴇᴀsᴇ ᴇɴᴛᴇʀ ᴛʜᴇ ᴄᴏʀʀᴇᴄᴛ ᴄᴏᴅᴇ:",
            parse_mode="HTML",
            reply_markup=get_back_keyboard()
        )
    except PhoneCodeExpired:
        await message.answer(
            "❌ <b>ʟᴏɢɪɴ ᴄᴏᴅᴇ ʜᴀs ᴇxᴘɪʀᴇᴅ. ᴘʟᴇᴀsᴇ ʀᴇsᴛᴀʀᴛ ᴛʜᴇ ᴘʀᴏᴄᴇss.</b>",
            parse_mode="HTML",
            reply_markup=get_back_keyboard()
        )
        await client.disconnect()
        await state.clear()
    except Exception as e:
        logger.exception("Error during sign_in")
        await message.answer(
            f"❌ <b>ᴀɴ ᴇʀʀᴏʀ ᴏᴄᴄᴜʀʀᴇᴅ:</b> <code>{html.escape(str(e))}</code>",
            parse_mode="HTML",
            reply_markup=get_back_keyboard()
        )
        await client.disconnect()
        await state.clear()

@router.message(AddAccountStates.waiting_for_2fa)
async def process_2fa(message: Message, state: FSMContext):
    if not message.text:
        await message.answer("⚠️ ᴘʟᴇᴀsᴇ sᴇɴᴅ ᴀ ᴠᴀʟɪᴅ 2ꜰᴀ ᴄʟᴏᴜᴅ ᴘᴀssᴡᴏʀᴅ.", reply_markup=get_back_keyboard())
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
            reply_markup=get_back_keyboard()
        )
        await state.clear()
        return
        
    await message.answer("⏳ <b><b>ᴄʜᴇᴄᴋɪɴɢ 2ꜰᴀ ᴄʟᴏᴜᴅ ᴘᴀssᴡᴏʀᴅ...</b></b>", parse_mode="HTML")
    try:
        await client.check_password(password)
        await finalize_account_registration(message, state, client, phone, proxy)
    except (PasswordHashInvalid, Exception) as e:
        logger.warning(f"Invalid 2FA password attempt: {e}")
        await message.answer(
            "❌ <b>ɪɴᴠᴀʟɪᴅ 2ꜰᴀ ᴄʟᴏᴜᴅ ᴘᴀssᴡᴏʀᴅ.</b> ᴘʟᴇᴀsᴇ ᴛʀʏ ᴀɢᴀɪɴ:",
            parse_mode="HTML",
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
                name_parts = [first, last]
                profile_name = " ".join([p for p in name_parts if p.strip()]) or me.username or "ᴜɴᴋɴᴏᴡɴ"
        except Exception as profile_err:
            logger.warning(f"Could not retrieve profile info for {phone}: {profile_err}")
            
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
                f"📱 <b><b>ᴘʜᴏɴᴇ:</b></b> <code>{html.escape(phone)}</code>\n"
                f"🔒 <b>sᴇssɪᴏɴ sᴛʀɪɴɢ:</b> ᴇɴᴄʀʏᴘᴛᴇᴅ &amp; sᴀᴠᴇᴅ sᴇᴄᴜʀᴇʟʏ.\n"
                f"🌐 <b>ʙᴏᴜɴᴅ ᴘʀᴏxʏ:</b> {proxy_info}\n\n"
                f"ʏᴏᴜ ᴄᴀɴ ɴᴏᴡ ʀᴇᴛʀɪᴇᴠᴇ ᴏᴛᴘ ꜰᴏʀ ʟᴏɢɪɴ ᴜsɪɴɢ ᴛʜᴇ ɪɴʟɪɴᴇ ᴘᴀɴᴇʟ.",
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="🔙 ʙᴀᴄᴋ ᴛᴏ ᴍᴀɪɴ ᴍᴇɴᴜ", callback_data="menu:main")]
                ])
            )
        else:
            await message.answer(
                "❌ <b>ᴇʀʀᴏʀ ᴏᴄᴄᴜʀʀᴇᴅ ᴡʜɪʟᴇ sᴀᴠɪɴɢ ᴛᴏ ᴍᴏɴɢᴏᴅʙ. ᴘʟᴇᴀsᴇ ᴄʜᴇᴄᴋ ʟᴏɢs.</b>",
                parse_mode="HTML",
                reply_markup=get_back_keyboard()
            )
    except Exception as e:
        logger.exception("Error during finalize_account_registration")
        await message.answer(
            f"❌ <b>ꜰᴀɪʟᴇᴅ ᴛᴏ ꜰɪɴᴀʟɪᴢᴇ ᴀᴄᴄᴏᴜɴᴛ:</b> <code>{html.escape(str(e))}</code>",
            parse_mode="HTML",
            reply_markup=get_back_keyboard()
        )
        try:
            await client.disconnect()
        except:
            pass
    finally:
        await state.clear()
