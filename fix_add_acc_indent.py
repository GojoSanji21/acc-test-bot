import re
with open('plugins/add_account.py', 'r') as f:
    content = f.read()

# I messed up the imports in add_account.py because it had a multi-line import
search = """# Pyrogram exceptions

    SessionPasswordNeeded,
    PhoneCodeInvalid,
    PhoneCodeExpired,
    PasswordHashInvalid,
    AuthKeyInvalid
)"""

replace = """# Pyrogram exceptions
from pyrogram.errors import (
    SessionPasswordNeeded,
    PhoneCodeInvalid,
    PhoneCodeExpired,
    PasswordHashInvalid,
    AuthKeyInvalid,
    RPCError, FloodWait, ChatAdminRequired, UserDeactivated, UsernameOccupied, UsernameInvalid
)"""

content = content.replace(search, replace)
with open('plugins/add_account.py', 'w') as f:
    f.write(content)
