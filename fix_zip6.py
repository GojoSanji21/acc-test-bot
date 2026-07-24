with open("plugins/add_account.py", "r") as f:
    content = f.read()

search_block = """
                    # Deduplicate sessions_to_import based on session data
                    unique_sessions = []
                    seen_strings = set()
                    for s_type, s_data, s_name, s_workdir in sessions_to_import:
                        if s_data not in seen_strings:
                            seen_strings.add(s_data)
                            unique_sessions.append((s_type, s_data, s_name, s_workdir))
"""

replace_block = """
                    # Deduplicate sessions_to_import based on session data
                    unique_sessions = []
                    seen_strings = set()
                    for s_type, s_data, s_name, s_workdir in sessions_to_import:
                        # For files, deduplicate by the full path (s_workdir + s_data)
                        # For strings, deduplicate by the string itself
                        dedup_key = f"{s_workdir}/{s_data}" if s_type == "file" else s_data
                        if dedup_key not in seen_strings:
                            seen_strings.add(dedup_key)
                            unique_sessions.append((s_type, s_data, s_name, s_workdir))
"""

content = content.replace(search_block.strip('\n'), replace_block.strip('\n'))

with open("plugins/add_account.py", "w") as f:
    f.write(content)

print("done")
