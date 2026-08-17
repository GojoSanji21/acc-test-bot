import os
import uuid
import time
import logging
import html
import emoji
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery

logger = logging.getLogger("TGStorageBot.plugins.chat_manager")


def to_small_caps(text: str) -> str:
    normal = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    small_caps = "ᴀʙᴄᴅᴇғɢʜɪᴊᴋʟᴍɴᴏᴘǫʀsᴛᴜᴠᴡxʏᴢᴀʙᴄᴅᴇғɢʜɪᴊᴋʟᴍɴᴏᴘǫʀsᴛᴜᴠᴡxʏᴢ"
    trans = str.maketrans(normal, small_caps)
    return text.translate(trans)

router = Router()

class ChatManagerState(StatesGroup):
    change_name = State()
    change_photo = State()
    make_public = State()
    promote_admin = State()
    send_message = State()

class CreateChannelState(StatesGroup):
    enter_name = State()
    enter_photo = State()
    choose_privacy = State()
    enter_username = State()


import math
from database import get_account
from helpers import decrypt_data, create_pyrogram_client
from pyrogram.errors import PeerIdInvalid, RPCError, FloodWait, ChatAdminRequired, UsernameOccupied, UsernameInvalid, FreshResetAuthorisationForbidden
from pyrogram.enums import ChatType, ChatMemberStatus

@router.callback_query(F.data.startswith("chat_mgr:devices:"))
async def process_active_devices(callback_query: CallbackQuery):
    await callback_query.answer()
    parts = callback_query.data.split(":")
    phone = parts[2]
    page = int(parts[3]) if len(parts) > 3 else 0

    acc = await get_account(phone, user_id=callback_query.from_user.id)
    if not acc:
        await callback_query.message.edit_text("❌ <b>sᴇʟᴇᴄᴛᴇᴅ ᴀᴄᴄᴏᴜɴᴛ ɴᴏ ʟᴏɴɢᴇʀ ᴇxɪsᴛs.</b>", parse_mode="HTML")
        return

    session_str = decrypt_data(acc["encrypted_session"])
    client = create_pyrogram_client(session_name=f"mgmt_{uuid.uuid4().hex[:8]}", session_string=session_str)

    try:
        await client.start()
        from pyrogram.raw import functions as raw_functions
        from pyrogram.raw import types as raw_types
        authorizations = await client.invoke(raw_functions.account.GetAuthorizations())

        text = "📱 <b>ᴀᴄᴛɪᴠᴇ ᴅᴇᴠɪᴄᴇs</b>\n━━━━━━━━━━━━━━━━━━━━━\n"
        keyboard = []

        import datetime
        for auth in authorizations.authorizations:
            ip_str = getattr(auth, 'ip', 'Unknown')
            date_created = getattr(auth, 'date_created', 0)
            date_str = datetime.datetime.fromtimestamp(date_created).strftime('%Y-%m-%d') if date_created else 'Unknown'

            if getattr(auth, 'current', False):
                text += f"🟢 <b>{html.escape(getattr(auth, 'app_name', 'Unknown'))} - {html.escape(getattr(auth, 'device_model', 'Unknown'))} ({html.escape(getattr(auth, 'platform', 'Unknown'))})</b>\n  IP: {ip_str} | Date: {date_str}\n"
            else:
                text += f"🔴 <b>{html.escape(getattr(auth, 'app_name', 'Unknown'))} - {html.escape(getattr(auth, 'device_model', 'Unknown'))} ({html.escape(getattr(auth, 'platform', 'Unknown'))})</b>\n  IP: {ip_str} | Date: {date_str}\n"
                keyboard.append([InlineKeyboardButton(text=f"ᴛᴇʀᴍɪɴᴀᴛᴇ {getattr(auth, 'device_model', 'Unknown'):15}", callback_data=f"term_dev:{auth.hash}:{phone}:{page}")])

        if len(authorizations.authorizations) > 1:
            keyboard.append([InlineKeyboardButton(text="ᴛᴇʀᴍɪɴᴀᴛᴇ ᴀʟʟ ᴏᴛʜᴇʀs", callback_data=f"term_all_dev:{phone}:{page}")])

        keyboard.append([InlineKeyboardButton(text="ʙᴀᴄᴋ", callback_data=f"view_acc:{phone}:{page}")])

        await callback_query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard), parse_mode="HTML")
    except Exception as e:
        logger.error(f"Error fetching devices for {phone}: {e}")
        await callback_query.message.edit_text(f"Error: {e}", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="ʙᴀᴄᴋ", callback_data=f"view_acc:{phone}:{page}")]]))
    finally:
        await client.stop()

@router.callback_query(F.data.startswith("term_dev:"))
async def process_terminate_device(callback_query: CallbackQuery):
    await callback_query.answer()
    parts = callback_query.data.split(":")
    auth_hash = int(parts[1])
    phone = parts[2]
    page = int(parts[3])

    acc = await get_account(phone, user_id=callback_query.from_user.id)
    if not acc:
        return

    session_str = decrypt_data(acc["encrypted_session"])
    client = create_pyrogram_client(session_name=f"mgmt_{uuid.uuid4().hex[:8]}", session_string=session_str)

    try:
        await client.start()
        from pyrogram.raw import functions as raw_functions
        await client.invoke(raw_functions.account.ResetAuthorization(hash=auth_hash))
        await callback_query.answer("ᴅᴇᴠɪᴄᴇ ᴛᴇʀᴍɪɴᴀᴛᴇᴅ.", show_alert=True)
        # Re-trigger devices menu
        callback_query.data = f"chat_mgr:devices:{phone}:{page}"
        await process_active_devices(callback_query)
    except FreshResetAuthorisationForbidden:
        await callback_query.answer("Session is too fresh to terminate devices.", show_alert=True)
    except Exception as e:
        logger.error(f"Error terminating device: {e}")
        await callback_query.answer(f"Error: {e}", show_alert=True)
    finally:
        await client.stop()

