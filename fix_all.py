import re
from pathlib import Path

with open("plugins/list_accounts.py", "r", encoding="utf-8") as f:
    content = f.read()

# 1. Replace extract block
extract_search = """    # Handle Extract option
    if action == "extract":
        session_str = decrypt_data(acc["encrypted_session"])
        p_name = acc.get("profile_name") or "ᴜɴᴋɴᴏᴡɴ"

        telethon_str = pyrogram_to_telethon(session_str)
        if not telethon_str:
            telethon_str = "Error converting to Telethon format."

        extract_text = (
            "━━━━━━━━━━━━━━━━━━━━━\\n"
            "🔑 <b>sᴇssɪᴏɴ ᴇxᴛʀᴀᴄᴛɪᴏɴ</b>\\n"
            "━━━━━━━━━━━━━━━━━━━━━\\n"
            f"📱 <b>ᴘʜᴏɴᴇ:</b> <code>{html.escape(phone)}</code>\\n"
            f"👤 <b>ᴀᴄᴄᴏᴜɴᴛ:</b> <code>{html.escape(p_name)}</code>\\n\\n"
            "👇 <b><b>Pyrogram sᴇssɪᴏɴ sᴛʀɪɴɢ (V2):</b></b>\\n"
            f"<code>{html.escape(session_str)}</code>\\n\\n"
            "👇 <b><b>Telethon sᴇssɪᴏɴ sᴛʀɪɴɢ:</b></b>\\n"
            f"<code>{html.escape(telethon_str)}</code>"
        )
        await callback_query.message.edit_text(
            extract_text,
            reply_markup=get_back_to_panel_keyboard(phone, page),
            parse_mode="HTML"
        )
        return"""

extract_replace = """    # Handle Extract option
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
        return"""

content = content.replace(extract_search, extract_replace)

# 2. Replace export block
export_search = """    # Handle Export SQLite option
    if action == "export":
        await callback_query.message.edit_text(
            f"⏳ <b>ɢᴇɴᴇʀᴀᴛɪɴɢ sǫʟɪᴛᴇ <code>.sᴇssɪᴏɴ</code> ꜰɪʟᴇ ꜰᴏʀ</b> <code>{html.escape(phone)}</code>... <b>ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ.</b>",
            parse_mode="HTML"
        )

        session_str = decrypt_data(acc["encrypted_session"])
        temp_dir = Path("temp_sessions")
        temp_dir.mkdir(exist_ok=True)

        name_clean = phone.replace("+", "")
        file_path = None
        try:
            file_path = await save_session_string_to_file(session_str, name_clean, temp_dir)
            if file_path and file_path.exists():
                await bot.send_document(
                    chat_id=callback_query.message.chat.id,
                    document=FSInputFile(str(file_path)),
                    caption=f"✅ <b>sǫʟɪᴛᴇ sᴇssɪᴏɴ ᴇxᴘᴏʀᴛᴇᴅ sᴜᴄᴄᴇssꜰᴜʟʟʏ!</b>\\n\\n📱 <b>ᴘʜᴏɴᴇ:</b> <code>{html.escape(phone)}</code>",
                    parse_mode="HTML"
                )
                await callback_query.message.edit_text(
                    f"✅ <b>sǫʟɪᴛᴇ sᴇssɪᴏɴ ꜰɪʟᴇ sᴇɴᴛ sᴜᴄᴄᴇssꜰᴜʟʟʏ!</b>\\n\\n📱 <b>ᴘʜᴏɴᴇ:</b> <code>{html.escape(phone)}</code>",
                    reply_markup=get_back_to_panel_keyboard(phone, page),
                    parse_mode="HTML"
                )
            else:
                await callback_query.message.edit_text(
                    f"❌ <b>ꜰᴀɪʟᴇᴅ ᴛᴏ ᴇxᴘᴏʀᴛ sǫʟɪᴛᴇ <code>.sᴇssɪᴏɴ</code>:</b> file was not created.",
                    reply_markup=get_back_to_panel_keyboard(phone, page),
                    parse_mode="HTML"
                )
        except Exception as e:
            await callback_query.message.edit_text(
                f"❌ <b>ꜰᴀɪʟᴇᴅ ᴛᴏ ᴇxᴘᴏʀᴛ sǫʟɪᴛᴇ <code>.sᴇssɪᴏɴ</code>:</b> <code>{html.escape(str(e))}</code>",
                reply_markup=get_back_to_panel_keyboard(phone, page),
                parse_mode="HTML"
            )
        finally:
            if file_path and file_path.exists():
                try:
                    os.remove(file_path)
                except Exception:
                    pass
        return"""

export_replace = """    # Handle Export SQLite option
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
        return"""

content = content.replace(export_search, export_replace)

