import re

with open("plugins/add_account.py", "r") as f:
    content = f.read()

search_block = """
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

                            saved = await save_account(
"""

replace_block = """
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

                            saved = await save_account(
"""

content = content.replace(search_block.strip('\n'), replace_block.strip('\n'))

with open("plugins/add_account.py", "w") as f:
    f.write(content)

print("done")