@router.callback_query(F.data.startswith("term_all_dev:"))
async def process_terminate_all_devices(callback_query: CallbackQuery):
    await callback_query.answer()
    parts = callback_query.data.split(":")
    phone = parts[1]
    page = int(parts[2])

    acc = await get_account(phone, user_id=callback_query.from_user.id)
    if not acc:
        return

    session_str = decrypt_data(acc["encrypted_session"])
    client = create_pyrogram_client(session_name=f"mgmt_{uuid.uuid4().hex[:8]}", session_string=session_str)

    try:
        await client.start()
        from pyrogram.raw import functions as raw_functions
        authorizations = await client.invoke(raw_functions.account.GetAuthorizations())
        count = 0
        for auth in authorizations.authorizations:
            if not getattr(auth, 'current', False):
                try:
                    await client.invoke(raw_functions.account.ResetAuthorization(hash=auth.hash))
                    count += 1
                except Exception as e:
                    logger.error(f"Failed to reset auth: {e}")

        await callback_query.answer(f"{count} ᴅᴇᴠɪᴄᴇs ᴛᴇʀᴍɪɴᴀᴛᴇᴅ.", show_alert=True)
        # Re-trigger devices menu
        callback_query.data = f"chat_mgr:devices:{phone}:{page}"
        await process_active_devices(callback_query)
    except FreshResetAuthorisationForbidden:
        await callback_query.answer("Session is too fresh to terminate devices.", show_alert=True)
    except Exception as e:
        await callback_query.answer(f"Error: {e}", show_alert=True)
    finally:
        await client.stop()


@router.callback_query(F.data.startswith("chat_mgr:pub_chan:") | F.data.startswith("chat_mgr:priv_chan:") | F.data.startswith("chat_mgr:groups:"))
async def process_dialog_fetching(callback_query: CallbackQuery):
    await callback_query.answer("Fetching chats, please wait...")
    parts = callback_query.data.split(":")
    action = parts[1]
    phone = parts[2]
    page = int(parts[3]) if len(parts) > 3 else 0

    acc = await get_account(phone, user_id=callback_query.from_user.id)
    if not acc:
        return

    session_str = decrypt_data(acc["encrypted_session"])
    client = create_pyrogram_client(session_name=f"mgmt_{uuid.uuid4().hex[:8]}", session_string=session_str)

    try:
        await client.start()
        dialogs = []
        async for dialog in client.get_dialogs():
            dialogs.append(dialog)

        filtered_chats = []
        if action == "pub_chan":
            title = "ᴘᴜʙʟɪᴄ ᴄʜᴀɴɴᴇʟs"
            filtered_chats = [d.chat for d in dialogs if d.chat.type == ChatType.CHANNEL and d.chat.username]
        elif action == "priv_chan":
            title = "ᴘʀɪᴠᴀᴛᴇ ᴄʜᴀɴɴᴇʟs"
            filtered_chats = [d.chat for d in dialogs if d.chat.type == ChatType.CHANNEL and not d.chat.username]
        elif action == "groups":
            title = "ɢʀᴏᴜᴘs"
            filtered_chats = [d.chat for d in dialogs if d.chat.type in [ChatType.SUPERGROUP, ChatType.GROUP]]

        if not filtered_chats:
            await callback_query.message.edit_text(f"📝 <b>{title}</b>\n━━━━━━━━━━━━━━━━━━━━━\n\nNo chats found in this category.", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="ʙᴀᴄᴋ", callback_data=f"view_acc:{phone}:{page}")]]), parse_mode="HTML")
            return

        # Pagination
        items_per_page = 10
        total_pages = math.ceil(len(filtered_chats) / items_per_page)
        current_chat_page = 0 # Default starting page for chats

        # We can encode the chat_page in the callback if needed, but for simplicity we'll just show the first page and add navigation if we want
        # Let's add a state parameter to track current chat page if needed, or pass it in callback

        start_idx = 0
        end_idx = min(items_per_page, len(filtered_chats))
        current_chats = filtered_chats[start_idx:end_idx]

        keyboard = []
        for chat in current_chats:
            chat_title = chat.title or "Unknown"
            display_title = to_small_caps(emoji.replace_emoji(chat_title, replace="").replace("[", "").replace("]", "").strip())

            if chat.username:
                url = f"https://t.me/{chat.username}"
                keyboard.append([InlineKeyboardButton(text=f"{display_title:30}", url=url)])
            else:
                invite_link = chat.invite_link
                if not invite_link:
                    try:
                        invite_link = await client.export_chat_invite_link(chat.id)
                    except Exception:
                        invite_link = None

                if invite_link:
                    keyboard.append([InlineKeyboardButton(text=f"{display_title:30}", url=invite_link)])
                else:
                    keyboard.append([InlineKeyboardButton(text=f"{display_title:30}", callback_data=f"chat_ctrl:{chat.id}:{phone}:{page}")])

        if len(filtered_chats) > items_per_page:
            # Add simple navigation logic later if needed
            pass

        keyboard.append([InlineKeyboardButton(text="ʙᴀᴄᴋ", callback_data=f"view_acc:{phone}:{page}")])

        await callback_query.message.edit_text(f"📝 <b>{title}</b>\n━━━━━━━━━━━━━━━━━━━━━\n\nSelect a chat to manage:", reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard), parse_mode="HTML")

    except Exception as e:
        logger.error(f"Error fetching dialogs for {phone}: {e}")
        await callback_query.message.edit_text(f"❌ Error: {e}", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="ʙᴀᴄᴋ", callback_data=f"view_acc:{phone}:{page}")]]))
    finally:
        await client.stop()

