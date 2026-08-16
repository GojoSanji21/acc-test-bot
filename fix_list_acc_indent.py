import re
with open('plugins/list_accounts.py', 'r') as f:
    content = f.read()

search = """# Pyrogram exceptions

    AuthKeyInvalid,
    RPCError
)"""

replace = """# Pyrogram exceptions
from pyrogram.errors import (
    AuthKeyInvalid,
    RPCError,
    FloodWait, ChatAdminRequired, UserDeactivated, UsernameOccupied, UsernameInvalid, FreshResetAuthorisationForbidden
)"""

content = content.replace(search, replace)
with open('plugins/list_accounts.py', 'w') as f:
    f.write(content)
