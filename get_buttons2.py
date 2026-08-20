import os
import re

for file in os.listdir('plugins'):
    if file.endswith('.py'):
        path = os.path.join('plugins', file)
        with open(path, 'r') as f:
            content = f.read()
            # Let's fix small caps inline buttons for start.py
            if file == 'start.py':
                content = content.replace("✅ Yes, Delete All", "✅ ʏᴇs, ᴅᴇʟᴇᴛᴇ ᴀʟʟ")
                content = content.replace("❌ Cancel", "❌ ᴄᴀɴᴄᴇʟ")

            with open(path, 'w') as f2:
                f2.write(content)

print("done")
