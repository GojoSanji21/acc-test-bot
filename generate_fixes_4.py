with open('plugins/chat_manager.py', 'r') as f:
    content = f.read()

# 4. Enhance Inbox Browser & Stats Search
stats_search = """@router.callback_query(F.data.startswith("chat_mgr:chat_stats:"))
async def process_chat_stats(callback_query: CallbackQuery):
    await callback_query.answer("Calculating stats...")
    parts = callback_query.data.split(":")
    phone = parts[2]

    acc = await get_account(phone, user_id=callback_query.from_user.id)
    if not acc:
        return

    session_str = decrypt_data(acc["encrypted_session"])
    client = create_pyrogram_client(session_name=f"mgmt_{uuid.uuid4().hex[:8]}", session_string=session_str)

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

        await callback_query.answer(f"📊 Chat Stats:\\nPublic Channels: {pub_chan_count}\\nPrivate Channels: {priv_chan_count}\\nGroups: {group_count}", show_alert=True)
    except Exception as e:
        await callback_query.answer(f"❌ Error fetching stats: {e}", show_alert=True)
    finally:
        if client.is_connected:
            await client.disconnect()"""

stats_replace = """class SearchChatState(StatesGroup):
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
        await client.connect()
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
            row.append(InlineKeyboardButton(text=f"🗨️ {title}", callback_data=f"chat_ctrl:{dialog.chat.id}:{phone}:{page}"))
            if len(row) == 2:
                keyboard.append(row)
                row = []
        if row:
            keyboard.append(row)

        nav_row = []
        if page > 0:
            nav_row.append(InlineKeyboardButton(text="◀️ ᴘʀᴇᴠɪᴏᴜs", callback_data=f"chat_mgr:chat_stats:{phone}:{page-1}"))
        if end_idx < len(dialogs):
            nav_row.append(InlineKeyboardButton(text="ɴᴇxᴛ ▶️", callback_data=f"chat_mgr:chat_stats:{phone}:{page+1}"))
        if nav_row:
            keyboard.append(nav_row)

        keyboard.append([InlineKeyboardButton(text="🔍 sᴇᴀʀᴄʜ", callback_data=f"chat_mgr:search_stats:{phone}:{page}")])
        keyboard.append([InlineKeyboardButton(text="ʙᴀᴄᴋ", callback_data=f"view_acc:{phone}:{page}")])

        await callback_query.message.edit_text(f"📊 <b>Inbox Browser & Stats</b>\\n━━━━━━━━━━━━━━━━━━━━━\\nTotal Chats: {len(dialogs)}", reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard), parse_mode="HTML")
    except Exception as e:
        await callback_query.answer(f"❌ Error fetching inbox: {e}", show_alert=True)
    finally:
        if client.is_connected:
            await client.disconnect()

@router.callback_query(F.data.startswith("chat_mgr:search_stats:"))
async def process_search_stats(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.answer()
    parts = callback_query.data.split(":")
    phone = parts[2]
    page = parts[3]

    await state.set_state(SearchChatState.waiting_for_query)
    await state.update_data(phone=phone, page=page)

    await callback_query.message.edit_text("🔍 Send search query (name, username, ID):\\n\\nSend /cancel to abort.", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="ᴄᴀɴᴄᴇʟ", callback_data=f"chat_mgr:chat_stats:{phone}:{page}")]]))

@router.message(SearchChatState.waiting_for_query)
async def handle_search_chat_query(message: Message, state: FSMContext):
    if message.text == "/cancel":
        await state.clear()
        await message.reply("❌ Cancelled.")
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

    processing_msg = await message.reply("🔍 Searching...")
    try:
        await client.connect()
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
            row.append(InlineKeyboardButton(text=f"🗨️ {title}", callback_data=f"chat_ctrl:{dialog.chat.id}:{phone}:{page}"))
            if len(row) == 2:
                keyboard.append(row)
                row = []
        if row:
            keyboard.append(row)

        keyboard.append([InlineKeyboardButton(text="ʙᴀᴄᴋ", callback_data=f"chat_mgr:chat_stats:{phone}:{page}")])

        await processing_msg.edit_text(f"🔍 <b>Search Results for:</b> {html.escape(query)}\n━━━━━━━━━━━━━━━━━━━━━\nMatches: {len(dialogs)} (showing top 20)", reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard), parse_mode="HTML")
        await state.clear()
    except Exception as e:
        await processing_msg.edit_text(f"❌ Error searching: {e}", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="ʙᴀᴄᴋ", callback_data=f"chat_mgr:chat_stats:{phone}:{page}")]]))
        await state.clear()
    finally:
        if client.is_connected:
            await client.disconnect()"""

content = content.replace(stats_search, stats_replace)

with open('plugins/chat_manager.py', 'w') as f:
    f.write(content)