class SearchChatState(StatesGroup):
    waiting_for_query = State()

@router.callback_query(F.data.startswith("chat_mgr:chat_stats:"))
async def process_chat_stats(callback_query: CallbackQuery):
    await callback_query.answer("Loading Inbox...")
    parts = callback_query.data.split(":")
    phone = parts[2]
    page = int(parts[3]) if len(parts) > 3 else 0

    acc = await get_account(phone, user_id=callback_query.from_user.id)
    if not acc:
        return

    session_str = decrypt_data(acc["encrypted_session"])
    client = create_pyrogram_client(session_name=f"mgmt_{uuid.uuid4().hex[:8]}", session_string=session_str)

    try:
        await client.start()
        dialogs = []
        async for dialog in client.get_dialogs():
            dialogs.append(dialog)

        # 10 rows x 2 columns = 20 per page
        per_page = 20
        start_idx = page * per_page
        end_idx = start_idx + per_page
        page_dialogs = dialogs[start_idx:end_idx]

        keyboard = []
        row = []
        for dialog in page_dialogs:
            title = dialog.chat.title or dialog.chat.first_name or "Unknown"
            if len(title) > 15: title = title[:15] + "..."
            row.append(InlineKeyboardButton(text=f"{title}", callback_data=f"chat_ctrl:{dialog.chat.id}:{phone}:{page}"))
            if len(row) == 2:
                keyboard.append(row)
                row = []
        if row:
            keyboard.append(row)

        nav_row = []
        if page > 0:
            nav_row.append(InlineKeyboardButton(text="ᴘʀᴇᴠɪᴏᴜs", callback_data=f"chat_mgr:chat_stats:{phone}:{page-1}"))
        if end_idx < len(dialogs):
            nav_row.append(InlineKeyboardButton(text="ɴᴇxᴛ", callback_data=f"chat_mgr:chat_stats:{phone}:{page+1}"))
        if nav_row:
            keyboard.append(nav_row)

        keyboard.append([InlineKeyboardButton(text="sᴇᴀʀᴄʜ", callback_data=f"chat_mgr:search_stats:{phone}:{page}")])
        keyboard.append([InlineKeyboardButton(text="ʙᴀᴄᴋ", callback_data=f"view_acc:{phone}:{page}")])

        await callback_query.message.edit_text(f"📊 <b>Inbox Browser & Stats</b>\n━━━━━━━━━━━━━━━━━━━━━\nTotal Chats: {len(dialogs)}", reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard), parse_mode="HTML")
    except Exception as e:
        await callback_query.answer(f"Error fetching inbox: {e}", show_alert=True)
    finally:
        await client.stop()

@router.callback_query(F.data.startswith("chat_mgr:search_stats:"))
async def process_search_stats(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.answer()
    parts = callback_query.data.split(":")
    phone = parts[2]
    page = parts[3]

    await state.set_state(SearchChatState.waiting_for_query)
    await state.update_data(phone=phone, page=page)

    await callback_query.message.edit_text("Send search query (name, username, ID):\n\nSend /cancel to abort.", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="ᴄᴀɴᴄᴇʟ", callback_data=f"chat_mgr:chat_stats:{phone}:{page}")]]))

@router.message(SearchChatState.waiting_for_query)
async def handle_search_chat_query(message: Message, state: FSMContext):
    if message.text == "/cancel":
        await state.clear()
        await message.reply("Cancelled.")
        return

    query = message.text.lower()
    data = await state.get_data()
    phone = data.get("phone")
    page = data.get("page", 0)

    acc = await get_account(phone, user_id=message.from_user.id)
    if not acc:
        await state.clear()
        return

    session_str = decrypt_data(acc["encrypted_session"])
    client = create_pyrogram_client(session_name=f"mgmt_{uuid.uuid4().hex[:8]}", session_string=session_str)

    processing_msg = await message.reply("Searching...")
    try:
        await client.start()
        dialogs = []
        async for dialog in client.get_dialogs():
            title = (dialog.chat.title or "").lower()
            fname = (dialog.chat.first_name or "").lower()
            lname = (dialog.chat.last_name or "").lower()
            uname = (dialog.chat.username or "").lower()
            cid = str(dialog.chat.id)
            if query in title or query in fname or query in lname or query in uname or query in cid:
                dialogs.append(dialog)

        keyboard = []
        row = []
        for dialog in dialogs[:20]: # Show up to 20 search results
            title = dialog.chat.title or dialog.chat.first_name or "Unknown"
            if len(title) > 15: title = title[:15] + "..."
            row.append(InlineKeyboardButton(text=f"{title}", callback_data=f"chat_ctrl:{dialog.chat.id}:{phone}:{page}"))
            if len(row) == 2:
                keyboard.append(row)
                row = []
        if row:
            keyboard.append(row)

        keyboard.append([InlineKeyboardButton(text="ʙᴀᴄᴋ", callback_data=f"chat_mgr:chat_stats:{phone}:{page}")])

        await processing_msg.edit_text(f"🔍 <b>Search Results for:</b> {html.escape(query)}\n━━━━━━━━━━━━━━━━━━━━━\nMatches: {len(dialogs)} (showing top 20)", reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard), parse_mode="HTML")
        await state.clear()
    except Exception as e:
        await processing_msg.edit_text(f"Error searching: {e}", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="ʙᴀᴄᴋ", callback_data=f"chat_mgr:chat_stats:{phone}:{page}")]]))
        await state.clear()
    finally:
        await client.stop()

