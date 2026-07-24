import re

with open("plugins/add_account.py", "r") as f:
    content = f.read()

search_block = """
            elif file_name.lower().endswith(".session"):
                status_msg = await message.answer("⚙️ ᴘᴀʀsɪɴɢ sǫʟɪᴛᴇ <code>.session</code> ꜰɪʟᴇ...", parse_mode="HTML")
                try:
                    # In order to read .session SQLite database, we can open it with FileStorage and export with MemoryStorage
                    # Session name must match the filename without extension
                    session_db_name = dest_path.stem
                    file_storage = FileStorage(session_db_name, temp_dir)
                    await file_storage.open()

                    dc_id = await file_storage.dc_id()
                    api_id = await file_storage.api_id()
                    test_mode = await file_storage.test_mode()
                    auth_key = await file_storage.auth_key()
                    user_id = await file_storage.user_id()
                    is_bot = await file_storage.is_bot()
                    date = await file_storage.date()

                    await file_storage.close()

                    mem_storage = MemoryStorage(session_db_name)
                    await mem_storage.open()
                    await mem_storage.dc_id(dc_id)
                    await mem_storage.api_id(api_id)
                    await mem_storage.test_mode(test_mode)
                    await mem_storage.auth_key(auth_key)
                    await mem_storage.user_id(user_id)
                    await mem_storage.is_bot(is_bot)
                    await mem_storage.date(date)

                    session_str = await mem_storage.export_session_string()
                    await mem_storage.close()
                    await status_msg.delete()
                except Exception as db_err:
                    logger.error(f"Failed to parse SQLite session file {dest_path.name}: {db_err}. Falling back to direct SQLite query...")

                    # Direct SQLite query fallback (supports both Pyrogram & Telethon schemas)
                    recovered_via_sql = False
                    try:
                        import sqlite3
                        import struct
                        import base64
                        conn = sqlite3.connect(str(dest_path))
                        cursor = conn.cursor()

                        # Get all tables
                        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                        tables = [row[0] for row in cursor.fetchall()]

                        for table in ["sessions", "session"]:
                            if table in tables:
                                cursor.execute(f"PRAGMA table_info({table})")
                                columns = [col[1] for col in cursor.fetchall()]
                                if "dc_id" in columns and "auth_key" in columns:
                                    cursor.execute(f"SELECT dc_id, auth_key FROM {table} LIMIT 1")
                                    row = cursor.fetchone()
                                    if row:
                                        dc_id, auth_key = row
                                        if auth_key and len(auth_key) == 256:
                                            # Pack into standard Pyrogram session string format: '>BI?256sQ?'
                                            packed = struct.pack(
                                                '>BI?256sQ?',
                                                dc_id,
                                                0,      # api_id
                                                False,  # test_mode
                                                auth_key,
                                                0,      # user_id
                                                False   # is_bot
                                            )
                                            session_str = base64.urlsafe_b64encode(packed).decode().rstrip("=")
                                            recovered_via_sql = True
                                            break
                        conn.close()
                    except Exception as sql_fallback_err:
                        logger.error(f"Direct SQLite query fallback failed for single upload: {sql_fallback_err}")

                    if recovered_via_sql:
                        await status_msg.delete()
                    else:
                        await message.answer(
                            f"❌ <b>ꜰᴀɪʟᴇᴅ ᴛᴏ ᴘᴀʀsɪɴɢ sǫʟɪᴛᴇ sᴇssɪᴏɴ:</b> <code>{html.escape(str(db_err))}</code>",
                            parse_mode="HTML",
                            reply_markup=get_back_keyboard()
                        )
                        return
"""

replace_block = """
            elif file_name.lower().endswith(".session"):
                status_msg = await message.answer("⚙️ ᴘᴀʀsɪɴɢ sǫʟɪᴛᴇ <code>.session</code> ꜰɪʟᴇ...", parse_mode="HTML")
                try:
                    # In order to read .session SQLite database directly
                    # Session name must match the filename without extension
                    session_db_name = dest_path.stem

                    proxy, proxy_error = get_random_proxy()

                    client = Client(
                        name=session_db_name,
                        api_id=API_ID,
                        api_hash=API_HASH,
                        workdir=str(temp_dir),
                        proxy=proxy
                    )

                    await client.connect()
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
                    session_str = await client.export_session_string()

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
                            f"✅ <b>ᴀᴄᴄᴏᴜɴᴛ ᴀᴅᴅᴇᴅ sᴜᴄᴄᴇssꜰᴜʟʟʏ ᴠɪᴀ ᴜᴘʟᴏᴀᴅ!</b>\\n\\n"
                            f"👤 <b>ɴᴀᴍᴇ:</b> <code>{html.escape(profile_name)}</code>\\n"
                            f"📱 <b>ᴘʜᴏɴᴇ:</b> <code>{html.escape(phone)}</code>\\n"
                            f"🔒 <b>sᴇssɪᴏɴ sᴛʀɪɴɢ:</b> ᴇɴᴄʀʏᴘᴛᴇᴅ &amp; sᴀᴠᴇᴅ sᴇᴄᴜʀᴇʟʏ.\\n"
                            f"🌐 <b>ʙᴏᴜɴᴅ ᴘʀᴏxʏ:</b> {proxy_info}\\n\\n"
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
"""

content = content.replace(search_block.replace("\\n", "\n").strip('\n'), replace_block.replace("\\n", "\n").strip('\n'))

with open("plugins/add_account.py", "w") as f:
    f.write(content)

print("done")
