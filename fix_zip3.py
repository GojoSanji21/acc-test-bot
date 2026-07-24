with open("plugins/add_account.py", "r") as f:
    content = f.read()

search_block = """
                    for i, (session_str_item, source_name) in enumerate(unique_sessions, 1):
                        session_str_item = normalize_session_string(session_str_item)
                        # Throttle live updates to prevent hitting Telegram API rate limits (flood waits)
                        now_time = time.time()
                        if i == 1 or i == total_sessions or (now_time - last_edit_time >= 1.5):
                            progress_text = (
                                f"⏳ <b>ʙᴜʟᴋ ɪᴍᴘᴏʀᴛ ɪɴ ᴘʀᴏɢʀᴇss...</b>\\n\\n"
                                f"📈 <b>ᴘʀᴏɢʀᴇss:</b> {make_progress_bar(i - 1, total_sessions)} (<code>{i - 1} / {total_sessions}</code>)\\n"
                                f"━━━━━━━━━━━━━━━━━━━━━\\n"
                                f"✅ <b>sᴜᴄᴄᴇss:</b> <code>{success_count}</code>\\n"
                                f"🔴 <b>ᴇxᴘɪʀᴇᴅ:</b> <code>{len(expired_sessions)}</code>\\n"
                                f"⚠️ <b>ꜰᴀɪʟᴇᴅ:</b> <code>{len(other_failed_sessions)}</code>\\n"
                                f"⏳ <b>ᴘᴇɴᴅɪɴɢ:</b> <code>{total_sessions - (i - 1)}</code>\\n\\n"
                                f"⚡ <i>Processing: {html.escape(source_name)}...</i>"
                            )
                            try:
                                await status_msg.edit_text(progress_text, parse_mode="HTML")
                                last_edit_time = now_time
                            except Exception as edit_err:
                                logger.warning(f"Failed to edit progress status: {edit_err}")

                        proxy, proxy_error = get_random_proxy()
                        temp_name = f"uploaded_sess_zip_{message.from_user.id}_{i}"
                        client = create_pyrogram_client(session_name=temp_name, session_string=session_str_item, proxy=proxy)

                        try:
                            await client.connect()
                            me = await client.get_me()

                            if not me:
                                raise ValueError("Could not retrieve account identity from get_me()")

                            phone = getattr(me, "phone_number", None)
                            if not phone:
                                phone = f"+{me.id}"
                            else:
                                if not phone.startswith("+"):
                                    phone = f"+{phone}"

                            profile_name = "ᴜɴᴋɴᴏᴡɴ"
                            first = me.first_name or ""
                            last = me.last_name or ""
                            name_parts = [first, last]
                            profile_name = " ".join([p for p in name_parts if p.strip()]) or me.username or "ᴜɴᴋɴᴏᴡɴ"

                            # Encrypt and save securely
                            encrypted_session = encrypt_data(session_str_item)
                            await client.disconnect()
"""

replace_block = """
                    for i, (s_type, s_data, source_name, s_workdir) in enumerate(unique_sessions, 1):
                        # Throttle live updates to prevent hitting Telegram API rate limits (flood waits)
                        now_time = time.time()
                        if i == 1 or i == total_sessions or (now_time - last_edit_time >= 1.5):
                            progress_text = (
                                f"⏳ <b>ʙᴜʟᴋ ɪᴍᴘᴏʀᴛ ɪɴ ᴘʀᴏɢʀᴇss...</b>\\n\\n"
                                f"📈 <b>ᴘʀᴏɢʀᴇss:</b> {make_progress_bar(i - 1, total_sessions)} (<code>{i - 1} / {total_sessions}</code>)\\n"
                                f"━━━━━━━━━━━━━━━━━━━━━\\n"
                                f"✅ <b>sᴜᴄᴄᴇss:</b> <code>{success_count}</code>\\n"
                                f"🔴 <b>ᴇxᴘɪʀᴇᴅ:</b> <code>{len(expired_sessions)}</code>\\n"
                                f"⚠️ <b>ꜰᴀɪʟᴇᴅ:</b> <code>{len(other_failed_sessions)}</code>\\n"
                                f"⏳ <b>ᴘᴇɴᴅɪɴɢ:</b> <code>{total_sessions - (i - 1)}</code>\\n\\n"
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
                            # For physical files, initialize client directly with workdir
                            client = Client(
                                name=s_data,
                                api_id=API_ID,
                                api_hash=API_HASH,
                                workdir=s_workdir,
                                proxy=proxy
                            )
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
"""

# Need to escape backslashes correctly for replace
content = content.replace(search_block.replace("\\n", "\n").strip('\n'), replace_block.replace("\\n", "\n").strip('\n'))

with open("plugins/add_account.py", "w") as f:
    f.write(content)

print("done")