@router.callback_query(F.data.startswith("chat_ctrl:"))
async def process_chat_control_panel(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.answer()
    parts = callback_query.data.split(":")
    chat_id = parts[1]
    phone = parts[2]
    page = int(parts[3]) if len(parts) > 3 else 0

    acc = await get_account(phone, user_id=callback_query.from_user.id)
    if not acc:
        return

    session_str = decrypt_data(acc["encrypted_session"])
    client = create_pyrogram_client(session_name=f"mgmt_{uuid.uuid4().hex[:8]}", session_string=session_str)

    try:
        await client.start()
        is_admin = False
        try:
            chat = await client.get_chat(int(chat_id))
            if chat.type in [ChatType.CHANNEL, ChatType.GROUP, ChatType.SUPERGROUP]:
                member = await client.get_chat_member(int(chat_id), "me")
                is_admin = member.status in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR]
        except PeerIdInvalid:
            async for _ in client.get_dialogs(limit=50):
                pass
            try:
                chat = await client.get_chat(int(chat_id))
                if chat.type in [ChatType.CHANNEL, ChatType.GROUP, ChatType.SUPERGROUP]:
                    member = await client.get_chat_member(int(chat_id), "me")
                    is_admin = member.status in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR]
            except PeerIdInvalid:
                await callback_query.answer("❌ Error: Peer ID Invalid. The bot might not have access to this chat.", show_alert=True)
                return

        text = f"⚙️ <b>Chat Control Panel</b>\n━━━━━━━━━━━━━━━━━━━━━\n"
        text += f"🏷️ <b>Name:</b> {html.escape(chat.title or chat.first_name or 'Unknown')}\n"
        text += f"🆔 <b>ID:</b> <code>{chat.id}</code>\n"
        text += f"📢 <b>Type:</b> {chat.type.name if chat.type else 'Unknown'}\n"
        if chat.username:
            text += f"🔗 <b>Username:</b> @{chat.username}\n"

        keyboard = []

        if chat.type in [ChatType.PRIVATE, ChatType.BOT]:
            keyboard = [
                [InlineKeyboardButton(text="sᴇɴᴅ ᴍᴇssᴀɢᴇ", callback_data=f"chat_act:send_msg:{chat.id}:{phone}:{page}")],
                [InlineKeyboardButton(text="ʙʟᴏᴄᴋ", callback_data=f"chat_act:block:{chat.id}:{phone}:{page}")],
            ]
            if chat.username:
                keyboard.append([InlineKeyboardButton(text="ᴠɪᴇᴡ ᴄʜᴀᴛ", url=f"https://t.me/{chat.username}")])
            keyboard.append([InlineKeyboardButton(text="ʙᴀᴄᴋ", callback_data=f"view_acc:{phone}:{page}")])
        elif chat.type in [ChatType.CHANNEL, ChatType.GROUP, ChatType.SUPERGROUP]:

            if not is_admin:
                text += "\n⚠️ <i>You're not admin/owner of this chat.</i>"
                keyboard = [
                    [InlineKeyboardButton(text="sᴇɴᴅ ᴍᴇssᴀɢᴇ", callback_data=f"chat_act:send_msg:{chat.id}:{phone}:{page}")],
                    [InlineKeyboardButton(text="ʙᴀᴄᴋ", callback_data=f"view_acc:{phone}:{page}")]
                ]
            else:
                keyboard = [
                    [
                        InlineKeyboardButton(text="ᴄʜᴀɴɢᴇ ɴᴀᴍᴇ", callback_data=f"chat_act:rename:{chat.id}:{phone}:{page}"),
                        InlineKeyboardButton(text="ᴄʜᴀɴɢᴇ ᴜsᴇʀɴᴀᴍᴇ", callback_data=f"chat_act:privacy:{chat.id}:{phone}:{page}")
                    ],
                    [
                        InlineKeyboardButton(text="sᴇɴᴅ ᴍᴇssᴀɢᴇ", callback_data=f"chat_act:send_msg:{chat.id}:{phone}:{page}"),
                        InlineKeyboardButton(text="ᴘʀᴏᴍᴏᴛᴇ ᴀᴅᴍɪɴ", callback_data=f"chat_act:admin:{chat.id}:{phone}:{page}")
                    ],
                    [
                        InlineKeyboardButton(text="ᴘᴜʙʟɪᴄ ʟɪɴᴋ" if chat.username else "ᴘʀɪᴠᴀᴛᴇ ʟɪɴᴋ", url=f"https://t.me/{chat.username}" if chat.username else (chat.invite_link or f"https://t.me/c/{str(chat.id).replace('-100', '')}/1")),
                        InlineKeyboardButton(text="ᴅᴇʟᴇᴛᴇ ᴄʜᴀɴɴᴇʟ" if chat.type.name == "CHANNEL" else "ʟᴇᴀᴠᴇ ᴄʜᴀᴛ", callback_data=f"chat_act:delete:{chat.id}:{phone}:{page}")
                    ],
                    [InlineKeyboardButton(text="ʙᴀᴄᴋ", callback_data=f"view_acc:{phone}:{page}")]
                ]

        await callback_query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard), parse_mode="HTML")

    except Exception as e:
        logger.error(f"Error fetching chat control panel for {chat_id}: {e}")
        await callback_query.message.edit_text(f"❌ Error: {e}", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="ʙᴀᴄᴋ", callback_data=f"view_acc:{phone}:{page}")]]))
    finally:
        await client.stop()


@router.callback_query(F.data.startswith("chat_act:rename:"))
async def process_chat_rename(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.answer()
    parts = callback_query.data.split(":")
    chat_id = parts[2]
    phone = parts[3]
    page = parts[4]

    await state.set_state(ChatManagerState.change_name)
    await state.update_data(chat_id=chat_id, phone=phone, page=page)

    await callback_query.message.edit_text("📝 Send the new title for the chat:\n\nSend /cancel to abort.", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="ᴄᴀɴᴄᴇʟ", callback_data=f"chat_ctrl:{chat_id}:{phone}:{page}")]]))

