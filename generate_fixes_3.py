with open('plugins/chat_manager.py', 'r') as f:
    content = f.read()

content += """
class ChatSendState(StatesGroup):
    waiting_for_message = State()

@router.callback_query(F.data.startswith("chat_act:send_msg:"))
async def process_chat_send_message(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.answer()
    parts = callback_query.data.split(":")
    chat_id = parts[2]
    phone = parts[3]
    page = parts[4]

    await state.set_state(ChatSendState.waiting_for_message)
    await state.update_data(chat_id=chat_id, phone=phone, page=page)

    await callback_query.message.edit_text("✉️ Send the text, photo, document, or forward a message you want to send to this chat:\\n\\nSend /cancel to abort.", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="ᴄᴀɴᴄᴇʟ", callback_data=f"chat_ctrl:{chat_id}:{phone}:{page}")]]))

@router.message(ChatSendState.waiting_for_message)
async def handle_chat_send_message(message: Message, state: FSMContext):
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

    session_str = decrypt_data(acc["encrypted_session"])
    client = create_pyrogram_client(session_name=f"mgmt_{uuid.uuid4().hex[:8]}", session_string=session_str)

    processing_msg = await message.reply("🔄 Sending message...")

    try:
        await client.connect()
        # Very basic forwarding or sending (text only for now)
        if message.text:
            await client.send_message(int(chat_id), message.text)
        elif message.photo:
            file_id = message.photo[-1].file_id
            file_info = await message.bot.get_file(file_id)
            downloaded_file = await message.bot.download_file(file_info.file_path)
            temp_path = f"temp_send_{message.from_user.id}.jpg"
            with open(temp_path, 'wb') as f:
                f.write(downloaded_file.read())
            await client.send_photo(int(chat_id), photo=temp_path, has_spoiler=True)
            import os
            if os.path.exists(temp_path):
                os.remove(temp_path)
        elif message.document:
             file_id = message.document.file_id
             file_info = await message.bot.get_file(file_id)
             downloaded_file = await message.bot.download_file(file_info.file_path)
             temp_path = f"temp_send_{message.from_user.id}_{message.document.file_name}"
             with open(temp_path, 'wb') as f:
                 f.write(downloaded_file.read())
             await client.send_document(int(chat_id), document=temp_path)
             import os
             if os.path.exists(temp_path):
                 os.remove(temp_path)
        else:
             await processing_msg.edit_text("❌ Unsupported message type.", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="ʙᴀᴄᴋ", callback_data=f"chat_ctrl:{chat_id}:{phone}:{page}")]]))
             await state.clear()
             return

        await processing_msg.edit_text("✅ Message sent successfully.", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="ʙᴀᴄᴋ", callback_data=f"chat_ctrl:{chat_id}:{phone}:{page}")]]))
        await state.clear()
    except Exception as e:
        logger.error(f"Error sending message to {chat_id}: {e}")
        await processing_msg.edit_text(f"❌ Error: {e}", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="ʙᴀᴄᴋ", callback_data=f"chat_ctrl:{chat_id}:{phone}:{page}")]]))
        await state.clear()
    finally:
        if client.is_connected:
            await client.disconnect()

@router.callback_query(F.data.startswith("chat_act:delete:"))
async def process_chat_delete(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.answer()
    parts = callback_query.data.split(":")
    chat_id = parts[2]
    phone = parts[3]
    page = parts[4]

    keyboard = [
        [
            InlineKeyboardButton(text="ʏᴇs, ᴅᴇʟᴇᴛᴇ/ʟᴇᴀᴠᴇ", callback_data=f"chat_act:confirm_del:{chat_id}:{phone}:{page}")
        ],
        [InlineKeyboardButton(text="ᴄᴀɴᴄᴇʟ", callback_data=f"chat_ctrl:{chat_id}:{phone}:{page}")]
    ]
    await callback_query.message.edit_text("⚠️ Are you sure you want to delete/leave this chat?", reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard))

@router.callback_query(F.data.startswith("chat_act:confirm_del:"))
async def process_chat_confirm_delete(callback_query: CallbackQuery):
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
        await client.connect()
        chat = await client.get_chat(int(chat_id))
        if chat.type.name == "CHANNEL" or chat.type.name == "SUPERGROUP":
            try:
                await client.delete_channel(int(chat_id))
            except Exception:
                await client.leave_chat(int(chat_id))
        else:
            await client.leave_chat(int(chat_id))

        await callback_query.message.edit_text("✅ Chat deleted/left successfully.", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="ʙᴀᴄᴋ ᴛᴏ ᴀᴄᴄᴏᴜɴᴛ", callback_data=f"view_acc:{phone}:{page}")]]))
    except Exception as e:
        logger.error(f"Error deleting chat {chat_id}: {e}")
        await callback_query.message.edit_text(f"❌ Error: {e}", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="ʙᴀᴄᴋ", callback_data=f"chat_ctrl:{chat_id}:{phone}:{page}")]]))
    finally:
        if client.is_connected:
            await client.disconnect()
"""

with open('plugins/chat_manager.py', 'w') as f:
    f.write(content)