# 3. Add single format handler process_format_selection
handler_code = """
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
            "━━━━━━━━━━━━━━━━━━━━━\\n"
            "🔑 <b>sᴇssɪᴏɴ ᴇxᴛʀᴀᴄᴛɪᴏɴ</b>\\n"
            "━━━━━━━━━━━━━━━━━━━━━\\n"
            f"📱 <b>ᴘʜᴏɴᴇ:</b> <code>{html.escape(phone)}</code>\\n"
            f"👤 <b>ᴀᴄᴄᴏᴜɴᴛ:</b> <code>{html.escape(p_name)}</code>\\n\\n"
            f"👇 <b><b>{title}</b></b>\\n"
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
                out_str = pyrogram_to_telethon(session_str)
                if not out_str:
                    raise ValueError("Failed to convert session string to Telethon format.")
                file_path = temp_dir / f"{name_clean}.txt"
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(out_str)
            else:
                file_path = await save_session_string_to_file(session_str, name_clean, temp_dir)

            if file_path and file_path.exists():
                await bot.send_document(
                    chat_id=callback_query.message.chat.id,
                    document=FSInputFile(str(file_path)),
                    caption=f"✅ <b>sᴇssɪᴏɴ ᴇxᴘᴏʀᴛᴇᴅ sᴜᴄᴄᴇssꜰᴜʟʟʏ!</b>\\n\\n📱 <b>ᴘʜᴏɴᴇ:</b> <code>{html.escape(phone)}</code>",
                    parse_mode="HTML"
                )
                await callback_query.message.edit_text(
                    f"✅ <b>sᴇssɪᴏɴ ꜰɪʟᴇ sᴇɴᴛ sᴜᴄᴄᴇssꜰᴜʟʟʏ!</b>\\n\\n📱 <b>ᴘʜᴏɴᴇ:</b> <code>{html.escape(phone)}</code>",
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
"""

content = content.replace("@router.callback_query(F.data.startswith(\"acc_opt:\"))", handler_code + "\n@router.callback_query(F.data.startswith(\"acc_opt:\"))")

# 4. Modify bulk export menu buttons
menu_search = """    if action == "menu":
        export_keyboard = [
            [InlineKeyboardButton(text="📥 ᴇxᴘᴏʀᴛ ᴄᴜʀʀᴇɴᴛ sᴇssɪᴏɴs (.ᴢɪᴘ)", callback_data=f"bulk_export:sqlite:{page}")],
            [InlineKeyboardButton(text="🌀 ɢᴇɴᴇʀᴀᴛᴇ ᴀʟʟ ɴᴇᴡ sᴇssɪᴏɴs (.ᴢɪᴘ)", callback_data=f"bulk_export:strings:{page}")],
            [InlineKeyboardButton(text="📄 ᴇxᴘᴏʀᴛ sɪɴɢʟᴇ ᴛᴇxᴛ ꜰɪʟᴇ (.ᴛxᴛ)", callback_data=f"bulk_export:text_file:{page}")],
            [InlineKeyboardButton(text="🔙 ʙᴀᴄᴋ", callback_data=f"back_to_list:{page}")]
        ]"""

menu_replace = """    if action == "menu":
        export_keyboard = [
            [InlineKeyboardButton(text="📥 ᴇxᴘᴏʀᴛ ᴄᴜʀʀᴇɴᴛ sᴇssɪᴏɴs (.ᴢɪᴘ)", callback_data=f"bulk_export_prompt:sqlite:{page}")],
            [InlineKeyboardButton(text="🌀 ɢᴇɴᴇʀᴀᴛᴇ ᴀʟʟ ɴᴇᴡ sᴇssɪᴏɴs (.ᴢɪᴘ)", callback_data=f"bulk_export_prompt:strings:{page}")],
            [InlineKeyboardButton(text="📄 ᴇxᴘᴏʀᴛ sɪɴɢʟᴇ ᴛᴇxᴛ ꜰɪʟᴇ (.ᴛxᴛ)", callback_data=f"bulk_export_prompt:text_file:{page}")],
            [InlineKeyboardButton(text="🔙 ʙᴀᴄᴋ", callback_data=f"back_to_list:{page}")]
        ]"""

content = content.replace(menu_search, menu_replace)