@router.message(ChatManagerState.change_name)
async def handle_chat_rename(message: Message, state: FSMContext):
    if message.text == "/cancel":
        await state.clear()
        await message.reply("❌ Cancelled.")
        return

    data = await state.get_data()
    chat_id = data.get("chat_id")
    phone = data.get("phone")
    page = data.get("page")

    acc = await get_account(phone, user_id=message.from_user.id)
    if not acc:
        await state.clear()
        return

    new_title = message.text
    session_str = decrypt_data(acc["encrypted_session"])
    client = create_pyrogram_client(session_name=f"mgmt_{uuid.uuid4().hex[:8]}", session_string=session_str)

    processing_msg = await message.reply("🔄 Processing...")

    try:
        await client.start()
        await client.set_chat_title(int(chat_id), new_title)
        await processing_msg.edit_text(f"✅ Chat title successfully changed to: <b>{html.escape(new_title)}</b>", parse_mode="HTML")
    except ChatAdminRequired:
        await processing_msg.edit_text("❌ You don't have admin rights to change the title.")
    except Exception as e:
        await processing_msg.edit_text(f"❌ Error: {e}")
    finally:
        await client.stop()
        await state.clear()

@router.callback_query(F.data.startswith("chat_act:photo:"))
async def process_chat_photo(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.answer()
    parts = callback_query.data.split(":")
    chat_id = parts[2]
    phone = parts[3]
    page = parts[4]

    await state.set_state(ChatManagerState.change_photo)
    await state.update_data(chat_id=chat_id, phone=phone, page=page)

    await callback_query.message.edit_text("📸 Send a new photo for the chat:\n\nSend /cancel to abort.", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="ᴄᴀɴᴄᴇʟ", callback_data=f"chat_ctrl:{chat_id}:{phone}:{page}")]]))

@router.message(ChatManagerState.change_photo, F.photo)
async def handle_chat_photo(message: Message, state: FSMContext):
    data = await state.get_data()
    chat_id = data.get("chat_id")
    phone = data.get("phone")
    page = data.get("page")

    acc = await get_account(phone, user_id=message.from_user.id)
    if not acc:
        await state.clear()
        return

    session_str = decrypt_data(acc["encrypted_session"])
    client = create_pyrogram_client(session_name=f"mgmt_{uuid.uuid4().hex[:8]}", session_string=session_str)

    processing_msg = await message.reply("🔄 Downloading photo and processing...")
    temp_path = f"temp_photo_{chat_id}.jpg"

    try:
        file_id = message.photo[-1].file_id
        file_info = await message.bot.get_file(file_id)
        downloaded_file = await message.bot.download_file(file_info.file_path)

        # Save temporarily
        with open(temp_path, 'wb') as f:
            f.write(downloaded_file.read())

        await client.start()
        await client.set_chat_photo(int(chat_id), photo=temp_path)
        await processing_msg.edit_text("✅ Chat photo successfully updated.")
    except ChatAdminRequired:
        await processing_msg.edit_text("❌ You don't have admin rights to change the photo.")
    except Exception as e:
        await processing_msg.edit_text(f"❌ Error: {e}")
    finally:
        await client.stop()
        if os.path.exists(temp_path):
            os.remove(temp_path)
        await state.clear()

@router.message(ChatManagerState.change_photo)
async def handle_chat_photo_invalid(message: Message, state: FSMContext):
    if message.text == "/cancel":
        await state.clear()
        await message.reply("❌ Cancelled.")
        return
    await message.reply("❌ Please send a valid photo or /cancel.")


@router.callback_query(F.data.startswith("chat_act:privacy:"))
async def process_chat_privacy(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.answer()
    parts = callback_query.data.split(":")
    chat_id = parts[2]
    phone = parts[3]
    page = parts[4]

    acc = await get_account(phone, user_id=callback_query.from_user.id)
    if not acc:
        return

    session_str = decrypt_data(acc["encrypted_session"])
    client = create_pyrogram_client(session_name=f"mgmt_{uuid.uuid4().hex[:8]}", session_string=session_str)

    try:
        await client.start()
        chat = await client.get_chat(int(chat_id))

        if chat.username:
            # It's public, let's make it private
            await client.set_chat_username(int(chat_id), None)
            await callback_query.message.edit_text("✅ Chat is now private.", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="ʙᴀᴄᴋ", callback_data=f"chat_ctrl:{chat_id}:{phone}:{page}")]]))
        else:
            # It's private, let's make it public by prompting for username
            await state.set_state(ChatManagerState.make_public)
            await state.update_data(chat_id=chat_id, phone=phone, page=page)
            await callback_query.message.edit_text("🔗 Send the new username (without @) to make the chat public:\n\nSend /cancel to abort.", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="ᴄᴀɴᴄᴇʟ", callback_data=f"chat_ctrl:{chat_id}:{phone}:{page}")]]))
    except ChatAdminRequired:
        await callback_query.message.edit_text("❌ You don't have admin rights to change privacy.", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="ʙᴀᴄᴋ", callback_data=f"chat_ctrl:{chat_id}:{phone}:{page}")]]))
    except Exception as e:
        logger.error(f"Error checking chat privacy for {chat_id}: {e}")
        await callback_query.message.edit_text(f"❌ Error: {e}", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="ʙᴀᴄᴋ", callback_data=f"chat_ctrl:{chat_id}:{phone}:{page}")]]))
    finally:
        await client.stop()

@router.callback_query(F.data.startswith("retry_make_public:"))
async def process_retry_make_public(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.answer()

    parts = callback_query.data.split(":")
    phone = parts[1]
    page = int(parts[2]) if len(parts) > 2 else 0
    chat_id = parts[3]

    await state.set_state(ChatManagerState.make_public)
    await state.update_data(chat_id=chat_id, phone=phone, page=page)

    await callback_query.message.edit_text(
        "🔗 Send the new username (without @) to make the chat public:\n\nSend /cancel to abort.",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="ᴄᴀɴᴄᴇʟ", callback_data=f"chat_ctrl:{chat_id}:{phone}:{page}")]])
    )

