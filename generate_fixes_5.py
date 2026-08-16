with open('plugins/list_accounts.py', 'r') as f:
    content = f.read()

# 5. Smart Account Search
search = """def get_accounts_keyboard(accounts: list, page: int = 0) -> InlineKeyboardMarkup:
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
    return InlineKeyboardMarkup(inline_keyboard=keyboard)"""

replace = """class SearchAccountState(StatesGroup):
    waiting_for_query = State()

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

    keyboard.append([InlineKeyboardButton(text="🔍 sᴇᴀʀᴄʜ ᴀᴄᴄᴏᴜɴᴛ", callback_data="search_acc_prompt")])
    keyboard.append([InlineKeyboardButton(text="📦 ʙᴜʟᴋ ᴇxᴘᴏʀᴛ / ɢᴇɴᴇʀᴀᴛᴇ", callback_data=f"bulk_export:menu:{page}")])
    keyboard.append([InlineKeyboardButton(text="🔙 ʙᴀᴄᴋ ᴛᴏ ᴍᴀɪɴ ᴍᴇɴᴜ", callback_data="menu:main")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

@router.callback_query(F.data == "search_acc_prompt")
async def prompt_search_account(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.answer()
    await state.set_state(SearchAccountState.waiting_for_query)
    await callback_query.message.edit_text("🔍 Send search query (phone, name, or starting prefix):\\n\\nSend /cancel to abort.", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="ᴄᴀɴᴄᴇʟ", callback_data="menu:main")]]))

@router.message(SearchAccountState.waiting_for_query)
async def handle_search_account(message: Message, state: FSMContext):
    if message.text == "/cancel":
        await state.clear()
        await message.reply("❌ Cancelled.", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔙 ʙᴀᴄᴋ ᴛᴏ ᴍᴀɪɴ ᴍᴇɴᴜ", callback_data="menu:main")]]))
        return

    query = message.text.lower()
    accounts = await get_all_accounts(user_id=message.from_user.id)
    if not accounts:
        await message.answer("📭 <b>ɴᴏ sᴀᴠᴇᴅ ᴛᴇʟᴇɢʀᴀᴍ ᴀᴄᴄᴏᴜɴᴛs ꜰᴏᴜɴᴅ ɪɴ ᴛʜᴇ ᴅᴀᴛᴀʙᴀsᴇ.</b>", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔙 ʙᴀᴄᴋ ᴛᴏ ᴍᴀɪɴ ᴍᴇɴᴜ", callback_data="menu:main")]]), parse_mode="HTML")
        await state.clear()
        return

    results = []
    for acc in accounts:
        phone = acc.get("phone", "").lower()
        name = (acc.get("profile_name") or "").lower()
        if query in phone or query in name or (len(query) == 1 and (phone.replace("+", "").startswith(query) or name.startswith(query))):
            results.append(acc)

    if not results:
        await message.reply("❌ No accounts matched your search.", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔙 ʙᴀᴄᴋ ᴛᴏ ʟɪsᴛ", callback_data="list_page:0")]]))
        await state.clear()
        return

    keyboard = []
    if len(results) == 1:
        acc = results[0]
        phone = acc.get("phone")
        p_name = acc.get("profile_name") or "ᴜɴᴋɴᴏᴡɴ"
        keyboard.append([InlineKeyboardButton(text=f"📱 {phone} | ⚙️ {p_name}", callback_data=f"view_acc:{phone}:0")])
    else:
        row = []
        for acc in results:
            phone = acc.get("phone")
            p_name = acc.get("profile_name") or "ᴜɴᴋɴᴏᴡɴ"
            btn_text = f"📱 {phone[-4:]} | {p_name[:8]}" # Shorten to fit 2 per row
            row.append(InlineKeyboardButton(text=btn_text, callback_data=f"view_acc:{phone}:0"))
            if len(row) == 2:
                keyboard.append(row)
                row = []
        if row:
            keyboard.append(row)

    keyboard.append([InlineKeyboardButton(text="🔙 ʙᴀᴄᴋ ᴛᴏ ʟɪsᴛ", callback_data="list_page:0")])
    await message.reply(f"🔍 <b>Search Results for:</b> {html.escape(query)}\\n━━━━━━━━━━━━━━━━━━━━━\\nMatches: {len(results)}", reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard), parse_mode="HTML")
    await state.clear()"""

content = content.replace(search, replace)
with open('plugins/list_accounts.py', 'w') as f:
    f.write(content)
