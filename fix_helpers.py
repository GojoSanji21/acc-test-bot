with open("helpers/__init__.py", "r") as f:
    content = f.read()

search_block = """
from .session import (
    get_random_proxy,
    create_pyrogram_client
)
"""

replace_block = """
from .session import (
    get_random_proxy,
    create_pyrogram_client,
    normalize_session_string
)
"""

content = content.replace(search_block.strip('\n'), replace_block.strip('\n'))

with open("helpers/__init__.py", "w") as f:
    f.write(content)

print("done")