@router.message(ChatManagerState.make_public)
async def handle_chat_make_public(message: Message, state: FSMContext):
    if message.text == "/cancel":
        await state.clear()
        await message.reply("❌ Cancelled.")
        return

    data = await state.get_data()
    chat_id = data.get("chat_id")
    phone = data.get("phone")
    page = data.get("page")

    acc = await get_account(phone, user_id=message.from_user.id)
    if not acc:
        await state.clear()
        return

    username = message.text.replace("@", "").strip()
    session_str = decrypt_data(acc["encrypted_session"])
    client = create_pyrogram_client(session_name=f"mgmt_{uuid.uuid4().hex[:8]}", session_string=session_str)

    processing_msg = await message.reply("🔄 Processing...")

    try:
        await client.start()
        await client.set_chat_username(int(chat_id), username)
        await processing_msg.edit_text(f"✅ Chat is now public with username: <b>@{html.escape(username)}</b>", parse_mode="HTML")
        await state.clear()
    except (UsernameOccupied, UsernameInvalid) as e:
        error_msg = "Username is already taken." if isinstance(e, UsernameOccupied) else "Username is invalid."
        await processing_msg.edit_text(
            f"❌ {error_msg} Click below to retry.",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="ʀᴇᴛʀʏ ᴜsᴇʀɴᴀᴍᴇ", callback_data=f"retry_make_public:{phone}:{page}:{chat_id}")],
                [InlineKeyboardButton(text="ᴄᴀɴᴄᴇʟ", callback_data=f"chat_ctrl:{chat_id}:{phone}:{page}")]
            ])
        )
    except ChatAdminRequired:
        await processing_msg.edit_text("❌ You don't have admin rights to set username.")
        await state.clear()
    except Exception as e:
        await processing_msg.edit_text(f"❌ Error: {e}")
        await state.clear()
    finally:
        await client.stop()

@router.callback_query(F.data.startswith("chat_act:admin:"))
async def process_chat_promote_admin(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.answer()
    parts = callback_query.data.split(":")
    chat_id = parts[2]
    phone = parts[3]
    page = parts[4]

    await state.set_state(ChatManagerState.promote_admin)
    await state.update_data(chat_id=chat_id, phone=phone, page=page)

    await callback_query.message.edit_text("👑 Send the user ID or @username to promote to admin:\n\nSend /cancel to abort.", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="ᴄᴀɴᴄᴇʟ", callback_data=f"chat_ctrl:{chat_id}:{phone}:{page}")]]))

from pyrogram.types import ChatPrivileges

@router.message(ChatManagerState.promote_admin)
async def handle_chat_promote_admin(message: Message, state: FSMContext):
    if message.text == "/cancel":
        await state.clear()
        await message.reply("❌ Cancelled.")
        return

    data = await state.get_data()
    chat_id = data.get("chat_id")
    phone = data.get("phone")
    page = data.get("page")

    acc = await get_account(phone, user_id=message.from_user.id)
    if not acc:
        await state.clear()
        return

    user_target = message.text.strip()
    # Try converting to int if possible
    try:
        user_target = int(user_target)
    except ValueError:
        pass

    session_str = decrypt_data(acc["encrypted_session"])
    client = create_pyrogram_client(session_name=f"mgmt_{uuid.uuid4().hex[:8]}", session_string=session_str)

    processing_msg = await message.reply("🔄 Promoting user...")

    try:
        await client.start()

        # Grant basic admin privileges
        privileges = ChatPrivileges(
            can_manage_chat=True,
            can_delete_messages=True,
            can_manage_video_chats=True,
            can_restrict_members=True,
            can_promote_members=False,
            can_change_info=True,
            can_post_messages=True,
            can_edit_messages=True,
            can_invite_users=True,
            can_pin_messages=True
        )

        await client.promote_chat_member(int(chat_id), user_target, privileges)
        await processing_msg.edit_text(f"✅ User successfully promoted to admin.")
    except ChatAdminRequired:
        await processing_msg.edit_text("❌ You don't have admin rights to promote members.")
    except Exception as e:
        await processing_msg.edit_text(f"❌ Error: {e}")
    finally:
        await client.stop()
        await state.clear()

@router.callback_query(F.data.startswith("chat_mgr:create_chan:"))
async def process_create_channel(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.answer()
    parts = callback_query.data.split(":")
    phone = parts[2]
    page = int(parts[3]) if len(parts) > 3 else 0

    await state.set_state(CreateChannelState.enter_name)
    await state.update_data(phone=phone, page=page)

    await callback_query.message.edit_text(
        "📝 Send the name for the new channel:\n\nSend /cancel to abort.",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="ᴄᴀɴᴄᴇʟ", callback_data=f"view_acc:{phone}:{page}")]])
    )

@router.message(CreateChannelState.enter_name)
async def handle_create_channel_name(message: Message, state: FSMContext):
    if message.text == "/cancel":
        await state.clear()
        await message.reply("❌ Cancelled.")
        return

    await state.update_data(channel_name=message.text)
    await state.set_state(CreateChannelState.enter_photo)

    data = await state.get_data()
    phone = data.get("phone")
    page = data.get("page")

    await message.reply(
        "📸 Send a profile photo for the new channel, or send /skip to continue without a photo:\n\nSend /cancel to abort.",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="ᴄᴀɴᴄᴇʟ", callback_data=f"view_acc:{phone}:{page}")]])
    )

