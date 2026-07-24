import re

with open("plugins/add_account.py", "r") as f:
    content = f.read()

# Replace the block from 226 to 334

search_block = """
                            if p.suffix.lower() == ".session":
                                # It's a SQLite session file!
                                try:
                                    session_db_name = p.stem
                                    file_storage = FileStorage(session_db_name, p.parent)
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

                                    temp_session_str = await mem_storage.export_session_string()
                                    await mem_storage.close()

                                    if temp_session_str:
                                        sessions_to_import.append((temp_session_str, p.name))
                                except Exception as db_err:
                                    logger.error(f"Failed to parse SQLite session file {p.name} from ZIP: {db_err}. Falling back to direct SQLite query...")
                                    parsing_errors.append(f"{p.name} (SQLite err: {str(db_err)[:40]})")

                                    # Fallback 1: Direct SQLite query for dc_id and auth_key (supports Pyrogram & Telethon schemas)
                                    recovered_via_sql = False
                                    try:
                                        import sqlite3
                                        import struct
                                        import base64
                                        conn = sqlite3.connect(str(p))
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
                                                            temp_session_str = base64.urlsafe_b64encode(packed).decode().rstrip("=")
                                                            sessions_to_import.append((temp_session_str, p.name))
                                                            parsing_errors.append(f"{p.name} (recovered via direct SQL fallback!)")
                                                            recovered_via_sql = True
                                                            break
                                        conn.close()
                                    except Exception as sql_fallback_err:
                                        logger.error(f"Direct SQLite query fallback failed for {p.name}: {sql_fallback_err}")

                                    if not recovered_via_sql:
                                        # Fallback 2: try to read as a text file
                                        try:
                                            with open(p, "r", encoding="utf-8", errors="ignore") as f:
                                                content = f.read()
                                            found_strings = re.findall(r"[a-zA-Z0-9+\-_=/]{100,}", content)
                                            if found_strings:
                                                for s in found_strings:
                                                    sessions_to_import.append((s, p.name))
                                                parsing_errors.append(f"{p.name} (recovered via text fallback!)")
                                            else:
                                                parsing_errors.append(f"{p.name} (no session found in fallback)")
                                        except Exception as fallback_err:
                                            logger.error(f"Fallback text parsing failed for {p.name}: {fallback_err}")
                                            parsing_errors.append(f"{p.name} (fallback err: {str(fallback_err)[:40]})")
                            else:
                                # Treat any non-.session file as a text candidate to find potential session strings
                                try:
                                    with open(p, "r", encoding="utf-8", errors="ignore") as f:
                                        content = f.read()

                                    # Use a regex to find all potential base64 strings of length >= 100 including standard and url-safe characters
                                    found_strings = re.findall(r"[a-zA-Z0-9+\-_=/]{100,}", content)
                                    if found_strings:
                                        for s in found_strings:
                                            sessions_to_import.append((s, p.name))
                                    else:
                                        parsing_errors.append(f"{p.name} (no session string found)")
                                except Exception as txt_err:
                                    logger.error(f"Failed to read text file {p.name} from ZIP: {txt_err}")
                                    parsing_errors.append(f"{p.name} (read err: {str(txt_err)[:40]})")
"""

replace_block = """
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
"""

content = content.replace(search_block.strip('\n'), replace_block.strip('\n'))

with open("plugins/add_account.py", "w") as f:
    f.write(content)

print("done")
