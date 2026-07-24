with open("plugins/add_account.py", "r") as f:
    content = f.read()

search_block = """
                    for i, (session_str_item, source_name) in enumerate(unique_sessions, 1):
                        session_str_item = normalize_session_string(session_str_item)
"""

replace_block = """
                    for i, (s_type, s_data, source_name, s_workdir) in enumerate(unique_sessions, 1):
"""

content = content.replace(search_block.strip('\n'), replace_block.strip('\n'))

with open("plugins/add_account.py", "w") as f:
    f.write(content)

print("done")