@router.message(CreateChannelState.enter_photo, F.photo)
async def handle_create_channel_photo(message: Message, state: FSMContext):
    data = await state.get_data()
    phone = data.get("phone")
    page = data.get("page")

    file_id = message.photo[-1].file_id
    file_info = await message.bot.get_file(file_id)
    downloaded_file = await message.bot.download_file(file_info.file_path)

    temp_path = f"temp_channel_photo_{message.from_user.id}_{int(time.time())}.jpg"
    with open(temp_path, 'wb') as f:
        f.write(downloaded_file.read())

    await state.update_data(channel_photo=temp_path)
    await state.set_state(CreateChannelState.choose_privacy)

    keyboard = [
        [
            InlineKeyboardButton(text="ᴘᴜʙʟɪᴄ", callback_data="chan_privacy:public"),
            InlineKeyboardButton(text="ᴘʀɪᴠᴀᴛᴇ", callback_data="chan_privacy:private")
        ],
        [InlineKeyboardButton(text="ᴄᴀɴᴄᴇʟ", callback_data=f"view_acc:{phone}:{page}")]
    ]
    await message.reply("🔒 Choose privacy for the new channel:", reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard))

@router.message(CreateChannelState.enter_photo)
async def handle_create_channel_photo_skip(message: Message, state: FSMContext):
    data = await state.get_data()
    phone = data.get("phone")
    page = data.get("page")

    if message.text == "/cancel":
        await state.clear()
        await message.reply("❌ Cancelled.")
        return
    elif message.text == "/skip":
        await state.update_data(channel_photo=None)
        await state.set_state(CreateChannelState.choose_privacy)

        keyboard = [
            [
                InlineKeyboardButton(text="ᴘᴜʙʟɪᴄ", callback_data="chan_privacy:public"),
                InlineKeyboardButton(text="ᴘʀɪᴠᴀᴛᴇ", callback_data="chan_privacy:private")
            ],
            [InlineKeyboardButton(text="ᴄᴀɴᴄᴇʟ", callback_data=f"view_acc:{phone}:{page}")]
        ]
        await message.reply("🔒 Choose privacy for the new channel:", reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard))
    else:
        await message.reply("❌ Please send a valid photo, /skip, or /cancel.")

@router.callback_query(CreateChannelState.choose_privacy, F.data.startswith("chan_privacy:"))
async def process_create_channel_privacy(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.answer()
    choice = callback_query.data.split(":")[1]

    data = await state.get_data()
    phone = data.get("phone")
    page = data.get("page")
    channel_name = data.get("channel_name")
    channel_photo = data.get("channel_photo")

    if choice == "private":
        acc = await get_account(phone, user_id=callback_query.from_user.id)
        if not acc:
            await state.clear()
            return

        session_str = decrypt_data(acc["encrypted_session"])
        client = create_pyrogram_client(session_name=f"mgmt_{uuid.uuid4().hex[:8]}", session_string=session_str)

        processing_msg = await callback_query.message.edit_text("🔄 Creating private channel...")

        try:
            await client.start()
            new_chat = await client.create_channel(title=channel_name, description="")

            if channel_photo:
                try:
                    await client.set_chat_photo(new_chat.id, photo=channel_photo)
                except Exception as e:
                    logger.error(f"Error setting chat photo during creation: {e}")

            invite_link_str = ""
            try:
                inv_link = await client.export_chat_invite_link(new_chat.id)
                invite_link_str = f"\n🔗 Link: {inv_link}"
            except Exception:
                pass
            await processing_msg.edit_text(f"✅ Private channel <b>{html.escape(channel_name)}</b> created successfully!{invite_link_str}\n🆔 ID: <code>{new_chat.id}</code>", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="ʙᴀᴄᴋ", callback_data=f"view_acc:{phone}:{page}")]]), parse_mode="HTML")
        except Exception as e:
            await processing_msg.edit_text(f"❌ Error creating channel: {e}", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="ʙᴀᴄᴋ", callback_data=f"view_acc:{phone}:{page}")]]))
        finally:
            if channel_photo and os.path.exists(channel_photo):
                try:
                    os.remove(channel_photo)
                except:
                    pass
            await client.stop()
            await state.clear()
    else:
        await state.set_state(CreateChannelState.enter_username)
        await callback_query.message.edit_text(
            "🔗 Send the username (without @) for the public channel:\n\nSend /cancel to abort.",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="ᴄᴀɴᴄᴇʟ", callback_data=f"view_acc:{phone}:{page}")]])
        )

@router.callback_query(F.data.startswith("retry_chan_username:"))
async def process_retry_channel_username(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.answer()

    parts = callback_query.data.split(":")
    phone = parts[1]
    page = int(parts[2]) if len(parts) > 2 else 0
    chat_id = parts[3]

    await state.set_state(CreateChannelState.enter_username)
    await state.update_data(phone=phone, page=page, created_chat_id=chat_id)

    await callback_query.message.edit_text(
        "🔗 Send the username (without @) for the public channel:\n\nSend /cancel to abort.",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="ᴄᴀɴᴄᴇʟ", callback_data=f"view_acc:{phone}:{page}")]])
    )


