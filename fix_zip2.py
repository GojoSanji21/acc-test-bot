import re

with open("plugins/add_account.py", "r") as f:
    content = f.read()

search_block = """
                    # Deduplicate sessions_to_import based on session_string
                    unique_sessions = []
                    seen_strings = set()
                    for s_str, s_name in sessions_to_import:
                        if s_str not in seen_strings:
                            seen_strings.add(s_str)
                            unique_sessions.append((s_str, s_name))
"""

replace_block = """
                    # Deduplicate sessions_to_import based on session data
                    unique_sessions = []
                    seen_strings = set()
                    for s_type, s_data, s_name, s_workdir in sessions_to_import:
                        if s_data not in seen_strings:
                            seen_strings.add(s_data)
                            unique_sessions.append((s_type, s_data, s_name, s_workdir))
"""

content = content.replace(search_block.strip('\n'), replace_block.strip('\n'))

with open("plugins/add_account.py", "w") as f:
    f.write(content)

print("done")
