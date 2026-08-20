import os
import re

for file in os.listdir('plugins'):
    if file.endswith('.py'):
        path = os.path.join('plugins', file)
        with open(path, 'r') as f:
            content = f.read()

        # Replace client.disconnect() with client.stop()
        content = content.replace('client.disconnect()', 'client.stop()')
        content = content.replace('client.connect()', 'client.start()')
        content = content.replace('client.is_connected', 'client.is_connected') # is_connected is still valid for pyrogram Client

        with open(path, 'w') as f:
            f.write(content)

print("done replacing disconnect/connect with stop/start")