@router.message(CreateChannelState.enter_username)
async def handle_create_channel_username(message: Message, state: FSMContext):
    if message.text == "/cancel":
        await state.clear()
        await message.reply("❌ Cancelled.")
        return

    username = message.text.replace("@", "").strip()

    data = await state.get_data()
    phone = data.get("phone")
    page = data.get("page")
    channel_name = data.get("channel_name")
    channel_photo = data.get("channel_photo")
    created_chat_id = data.get("created_chat_id")

    acc = await get_account(phone, user_id=message.from_user.id)
    if not acc:
        await state.clear()
        return

    session_str = decrypt_data(acc["encrypted_session"])
    client = create_pyrogram_client(session_name=f"mgmt_{uuid.uuid4().hex[:8]}", session_string=session_str)

    processing_msg = await message.reply("🔄 Setting up public channel...")

    try:
        await client.start()

        if not created_chat_id:
            new_chat = await client.create_channel(title=channel_name, description="")
            created_chat_id = new_chat.id
            await state.update_data(created_chat_id=created_chat_id)

        try:
            await client.set_chat_username(int(created_chat_id), username)
        except (UsernameOccupied, UsernameInvalid) as e:
            error_msg = "Username is already taken." if isinstance(e, UsernameOccupied) else "Username is invalid."
            await processing_msg.edit_text(
                f"⚠️ Channel created but {error_msg} Click below to retry.",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="ʀᴇᴛʀʏ ᴜsᴇʀɴᴀᴍᴇ", callback_data=f"retry_chan_username:{phone}:{page}:{created_chat_id}")],
                    [InlineKeyboardButton(text="ᴄᴀɴᴄᴇʟ", callback_data=f"view_acc:{phone}:{page}")]
                ])
            )
            return

        if channel_photo:
            try:
                await client.set_chat_photo(int(created_chat_id), photo=channel_photo)
            except Exception as e:
                logger.error(f"Error setting chat photo during creation: {e}")

        await processing_msg.edit_text(f"✅ Public channel <b>{html.escape(channel_name)}</b> created successfully!\n🔗 Link: https://t.me/{username}\n🆔 ID: <code>{created_chat_id}</code>", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="ʙᴀᴄᴋ", callback_data=f"view_acc:{phone}:{page}")]]), parse_mode="HTML")
        await state.clear()
    except Exception as e:
        await processing_msg.edit_text(f"❌ Error: {e}", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="ʙᴀᴄᴋ", callback_data=f"view_acc:{phone}:{page}")]]))
        await state.clear()
    finally:
        if channel_photo and os.path.exists(channel_photo):
            try:
                os.remove(channel_photo)
            except:
                pass
        await client.stop()
@router.callback_query(F.data.startswith("chat_act:block:"))
async def process_chat_block(callback_query: CallbackQuery):
    await callback_query.answer()
    parts = callback_query.data.split(":")
    chat_id = parts[2]
    phone = parts[3]
    page = parts[4]

    acc = await get_account(phone, user_id=callback_query.from_user.id)
    if not acc:
        return

    session_str = decrypt_data(acc["encrypted_session"])
    client = create_pyrogram_client(session_name=f"mgmt_{uuid.uuid4().hex[:8]}", session_string=session_str)

    try:
        await client.start()
        await client.block_user(int(chat_id))
        await callback_query.message.edit_text("✅ User/Bot blocked successfully.", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="ʙᴀᴄᴋ", callback_data=f"view_acc:{phone}:{page}")]]))
    except Exception as e:
        logger.error(f"Error blocking user {chat_id}: {e}")
        await callback_query.message.edit_text(f"❌ Error: {e}", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="ʙᴀᴄᴋ", callback_data=f"chat_ctrl:{chat_id}:{phone}:{page}")]]))
    finally:
        await client.stop()

@router.callback_query(F.data.startswith("chat_act:send_msg:"))
async def process_chat_send_message(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.answer()
    parts = callback_query.data.split(":")
    chat_id = parts[2]
    phone = parts[3]
    page = parts[4]

    await state.set_state(ChatManagerState.send_message)
    await state.update_data(chat_id=chat_id, phone=phone, page=page)

    await callback_query.message.edit_text("💬 Send the message you want to forward or send to this chat (Text, Photo, or Forwarded Message):\n\nSend /cancel to abort.", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="ᴄᴀɴᴄᴇʟ", callback_data=f"chat_ctrl:{chat_id}:{phone}:{page}")]]))

@router.message(ChatManagerState.send_message)
async def handle_chat_send_message(message: Message, state: FSMContext):
    if message.text == "/cancel":
        data = await state.get_data()
        chat_id = data.get("chat_id")
        phone = data.get("phone")
        page = data.get("page")
        await state.clear()

        await message.reply("❌ Cancelled.")
        return

    data = await state.get_data()
    chat_id = data.get("chat_id")
    phone = data.get("phone")
    page = data.get("page")

    acc = await get_account(phone, user_id=message.from_user.id)
    if not acc:
        await state.clear()
        return

    session_str = decrypt_data(acc["encrypted_session"])
    client = create_pyrogram_client(session_name=f"mgmt_{uuid.uuid4().hex[:8]}", session_string=session_str)

    processing_msg = await message.reply("🔄 Sending message...")

    temp_path = None
    try:
        await client.start()

        if message.photo:
            file_id = message.photo[-1].file_id
            file_info = await message.bot.get_file(file_id)
            downloaded_file = await message.bot.download_file(file_info.file_path)

            temp_path = f"temp_send_photo_{uuid.uuid4().hex}.jpg"
            with open(temp_path, 'wb') as f:
                f.write(downloaded_file.read())

            await client.send_photo(chat_id=int(chat_id), photo=temp_path, caption=message.caption or "")

        elif message.text:
            await client.send_message(chat_id=int(chat_id), text=message.text)
        elif message.video:
            file_id = message.video.file_id
            file_info = await message.bot.get_file(file_id)
            downloaded_file = await message.bot.download_file(file_info.file_path)

            temp_path = f"temp_send_video_{uuid.uuid4().hex}.mp4"
            with open(temp_path, 'wb') as f:
                f.write(downloaded_file.read())

            await client.send_video(chat_id=int(chat_id), video=temp_path, caption=message.caption or "")

        else:
            await processing_msg.edit_text("❌ Unsupported message type.")
            return

        await processing_msg.edit_text(f"✅ Message sent successfully.")
    except ChatAdminRequired:
        await processing_msg.edit_text("❌ You don't have permission to send messages here.")
    except Exception as e:
        await processing_msg.edit_text(f"❌ Error: {e}")
    finally:
        if temp_path and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except Exception:
                pass
        await client.stop()
        await state.clear()
