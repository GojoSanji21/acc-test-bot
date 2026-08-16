import re
with open('plugins/list_accounts.py', 'r') as f:
    content = f.read()

# Fix create_pyrogram_client calls in list_accounts.py to use kwarg session_string properly
def replace_create_client(match):
    name = match.group(1).strip()
    session_str = match.group(2).strip()
    proxy = match.group(3).strip()
    custom_api = match.group(4).strip()
    return f"client = create_pyrogram_client(session_name={name}, session_string={session_str}, proxy={proxy}, custom_api={custom_api})"

content = re.sub(r'client\s*=\s*create_pyrogram_client\((f"[^"]+"),\s*([^,]+),\s*([^,]+),\s*([^)]+)\)', replace_create_client, content)

with open('plugins/list_accounts.py', 'w') as f:
    f.write(content)