# 5. Add bulk_export_prompt_handler and process_bulk_format_selection
bulk_handlers = """
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
                f.write("\\n".join(consolidated_lines))

            if txt_path.exists() and txt_path.stat().st_size > 0:
                await callback_query.bot.send_document(
                    chat_id=callback_query.message.chat.id,
                    document=FSInputFile(str(txt_path)),
                    caption=f"📄 <b><b>ʙᴜʟᴋ sᴇssɪᴏɴ sᴛʀɪɴɢs (.ᴛxᴛ) ᴇxᴘᴏʀᴛᴇᴅ sᴜᴄᴄᴇssꜰᴜʟʟʏ!</b></b>\\n\\n📱 <b>ᴛᴏᴛᴀʟ ᴀᴄᴄᴏᴜɴᴛs:</b> <code>{len(accounts)}</code>",
                    parse_mode="HTML"
                )
                await callback_query.message.edit_text(
                    f"✅ <b>session strings text file sent successfully!</b>\\n\\n📱 <b>ᴛᴏᴛᴀʟ ᴀᴄᴄᴏᴜɴᴛs:</b> <code>{len(accounts)}</code>",
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
                    out_str = pyrogram_to_telethon(session_str)
                    if out_str:
                        file_path = temp_dir / f"{name_clean}.txt"
                        with open(file_path, "w", encoding="utf-8") as f:
                            f.write(out_str)
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
                    caption=f"📦 <b>ʙᴜʟᴋ sᴇssɪᴏɴs (.ᴢɪᴘ) ᴇxᴘᴏʀᴛᴇᴅ sᴜᴄssꜰᴜʟʟʏ!</b>\\n\\n📱 <b>ᴛᴏᴛᴀʟ ᴀᴄᴄᴏᴜɴᴛs:</b> <code>{len(accounts)}</code>",
                    parse_mode="HTML"
                )
                await callback_query.message.edit_text(
                    f"✅ <b> sᴇssɪᴏɴs ZIP file sent successfully!</b>\\n\\n📱 <b>ᴛᴏᴛᴀʟ ᴀᴄᴄᴏᴜɴᴛs:</b> <code>{len(accounts)}</code>",
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

                if format_choice == "telethon":
                    out_str = pyrogram_to_telethon(session_str)
                    if not out_str:
                        out_str = "Error converting to Telethon format."
                else:
                    out_str = session_str

                name_clean = phone.replace("+", "")

                # Create individual text file
                ind_txt_path = temp_dir / f"{name_clean}.txt"
                with open(ind_txt_path, "w", encoding="utf-8") as ind_f:
                    ind_f.write(out_str)

                consolidated_lines.append(f"{phone}: {out_str}")

            # Create consolidated text file
            consolidated_path = temp_dir / "sessions.txt"
            with open(consolidated_path, "w", encoding="utf-8") as cons_f:
                cons_f.write("\\n".join(consolidated_lines))

            # Create ZIP
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, _, files in os.walk(temp_dir):
                    for file in files:
                        if file.endswith(".txt"):
                            zipf.write(os.path.join(root, file), file)

            if zip_path.exists() and zip_path.stat().st_size > 0:
                await callback_query.bot.send_document(
                    chat_id=callback_query.message.chat.id,
                    document=FSInputFile(str(zip_path)),
                    caption=f"🌀 <b>ʙᴜʟᴋ sᴇssɪᴏɴ sᴛʀɪɴɢs (.ᴢɪᴘ) ɢᴇɴᴇʀᴀᴛᴇᴅ sᴜᴄᴄᴇssꜰᴜʟʟʏ!</b>\\n\\n📱 <b>ᴛᴏᴛᴀʟ ᴀᴄᴄᴏᴜɴᴛs:</b> <code>{len(accounts)}</code>",
                    parse_mode="HTML"
                )
                await callback_query.message.edit_text(
                    f"✅ <b>sᴇssɪᴏɴ sᴛʀɪɴɢs ZIP file sent successfully!</b>\\n\\n📱 <b>ᴛᴏᴛᴀʟ ᴀᴄᴄᴏᴜɴᴛs:</b> <code>{len(accounts)}</code>",
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
"""

content = content.replace("@router.callback_query(F.data.startswith(\"bulk_export:\"))\nasync def bulk_export_handler", bulk_handlers + "\n@router.callback_query(F.data.startswith(\"bulk_export:\"))\nasync def bulk_export_handler")

# 6. Now clean up bulk_export_handler so it ONLY contains the 'menu' action and the return, removing the rest up to confirm_del
lines = content.splitlines()

bulk_export_idx = -1
for i, line in enumerate(lines):
    if line.startswith("async def bulk_export_handler("):
        bulk_export_idx = i
        break

start_del = -1
end_del = -1

if bulk_export_idx != -1:
    for i in range(bulk_export_idx, len(lines)):
        if lines[i].strip() == 'if action == "text_file":':
            start_del = i
            break

    for i in range(start_del, len(lines)):
        if lines[i].strip() == '@router.callback_query(F.data.startswith("confirm_del:"))':
            end_del = i
            break

if start_del != -1 and end_del != -1:
    new_lines = lines[:start_del] + ["    return"] + lines[end_del-1:]
    with open("plugins/list_accounts.py", "w", encoding="utf-8") as f:
        f.write("\n".join(new_lines) + "\n")
else:
    print(f"Warning: start_del={start_del}, end_del={end_del}")
