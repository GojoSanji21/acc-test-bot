import logging
import html
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery

logger = logging.getLogger("TGStorageBot.plugins.chat_manager")

router = Router()

class ChatManagerState(StatesGroup):
    change_name = State()
    change_photo = State()
    make_public = State()
    promote_admin = State()


import math
from database import get_account
from helpers import decrypt_data, create_pyrogram_client
from pyrogram.errors import RPCError, FloodWait, ChatAdminRequired, UsernameOccupied, UsernameInvalid, FreshResetAuthorisationForbidden
from pyrogram.enums import ChatType

@router.callback_query(F.data.startswith("acc_opt:devices:"))
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
    client = create_pyrogram_client(session_string=session_str)

    try:
        await client.connect()
        authorizations = await client.get_authorizations()

        text = "📱 <b>ᴀᴄᴛɪᴠᴇ ᴅᴇᴠɪᴄᴇs</b>\n━━━━━━━━━━━━━━━━━━━━━\n"
        keyboard = []

        for auth in authorizations:
            if auth.is_current:
                text += f"🟢 <b>{html.escape(auth.device_model)}</b> (Current)\n"
            else:
                text += f"🔴 <b>{html.escape(auth.device_model)}</b> (App: {html.escape(auth.app_version)})\n"
                keyboard.append([InlineKeyboardButton(text=f"❌ ᴛᴇʀᴍɪɴᴀᴛᴇ {auth.device_model[:15]}", callback_data=f"term_dev:{auth.hash}:{phone}:{page}")])

        if len(authorizations) > 1:
            keyboard.append([InlineKeyboardButton(text="💣 ᴛᴇʀᴍɪɴᴀᴛᴇ ᴀʟʟ ᴏᴛʜᴇʀs", callback_data=f"term_all_dev:{phone}:{page}")])

        keyboard.append([InlineKeyboardButton(text="🔙 ʙᴀᴄᴋ", callback_data=f"view_acc:{phone}:{page}")])

        await callback_query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard), parse_mode="HTML")
    except Exception as e:
        logger.error(f"Error fetching devices for {phone}: {e}")
        await callback_query.message.edit_text(f"❌ Error: {e}", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔙 ʙᴀᴄᴋ", callback_data=f"view_acc:{phone}:{page}")]]))
    finally:
        if client.is_connected:
            await client.disconnect()

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
    client = create_pyrogram_client(session_string=session_str)

    try:
        await client.connect()
        await client.reset_authorization(auth_hash)
        await callback_query.answer("✅ ᴅᴇᴠɪᴄᴇ ᴛᴇʀᴍɪɴᴀᴛᴇᴅ.", show_alert=True)
        # Re-trigger devices menu
        # Fake callback query data to reload
        callback_query.data = f"acc_opt:devices:{phone}:{page}"
        await process_active_devices(callback_query)
    except FreshResetAuthorisationForbidden:
        await callback_query.answer("⚠️ Session is too fresh. Please wait a few hours before terminating other sessions.", show_alert=True)
    except Exception as e:
        await callback_query.answer(f"❌ Error: {e}", show_alert=True)
    finally:
        if client.is_connected:
            await client.disconnect()

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
    client = create_pyrogram_client(session_string=session_str)

    try:
        await client.connect()
        authorizations = await client.get_authorizations()
        count = 0
        for auth in authorizations:
            if not auth.is_current:
                await client.reset_authorization(auth.hash)
                count += 1

        await callback_query.answer(f"✅ {count} ᴅᴇᴠɪᴄᴇs ᴛᴇʀᴍɪɴᴀᴛᴇᴅ.", show_alert=True)
        # Re-trigger devices menu
        callback_query.data = f"acc_opt:devices:{phone}:{page}"
        await process_active_devices(callback_query)
    except FreshResetAuthorisationForbidden:
        await callback_query.answer("⚠️ Session is too fresh. Please wait a few hours before terminating other sessions.", show_alert=True)
    except Exception as e:
        await callback_query.answer(f"❌ Error: {e}", show_alert=True)
    finally:
        if client.is_connected:
            await client.disconnect()


@router.callback_query(F.data.startswith("acc_opt:pub_chan:") | F.data.startswith("acc_opt:priv_chan:") | F.data.startswith("acc_opt:groups:"))
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
    client = create_pyrogram_client(session_string=session_str)

    try:
        await client.connect()
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
            await callback_query.message.edit_text(f"📝 <b>{title}</b>\n━━━━━━━━━━━━━━━━━━━━━\n\nNo chats found in this category.", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔙 ʙᴀᴄᴋ", callback_data=f"view_acc:{phone}:{page}")]]), parse_mode="HTML")
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
            keyboard.append([InlineKeyboardButton(text=f"💬 {chat_title[:30]}", callback_data=f"chat_ctrl:{chat.id}:{phone}:{page}")])

        if len(filtered_chats) > items_per_page:
            # Add simple navigation logic later if needed
            pass

        keyboard.append([InlineKeyboardButton(text="🔙 ʙᴀᴄᴋ", callback_data=f"view_acc:{phone}:{page}")])

        await callback_query.message.edit_text(f"📝 <b>{title}</b>\n━━━━━━━━━━━━━━━━━━━━━\n\nSelect a chat to manage:", reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard), parse_mode="HTML")

    except Exception as e:
        logger.error(f"Error fetching dialogs for {phone}: {e}")
        await callback_query.message.edit_text(f"❌ Error: {e}", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔙 ʙᴀᴄᴋ", callback_data=f"view_acc:{phone}:{page}")]]))
    finally:
        if client.is_connected:
            await client.disconnect()

@router.callback_query(F.data.startswith("acc_opt:chat_stats:"))
async def process_chat_stats(callback_query: CallbackQuery):
    await callback_query.answer("Calculating stats...")
    parts = callback_query.data.split(":")
    phone = parts[2]

    acc = await get_account(phone, user_id=callback_query.from_user.id)
    if not acc:
        return

    session_str = decrypt_data(acc["encrypted_session"])
    client = create_pyrogram_client(session_string=session_str)

    try:
        await client.connect()
        pub_chan_count = 0
        priv_chan_count = 0
        group_count = 0

        async for dialog in client.get_dialogs():
            if dialog.chat.type == ChatType.CHANNEL:
                if dialog.chat.username:
                    pub_chan_count += 1
                else:
                    priv_chan_count += 1
            elif dialog.chat.type in [ChatType.SUPERGROUP, ChatType.GROUP]:
                group_count += 1

        await callback_query.answer(f"📊 Chat Stats:\nPublic Channels: {pub_chan_count}\nPrivate Channels: {priv_chan_count}\nGroups: {group_count}", show_alert=True)
    except Exception as e:
        await callback_query.answer(f"❌ Error fetching stats: {e}", show_alert=True)
    finally:
        if client.is_connected:
            await client.disconnect()

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
    client = create_pyrogram_client(session_string=session_str)

    try:
        await client.connect()
        chat = await client.get_chat(int(chat_id))

        text = f"⚙️ <b>Chat Control Panel</b>\n━━━━━━━━━━━━━━━━━━━━━\n"
        text += f"🏷️ <b>Name:</b> {html.escape(chat.title or 'Unknown')}\n"
        text += f"🆔 <b>ID:</b> <code>{chat.id}</code>\n"
        text += f"📢 <b>Type:</b> {chat.type.name if chat.type else 'Unknown'}\n"
        if chat.username:
            text += f"🔗 <b>Username:</b> @{chat.username}\n"

        keyboard = [
            [
                InlineKeyboardButton(text="ᴄʜᴀɴɢᴇ ɴᴀᴍᴇ", callback_data=f"chat_act:rename:{chat.id}:{phone}:{page}"),
                InlineKeyboardButton(text="ᴄʜᴀɴɢᴇ ᴘʜᴏᴛᴏ", callback_data=f"chat_act:photo:{chat.id}:{phone}:{page}")
            ],
            [
                InlineKeyboardButton(text="ᴍᴀᴋᴇ ᴘᴜʙʟɪᴄ" if not chat.username else "ᴍᴀᴋᴇ ᴘʀɪᴠᴀᴛᴇ", callback_data=f"chat_act:privacy:{chat.id}:{phone}:{page}"),
                InlineKeyboardButton(text="ᴘʀᴏᴍᴏᴛᴇ ᴀᴅᴍɪɴ", callback_data=f"chat_act:admin:{chat.id}:{phone}:{page}")
            ],
            [InlineKeyboardButton(text="🔙 ʙᴀᴄᴋ", callback_data=f"view_acc:{phone}:{page}")]
        ]

        await callback_query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard), parse_mode="HTML")

    except Exception as e:
        logger.error(f"Error fetching chat control panel for {chat_id}: {e}")
        await callback_query.message.edit_text(f"❌ Error: {e}", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔙 ʙᴀᴄᴋ", callback_data=f"view_acc:{phone}:{page}")]]))
    finally:
        if client.is_connected:
            await client.disconnect()


@router.callback_query(F.data.startswith("chat_act:rename:"))
async def process_chat_rename(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.answer()
    parts = callback_query.data.split(":")
    chat_id = parts[2]
    phone = parts[3]
    page = parts[4]

    await state.set_state(ChatManagerState.change_name)
    await state.update_data(chat_id=chat_id, phone=phone, page=page)

    await callback_query.message.edit_text("📝 Send the new title for the chat:\n\nSend /cancel to abort.", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="❌ ᴄᴀɴᴄᴇʟ", callback_data=f"chat_ctrl:{chat_id}:{phone}:{page}")]]))

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
    client = create_pyrogram_client(session_string=session_str)

    processing_msg = await message.reply("🔄 Processing...")

    try:
        await client.connect()
        await client.set_chat_title(int(chat_id), new_title)
        await processing_msg.edit_text(f"✅ Chat title successfully changed to: <b>{html.escape(new_title)}</b>", parse_mode="HTML")
    except ChatAdminRequired:
        await processing_msg.edit_text("❌ You don't have admin rights to change the title.")
    except Exception as e:
        await processing_msg.edit_text(f"❌ Error: {e}")
    finally:
        if client.is_connected:
            await client.disconnect()
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

    await callback_query.message.edit_text("📸 Send a new photo for the chat:\n\nSend /cancel to abort.", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="❌ ᴄᴀɴᴄᴇʟ", callback_data=f"chat_ctrl:{chat_id}:{phone}:{page}")]]))

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
    client = create_pyrogram_client(session_string=session_str)

    processing_msg = await message.reply("🔄 Downloading photo and processing...")
    temp_path = f"temp_photo_{chat_id}.jpg"

    try:
        file_id = message.photo[-1].file_id
        file_info = await message.bot.get_file(file_id)
        downloaded_file = await message.bot.download_file(file_info.file_path)

        # Save temporarily
        with open(temp_path, 'wb') as f:
            f.write(downloaded_file.read())

        await client.connect()
        await client.set_chat_photo(int(chat_id), photo=temp_path)
        await processing_msg.edit_text("✅ Chat photo successfully updated.")
    except ChatAdminRequired:
        await processing_msg.edit_text("❌ You don't have admin rights to change the photo.")
    except Exception as e:
        await processing_msg.edit_text(f"❌ Error: {e}")
    finally:
        if client.is_connected:
            await client.disconnect()
        import os
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
    client = create_pyrogram_client(session_string=session_str)

    try:
        await client.connect()
        chat = await client.get_chat(int(chat_id))

        if chat.username:
            # It's public, let's make it private
            await client.set_chat_username(int(chat_id), None)
            await callback_query.message.edit_text("✅ Chat is now private.", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔙 ʙᴀᴄᴋ", callback_data=f"chat_ctrl:{chat_id}:{phone}:{page}")]]))
        else:
            # It's private, let's make it public by prompting for username
            await state.set_state(ChatManagerState.make_public)
            await state.update_data(chat_id=chat_id, phone=phone, page=page)
            await callback_query.message.edit_text("🔗 Send the new username (without @) to make the chat public:\n\nSend /cancel to abort.", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="❌ ᴄᴀɴᴄᴇʟ", callback_data=f"chat_ctrl:{chat_id}:{phone}:{page}")]]))
    except ChatAdminRequired:
        await callback_query.message.edit_text("❌ You don't have admin rights to change privacy.", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔙 ʙᴀᴄᴋ", callback_data=f"chat_ctrl:{chat_id}:{phone}:{page}")]]))
    except Exception as e:
        logger.error(f"Error checking chat privacy for {chat_id}: {e}")
        await callback_query.message.edit_text(f"❌ Error: {e}", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔙 ʙᴀᴄᴋ", callback_data=f"chat_ctrl:{chat_id}:{phone}:{page}")]]))
    finally:
        if client.is_connected:
            await client.disconnect()

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
    client = create_pyrogram_client(session_string=session_str)

    processing_msg = await message.reply("🔄 Processing...")

    try:
        await client.connect()
        await client.set_chat_username(int(chat_id), username)
        await processing_msg.edit_text(f"✅ Chat is now public with username: <b>@{html.escape(username)}</b>", parse_mode="HTML")
        await state.clear()
    except UsernameOccupied:
        await processing_msg.edit_text("❌ Username is already taken. Please send a different username or /cancel.")
    except UsernameInvalid:
        await processing_msg.edit_text("❌ Username is invalid. Please send a different username or /cancel.")
    except ChatAdminRequired:
        await processing_msg.edit_text("❌ You don't have admin rights to set username.")
        await state.clear()
    except Exception as e:
        await processing_msg.edit_text(f"❌ Error: {e}")
        await state.clear()
    finally:
        if client.is_connected:
            await client.disconnect()

@router.callback_query(F.data.startswith("chat_act:admin:"))
async def process_chat_promote_admin(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.answer()
    parts = callback_query.data.split(":")
    chat_id = parts[2]
    phone = parts[3]
    page = parts[4]

    await state.set_state(ChatManagerState.promote_admin)
    await state.update_data(chat_id=chat_id, phone=phone, page=page)

    await callback_query.message.edit_text("👑 Send the user ID or @username to promote to admin:\n\nSend /cancel to abort.", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="❌ ᴄᴀɴᴄᴇʟ", callback_data=f"chat_ctrl:{chat_id}:{phone}:{page}")]]))

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
    client = create_pyrogram_client(session_string=session_str)

    processing_msg = await message.reply("🔄 Promoting user...")

    try:
        await client.connect()

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
        if client.is_connected:
            await client.disconnect()
        await state.clear()
